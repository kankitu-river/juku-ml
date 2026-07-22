"""講習割り振り最適化 (B-5) - ハンガリアン法 (scipy) / 貪欲法フォールバック"""
from __future__ import annotations
from pydantic import BaseModel

try:
    import numpy as np
    from scipy.optimize import linear_sum_assignment
    HAS_SCIPY = True
except ImportError:  # pragma: no cover
    HAS_SCIPY = False

_INF = 1e9


class StudentRequest(BaseModel):
    student_id: str
    subject: str
    desired_slots: int           # 希望コマ数
    available_slot_ids: list[str]  # 受講可能スロットID（lesson_id）


class SlotOption(BaseModel):
    slot_id: str
    teacher_id: str
    subject: str
    day: int
    slot_index: int
    current_enrollment: int
    capacity: int


class IntensiveRequest(BaseModel):
    students: list[StudentRequest]
    slots: list[SlotOption]


class Assignment(BaseModel):
    student_id: str
    slot_id: str
    teacher_id: str


class IntensiveResponse(BaseModel):
    assignments: list[Assignment]
    unassigned: list[str]   # 割り当て不可だった student_id
    message: str


def optimize(payload: IntensiveRequest) -> IntensiveResponse:
    students = payload.students
    slots = payload.slots

    if not students or not slots:
        return IntensiveResponse(
            assignments=[],
            unassigned=[s.student_id for s in students],
            message="データなし",
        )

    # 空き席があるスロットだけ対象
    available_slots = [sl for sl in slots if sl.current_enrollment < sl.capacity]
    if not available_slots:
        return IntensiveResponse(
            assignments=[],
            unassigned=[s.student_id for s in students],
            message="空きスロットなし",
        )

    # 展開: 生徒は desired_slots 分だけ行を複製
    expanded_students: list[tuple[StudentRequest, int]] = []
    for s in students:
        for i in range(max(1, s.desired_slots)):
            expanded_students.append((s, i))

    # 展開: スロットは残り席数分だけ列を複製
    expanded_slots: list[SlotOption] = []
    for sl in available_slots:
        for _ in range(sl.capacity - sl.current_enrollment):
            expanded_slots.append(sl)

    if HAS_SCIPY:
        assignments = _hungarian(expanded_students, expanded_slots)
    else:
        assignments = _greedy(expanded_students, expanded_slots)

    assigned_ids = {a.student_id for a in assignments}
    unassigned = [s.student_id for s in students if s.student_id not in assigned_ids]
    algo = "ハンガリアン法" if HAS_SCIPY else "貪欲法"
    return IntensiveResponse(
        assignments=assignments,
        unassigned=unassigned,
        message=f"{len(assignments)}件割当（{algo}）、{len(unassigned)}件未割当",
    )


def _build_cost(
    expanded_students: list[tuple[StudentRequest, int]],
    expanded_slots: list[SlotOption],
) -> "np.ndarray":
    n_rows = len(expanded_students)
    n_cols = len(expanded_slots)
    dim = max(n_rows, n_cols)
    cost = np.full((n_rows, dim), _INF)
    for i, (s, _) in enumerate(expanded_students):
        avail = set(s.available_slot_ids)
        for j, sl in enumerate(expanded_slots):
            if sl.subject != s.subject:
                continue
            if sl.slot_id not in avail:
                continue
            # コスト: 負荷が高いほど高コスト（0〜1）
            load = sl.current_enrollment / max(sl.capacity, 1)
            cost[i][j] = load
    return cost


def _collect(
    row_ind: list[int],
    col_ind: list[int],
    expanded_students: list[tuple[StudentRequest, int]],
    expanded_slots: list[SlotOption],
    cost: "np.ndarray",
) -> list[Assignment]:
    n_cols = len(expanded_slots)
    student_slot_used: dict[str, set[str]] = {}
    result: list[Assignment] = []
    for i, j in zip(row_ind, col_ind):
        if j >= n_cols or cost[i][j] >= _INF:
            continue
        student, _ = expanded_students[i]
        slot = expanded_slots[j]
        sid = student.student_id
        used = student_slot_used.setdefault(sid, set())
        if slot.slot_id in used:
            continue  # 同一スロットへの重複割り当てを防止
        used.add(slot.slot_id)
        result.append(Assignment(student_id=sid, slot_id=slot.slot_id, teacher_id=slot.teacher_id))
    return result


def _hungarian(
    expanded_students: list[tuple[StudentRequest, int]],
    expanded_slots: list[SlotOption],
) -> list[Assignment]:
    cost = _build_cost(expanded_students, expanded_slots)
    row_ind, col_ind = linear_sum_assignment(cost)
    return _collect(list(row_ind), list(col_ind), expanded_students, expanded_slots, cost)


def _greedy(
    expanded_students: list[tuple[StudentRequest, int]],
    expanded_slots: list[SlotOption],
) -> list[Assignment]:
    cost = _build_cost(expanded_students, expanded_slots)
    n_rows, n_cols_orig = len(expanded_students), len(expanded_slots)
    used_cols: set[int] = set()
    row_ind, col_ind = [], []
    for i in range(n_rows):
        best_j, best_c = -1, _INF
        for j in range(n_cols_orig):
            if j not in used_cols and cost[i][j] < best_c:
                best_c = cost[i][j]
                best_j = j
        if best_j >= 0:
            row_ind.append(i)
            col_ind.append(best_j)
            used_cols.add(best_j)
    return _collect(row_ind, col_ind, expanded_students, expanded_slots, cost)
