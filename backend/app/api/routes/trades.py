"""成交接口（含幂等上报）。"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.models.entities import Trade
from app.repository import trades as trades_repo
from shared.models import TradeReport

router = APIRouter(
    prefix="/trades",
    tags=["trades"],
    dependencies=[Depends(require_api_key)],
)


def _trade_to_dict(trade: Trade) -> dict:
    return {
        "trade_id": trade.id,
        "order_id": trade.order_id,
        "client_request_id": trade.client_request_id,
        "code": trade.code,
        "side": trade.side,
        "quantity": trade.quantity,
        "price": trade.price,
        "amount": trade.amount,
        "commission": trade.commission,
        "traded_at": trade.traded_at.isoformat() if trade.traded_at else None,
    }


@router.post("", status_code=201)
def report_trade(payload: TradeReport, db: Session = Depends(get_db)) -> dict:
    existing = trades_repo.find_by_client_request_id(db, payload.client_request_id)
    if existing is not None:
        # 幂等：重复上报返回同一 trade_id
        return {"code": 0, "message": "ok", "data": {"trade_id": existing.id}}
    trade = trades_repo.save_trade(db, payload)
    return {"code": 0, "message": "ok", "data": {"trade_id": trade.id}}


@router.get("")
def list_trades(
    date: date | None = None,
    code: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> dict:
    limit = min(max(limit, 1), 200)
    rows = trades_repo.list_trades(db, trade_date=date, code=code, limit=limit, offset=offset)
    return {
        "code": 0,
        "message": "ok",
        "data": {"trades": [_trade_to_dict(t) for t in rows], "total": len(rows)},
    }


@router.get("/{trade_id}")
def get_trade_detail(trade_id: int, db: Session = Depends(get_db)) -> dict:
    trade = trades_repo.get_trade(db, trade_id)
    if trade is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 2001, "message": "成交不存在"},
        )
    return {"code": 0, "message": "ok", "data": _trade_to_dict(trade)}
