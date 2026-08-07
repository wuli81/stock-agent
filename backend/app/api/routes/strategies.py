"""策略列表接口。"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.models.entities import Strategy

router = APIRouter(
    prefix="/strategies",
    tags=["strategies"],
    dependencies=[Depends(require_api_key)],
)


@router.get("")
def list_strategies(db: Session = Depends(get_db)) -> dict:
    rows = list(db.scalars(select(Strategy).order_by(Strategy.id)))
    return {
        "code": 0,
        "message": "ok",
        "data": {
            "strategies": [
                {
                    "strategy_id": s.id,
                    "name": s.name,
                    "version": s.version,
                    "enabled": s.enabled,
                }
                for s in rows
            ],
            "total": len(rows),
        },
    }
