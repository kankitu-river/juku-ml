"""振替候補スコアリング (B-3)"""
from __future__ import annotations
from pydantic import BaseModel
import numpy as np


class Candidate(BaseModel):
    candidate_id: str
    past_lessons: int    # 生徒×この講師の過去受講回数
    attendance_rate: float  # 生徒×この講師の出席率 (0〜1)
    teacher_load: int    # 講師の現在担当コマ数（負荷）


class MakeupRequest(BaseModel):
    student_id: str
    candidates: list[Candidate]


class RankedCandidate(BaseModel):
    candidate_id: str
    score: float
    reasons: list[str]


class MakeupResponse(BaseModel):
    ranked: list[RankedCandidate]


def score(payload: MakeupRequest) -> MakeupResponse:
    if not payload.candidates:
        return MakeupResponse(ranked=[])

    loads = [c.teacher_load for c in payload.candidates]
    max_load = max(loads) if loads else 1
    max_lessons = max(c.past_lessons for c in payload.candidates) if payload.candidates else 1

    ranked = []
    for c in payload.candidates:
        norm_lessons = c.past_lessons / max_lessons if max_lessons > 0 else 0
        load_inv = 1.0 - (c.teacher_load / (max_load + 1))
        s = 0.5 * norm_lessons + 0.3 * c.attendance_rate + 0.2 * load_inv

        reasons: list[str] = []
        if c.past_lessons >= 3:
            reasons.append(f"過去{c.past_lessons}回受講実績あり")
        if c.attendance_rate >= 0.9:
            reasons.append(f"出席率{int(c.attendance_rate*100)}%")
        if c.teacher_load == 0:
            reasons.append("現在空き時間")

        ranked.append(RankedCandidate(candidate_id=c.candidate_id, score=round(s, 4), reasons=reasons))

    ranked.sort(key=lambda x: x.score, reverse=True)
    return MakeupResponse(ranked=ranked)
