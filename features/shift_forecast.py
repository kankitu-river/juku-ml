"""シフト予測 (B-4)

過去12週の出勤実績から曜日×スロットの出勤確率をベータ分布でスムージングして返す。
頻度 >= 0.6 を「出勤見込み」とする。
"""
from __future__ import annotations
from pydantic import BaseModel


class ShiftRecord(BaseModel):
    day: int    # 0=日〜6=土
    slot: int   # 1〜7


class TeacherHistory(BaseModel):
    teacher_id: str
    weeks: int                # 集計対象の週数
    records: list[ShiftRecord]  # 実際に出勤した曜日×スロットの全レコード（重複あり）


class ShiftRequest(BaseModel):
    teachers: list[TeacherHistory]


class LikelySlot(BaseModel):
    day: int
    slot: int
    probability: float


class TeacherForecast(BaseModel):
    teacher_id: str
    likely_slots: list[LikelySlot]


class ShiftResponse(BaseModel):
    forecasts: list[TeacherForecast]


def forecast(payload: ShiftRequest) -> ShiftResponse:
    result: list[TeacherForecast] = []

    for teacher in payload.teachers:
        n_weeks = max(teacher.weeks, 1)
        count: dict[tuple[int, int], int] = {}
        for r in teacher.records:
            key = (r.day, r.slot)
            count[key] = count.get(key, 0) + 1

        likely: list[LikelySlot] = []
        for (day, slot), c in count.items():
            # ベータ分布の平均: (出勤回数+1) / (週数+2)
            prob = (c + 1) / (n_weeks + 2)
            if prob >= 0.6:
                likely.append(LikelySlot(day=day, slot=slot, probability=round(prob, 3)))

        likely.sort(key=lambda x: (x.day, x.slot))
        result.append(TeacherForecast(teacher_id=teacher.teacher_id, likely_slots=likely))

    return ShiftResponse(forecasts=result)
