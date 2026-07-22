from features.intensive_opt import optimize, IntensiveRequest, StudentRequest, SlotOption


def _make_slot(slot_id: str, subject: str, enrollment: int = 0, capacity: int = 2) -> SlotOption:
    return SlotOption(
        slot_id=slot_id,
        teacher_id="teacher-1",
        subject=subject,
        day=1,
        slot_index=1,
        current_enrollment=enrollment,
        capacity=capacity,
    )


def _make_student(student_id: str, subject: str, desired: int, available: list[str]) -> StudentRequest:
    return StudentRequest(
        student_id=student_id,
        subject=subject,
        desired_slots=desired,
        available_slot_ids=available,
    )


def test_empty_input():
    res = optimize(IntensiveRequest(students=[], slots=[]))
    assert res.assignments == []
    assert res.unassigned == []


def test_basic_assignment():
    """空きスロットに生徒1人が割り当てられる"""
    res = optimize(IntensiveRequest(
        students=[_make_student("s1", "数学", 1, ["slot-a"])],
        slots=[_make_slot("slot-a", "数学")],
    ))
    assert len(res.assignments) == 1
    assert res.assignments[0].student_id == "s1"
    assert res.assignments[0].slot_id == "slot-a"
    assert res.unassigned == []


def test_subject_mismatch_is_unassigned():
    """科目が合わないスロットには割り当てない"""
    res = optimize(IntensiveRequest(
        students=[_make_student("s1", "数学", 1, ["slot-a"])],
        slots=[_make_slot("slot-a", "英語")],
    ))
    assert res.assignments == []
    assert "s1" in res.unassigned


def test_availability_mismatch_is_unassigned():
    """希望日程外のスロットには割り当てない"""
    res = optimize(IntensiveRequest(
        students=[_make_student("s1", "数学", 1, [])],  # 空の希望
        slots=[_make_slot("slot-a", "数学")],
    ))
    assert res.assignments == []
    assert "s1" in res.unassigned


def test_full_slot_is_skipped():
    """定員満のスロットには割り当てない"""
    res = optimize(IntensiveRequest(
        students=[_make_student("s1", "数学", 1, ["slot-a"])],
        slots=[_make_slot("slot-a", "数学", enrollment=2, capacity=2)],
    ))
    assert res.assignments == []
    assert "s1" in res.unassigned


def test_multiple_students_multiple_slots():
    """複数生徒を複数スロットに最適割り当て"""
    students = [
        _make_student("s1", "数学", 1, ["slot-a", "slot-b"]),
        _make_student("s2", "数学", 1, ["slot-a", "slot-b"]),
    ]
    slots = [
        _make_slot("slot-a", "数学", capacity=1),
        _make_slot("slot-b", "数学", capacity=1),
    ]
    res = optimize(IntensiveRequest(students=students, slots=slots))
    assert len(res.assignments) == 2
    assert res.unassigned == []
    # 同じスロットに2人が入っていないことを確認
    assigned_slots = [a.slot_id for a in res.assignments]
    assert len(set(assigned_slots)) == 2


def test_desired_slots_multi():
    """desired_slots=2 の生徒に2つのスロットを割り当てる"""
    res = optimize(IntensiveRequest(
        students=[_make_student("s1", "数学", 2, ["slot-a", "slot-b"])],
        slots=[
            _make_slot("slot-a", "数学", capacity=1),
            _make_slot("slot-b", "数学", capacity=1),
        ],
    ))
    assert len(res.assignments) == 2
    assert all(a.student_id == "s1" for a in res.assignments)
    assert res.unassigned == []


def test_same_slot_not_assigned_twice():
    """同じスロットに同一生徒を2回割り当てない"""
    res = optimize(IntensiveRequest(
        students=[_make_student("s1", "数学", 2, ["slot-a"])],
        slots=[_make_slot("slot-a", "数学", capacity=2)],
    ))
    # slot-aに入れるのは1回だけ（同じスロットへの重複を防ぐ）
    s1_assignments = [a for a in res.assignments if a.student_id == "s1"]
    slot_ids = [a.slot_id for a in s1_assignments]
    assert len(set(slot_ids)) == len(slot_ids)
