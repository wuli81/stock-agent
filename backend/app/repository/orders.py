"""订单数据访问（v0.4）。"""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import Order
from shared.models import OrderReport


def get_order(db: Session, order_id: int) -> Order | None:
    return db.get(Order, order_id)


def find_by_client_request_id(db: Session, client_request_id: str) -> Order | None:
    return db.scalar(select(Order).where(Order.client_request_id == client_request_id))


def save_order(db: Session, report: OrderReport) -> Order:
    """幂等创建/更新订单（以 client_request_id 为幂等键）。"""
    existing = find_by_client_request_id(db, report.client_request_id)
    if existing is not None:
        existing.order_no = report.order_no or existing.order_no
        existing.price = report.price
        existing.status = report.status
        existing.error = report.error
        db.commit()
        db.refresh(existing)
        return existing
    order = Order(
        client_request_id=report.client_request_id,
        item_id=report.item_id,
        order_no=report.order_no,
        code=report.code,
        side=report.side.value,
        quantity=report.quantity,
        price=report.price,
        status=report.status,
        error=report.error,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def list_orders(
    db: Session,
    order_date: date | None = None,
    code: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Order]:
    stmt = select(Order).order_by(Order.id.desc())
    if order_date is not None:
        stmt = stmt.where(func.date(Order.created_at) == order_date.isoformat())
    if code is not None:
        stmt = stmt.where(Order.code == code)
    if status is not None:
        stmt = stmt.where(Order.status == status)
    return list(db.scalars(stmt.limit(limit).offset(offset)))
