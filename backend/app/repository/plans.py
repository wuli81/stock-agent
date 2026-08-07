"""交易计划数据访问。"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import TradePlan, TradePlanItem


def get_plan(db: Session, plan_id: int) -> TradePlan | None:
    return db.get(TradePlan, plan_id)


def get_plan_by_date(db: Session, plan_date: date) -> TradePlan | None:
    return db.scalar(select(TradePlan).where(TradePlan.plan_date == plan_date.isoformat()))


def list_plans(
    db: Session,
    plan_date: date | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[TradePlan]:
    stmt = select(TradePlan).order_by(TradePlan.plan_date.desc(), TradePlan.id.desc())
    if plan_date is not None:
        stmt = stmt.where(TradePlan.plan_date == plan_date.isoformat())
    if status is not None:
        stmt = stmt.where(TradePlan.status == status)
    return list(db.scalars(stmt.limit(limit).offset(offset)))


def save_plan(
    db: Session,
    plan_date: date,
    status: str = "draft",
    total_budget: float | None = None,
    note: str | None = None,
    items: list[dict] | None = None,
) -> TradePlan:
    plan = TradePlan(
        plan_date=plan_date.isoformat(),
        status=status,
        total_budget=total_budget,
        note=note,
    )
    for item in items or []:
        plan.items.append(TradePlanItem(**item))
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def update_item_status(db: Session, item_id: int, status: str) -> None:
    item = db.get(TradePlanItem, item_id)
    if item is not None:
        item.status = status
        db.commit()
