from datetime import date

from app.planner.service import build_plan
from app.strategy.base import Candidate

from shared.enums import PlanStatus, Side


def test_build_plan_limits_items():
    candidates = [Candidate(code=f"60000{i}", score=10 - i, reason="x") for i in range(10)]
    plan = build_plan(date(2026, 8, 7), candidates, max_items=5)
    assert plan.status == PlanStatus.PUBLISHED
    assert len(plan.items) == 5
    assert all(i.side == Side.BUY for i in plan.items)
    assert plan.items[0].code == "600000"


def test_build_plan_empty():
    plan = build_plan(date(2026, 8, 7), [])
    assert plan.items == []
