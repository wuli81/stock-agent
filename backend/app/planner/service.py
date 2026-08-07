"""交易计划生成服务。

v0.1 采用简化规则：取评分最高的若干候选标的，每个标的 100 股（一手）。
"""

from datetime import date

from app.strategy.base import Candidate
from shared.enums import ItemStatus, PlanStatus, Side
from shared.models import TradePlan, TradePlanItem


def build_plan(
    plan_date: date,
    candidates: list[Candidate],
    total_budget: float = 100_000.0,
    max_items: int = 5,
    qty_per_item: int = 100,
) -> TradePlan:
    items: list[TradePlanItem] = []
    for cand in candidates[:max_items]:
        items.append(
            TradePlanItem(
                code=cand.code,
                name=cand.name,
                side=Side.BUY,
                quantity=qty_per_item,
                status=ItemStatus.PENDING,
                reason=cand.reason,
            )
        )
    return TradePlan(
        plan_date=plan_date,
        status=PlanStatus.PUBLISHED,
        items=items,
    )
