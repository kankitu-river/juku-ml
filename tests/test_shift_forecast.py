import pytest
from features.shift_forecast import ShiftRequest, TeacherHistory, ShiftRecord, forecast


def test_forecast_basic():
    """毎週同じスロットに出勤した講師は高確率で予測される"""
    req = ShiftRequest(teachers=[
        TeacherHistory(
            teacher_id="t1",
            weeks=10,
            records=[ShiftRecord(day=1, slot=1)] * 10,  # 月曜1コマ、10週連続
        )
    ])
    res = forecast(req)
    assert len(res.forecasts) == 1
    slots = res.forecasts[0].likely_slots
    assert any(s.day == 1 and s.slot == 1 for s in slots)
    prob = next(s.probability for s in slots if s.day == 1 and s.slot == 1)
    assert prob >= 0.6


def test_forecast_low_freq_excluded():
    """出勤頻度が低い（3/10週）スロットは likely_slots に含まれない"""
    req = ShiftRequest(teachers=[
        TeacherHistory(
            teacher_id="t2",
            weeks=10,
            records=[ShiftRecord(day=3, slot=2)] * 3,  # 水曜2コマ、3週のみ
        )
    ])
    res = forecast(req)
    slots = res.forecasts[0].likely_slots
    assert not any(s.day == 3 and s.slot == 2 for s in slots)


def test_forecast_empty_history():
    """出勤実績がない場合は likely_slots が空"""
    req = ShiftRequest(teachers=[
        TeacherHistory(teacher_id="t3", weeks=4, records=[])
    ])
    res = forecast(req)
    assert res.forecasts[0].likely_slots == []


def test_forecast_multiple_teachers():
    """複数講師のforecastが全員分返る"""
    req = ShiftRequest(teachers=[
        TeacherHistory(teacher_id="t1", weeks=4, records=[ShiftRecord(day=1, slot=1)] * 4),
        TeacherHistory(teacher_id="t2", weeks=4, records=[ShiftRecord(day=5, slot=3)] * 4),
    ])
    res = forecast(req)
    assert len(res.forecasts) == 2
    ids = {f.teacher_id for f in res.forecasts}
    assert ids == {"t1", "t2"}
