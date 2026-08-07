"""账户与持仓接口。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.models.entities import AccountSnapshot
from app.repository import account as account_repo

router = APIRouter(
    prefix="/account",
    tags=["account"],
    dependencies=[Depends(require_api_key)],
)


def _snap_to_dict(snap: AccountSnapshot) -> dict:
    return {
        "snapshot_date": snap.snapshot_date,
        "total_asset": snap.total_asset,
        "available_cash": snap.available_cash,
        "market_value": snap.market_value,
        "positions": snap.positions_json,
    }


@router.get("")
def get_account(date: str | None = None, db: Session = Depends(get_db)) -> dict:
    snap = account_repo.get_by_date(db, date)
    if snap is None:
        return {"code": 0, "message": "ok", "data": None}
    return {"code": 0, "message": "ok", "data": _snap_to_dict(snap)}
