"""订单接口（v0.4 订单状态同步）。"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.models.entities import Order
from app.repository import orders as orders_repo
from shared.models import OrderReport

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    dependencies=[Depends(require_api_key)],
)


def _order_to_dict(order: Order) -> dict:
    return {
        "order_id": order.id,
        "client_request_id": order.client_request_id,
        "item_id": order.item_id,
        "order_no": order.order_no,
        "code": order.code,
        "side": order.side,
        "quantity": order.quantity,
        "price": order.price,
        "status": order.status,
        "error": order.error,
        "created_at": order.created_at.isoformat() if order.created_at else None,
    }


@router.post("", status_code=201)
def report_order(payload: OrderReport, db: Session = Depends(get_db)) -> dict:
    order = orders_repo.save_order(db, payload)
    return {"code": 0, "message": "ok", "data": {"order_id": order.id}}


@router.get("")
def list_orders(
    date: date | None = None,
    code: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> dict:
    limit = min(max(limit, 1), 200)
    rows = orders_repo.list_orders(
        db, order_date=date, code=code, status=status, limit=limit, offset=offset
    )
    return {
        "code": 0,
        "message": "ok",
        "data": {"orders": [_order_to_dict(o) for o in rows], "total": len(rows)},
    }


@router.get("/{order_id}")
def get_order_detail(order_id: int, db: Session = Depends(get_db)) -> dict:
    order = orders_repo.get_order(db, order_id)
    if order is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 2001, "message": "订单不存在"},
        )
    return {"code": 0, "message": "ok", "data": _order_to_dict(order)}
