"""成交数据访问。"""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import Trade
from shared.models import TradeReport


def find_by_client_request_id(db: Session, client_request_id: str) -> Trade | None:
    return db.scalar(select(Trade).where(Trade.client_request_id == client_request_id))


def get_trade(db: Session, trade_id: int) -> Trade | None:
    return db.get(Trade, trade_id)


def save_trade(db: Session, report: TradeReport) -> Trade:
    trade = Trade(
        client_request_id=report.client_request_id,
        item_id=report.item_id,
        order_no=report.order_no,
        code=report.code,
        side=report.side.value,
        quantity=report.quantity,
        price=report.price,
        amount=report.price * report.quantity,
        commission=report.commission or 0.0,
        traded_at=report.traded_at,
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade


def list_trades(
    db: Session,
    trade_date: date | None = None,
    code: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Trade]:
    stmt = select(Trade).order_by(Trade.id.desc())
    if trade_date is not None:
        stmt = stmt.where(func.date(Trade.traded_at) == trade_date.isoformat())
    if code is not None:
        stmt = stmt.where(Trade.code == code)
    return list(db.scalars(stmt.limit(limit).offset(offset)))
