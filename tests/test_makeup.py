import pytest
from features.makeup import MakeupRequest, Candidate, score


def make_req(*candidates):
    return MakeupRequest(student_id="s1", candidates=list(candidates))


def test_score_ranking_by_past_lessons():
    """過去受講回数が多い候補ほど上位になる"""
    req = make_req(
        Candidate(candidate_id="c1", past_lessons=1, attendance_rate=0.8, teacher_load=2),
        Candidate(candidate_id="c2", past_lessons=8, attendance_rate=0.8, teacher_load=2),
    )
    res = score(req)
    assert res.ranked[0].candidate_id == "c2"


def test_score_empty_candidates():
    """候補なしは空リストを返す"""
    req = MakeupRequest(student_id="s1", candidates=[])
    res = score(req)
    assert res.ranked == []


def test_score_reasons_populated():
    """十分な実績がある候補は reasons が付く"""
    req = make_req(
        Candidate(candidate_id="c1", past_lessons=5, attendance_rate=0.95, teacher_load=0),
    )
    res = score(req)
    assert len(res.ranked[0].reasons) > 0


def test_score_low_load_bonus():
    """担当コマ0の講師は負荷ボーナスが最大になる"""
    req = make_req(
        Candidate(candidate_id="busy", past_lessons=0, attendance_rate=0.5, teacher_load=10),
        Candidate(candidate_id="free", past_lessons=0, attendance_rate=0.5, teacher_load=0),
    )
    res = score(req)
    free = next(r for r in res.ranked if r.candidate_id == "free")
    busy = next(r for r in res.ranked if r.candidate_id == "busy")
    assert free.score > busy.score
