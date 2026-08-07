"""交易计划接口。"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.models.entities import TradePlan
from app.repository import plans as plans_repo

router = APIRouter(
    prefix="/trade-plans",
    tags=["trade-plans"],
    dependencies=[Depends(require_api_key)],
)


def _item_to_dict(item) -> dict:
    return {
        "item_id": item.id,
        "code": item.code,
        "side": item.side,
        "quantity": item.quantity,
        "price_min": item.price_min,
        "price_max": item.price_max,
        "expire_at": item.expire_at.isoformat() if item.expire_at else None,
        "status": item.status,
        "reason": item.reason,
    }


def _plan_to_dict(plan: TradePlan) -> dict:
    return {
        "plan_id": plan.id,
        "plan_date": plan.plan_date,
        "status": plan.status,
        "items": [_item_to_dict(item) for item in plan.items],
    }


@router.get("")
def list_plans(
    date: date,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> dict:
    limit = min(max(limit, 1), 200)
    rows = plans_repo.list_plans(db, plan_date=date, status=status, limit=limit, offset=offset)
    return {
        "code": 0,
        "message": "ok",
        "data": {"plans": [_plan_to_dict(p) for p in rows], "total": len(rows)},
    }


@router.get("/{plan_id}")
def get_plan_detail(plan_id: int, db: Session = Depends(get_db)) -> dict:
    plan = plans_repo.get_plan(db, plan_id)
    if plan is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 2001, "message": "计划不存在"},
        )
    return {"code": 0, "message": "ok", "data": _plan_to_dict(plan)}
