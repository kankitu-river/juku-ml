"""退塾予兆検知 (B-2)

特徴量設計とモデル選定は開発者本人が実装予定。
このファイルはスタブ（インターフェースのみ確定）。
"""
from __future__ import annotations
from pydantic import BaseModel


class WeeklyRecord(BaseModel):
    week: str         # "2026-W20"
    scheduled: int
    attended: int
    makeup_pending: int


class StudentHistory(BaseModel):
    id: str
    weekly: list[WeeklyRecord]


class ChurnRequest(BaseModel):
    students: list[StudentHistory]


class ChurnAlert(BaseModel):
    student_id: str
    score: float      # 0〜1
    reasons: list[str]


class ChurnResponse(BaseModel):
    alerts: list[ChurnAlert]


def detect(payload: ChurnRequest) -> ChurnResponse:
    # TODO: B-2 実装（開発者本人が特徴量設計・モデル選定を行う）
    return ChurnResponse(alerts=[])
