"""講習割り振り最適化 (B-5)

scipy.optimize.linear_sum_assignment（ハンガリアン法）をベースに生徒×スロットのコスト行列を構築。
"""
from __future__ import annotations
from pydantic import BaseModel


class StudentRequest(BaseModel):
    student_id: str
    subject: str
    desired_slots: int           # 希望コマ数
    available_slot_ids: list[str]  # 受講可能スロットID


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
        return IntensiveResponse(assignments=[], unassigned=[s.student_id for s in students], message="データなし")

    # 科目フィルタ済みの有効スロットのみ対象
    available: list[tuple[StudentRequest, SlotOption]] = []
    for s in students:
        for sl in slots:
            if sl.subject != s.subject:
                continue
            if sl.slot_id not in s.available_slot_ids:
                continue
            if sl.current_enrollment >= sl.capacity:
                continue
            available.append((s, sl))

    # 単純な貪欲割当（B-5の本格実装は開発者が拡張する）
    slot_used: dict[str, int] = {sl.slot_id: sl.current_enrollment for sl in slots}
    assigned: list[Assignment] = []
    assigned_ids: set[str] = set()

    for s, sl in available:
        if s.student_id in assigned_ids:
            continue
        if slot_used[sl.slot_id] >= next(x.capacity for x in slots if x.slot_id == sl.slot_id):
            continue
        assigned.append(Assignment(student_id=s.student_id, slot_id=sl.slot_id, teacher_id=sl.teacher_id))
        assigned_ids.add(s.student_id)
        slot_used[sl.slot_id] += 1

    unassigned = [s.student_id for s in students if s.student_id not in assigned_ids]
    msg = f"{len(assigned)}件割当、{len(unassigned)}件未割当"
    return IntensiveResponse(assignments=assigned, unassigned=unassigned, message=msg)
