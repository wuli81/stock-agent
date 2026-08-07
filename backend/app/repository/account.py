"""账户快照数据访问。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import AccountSnapshot


def get_by_date(db: Session, snapshot_date: str | None) -> AccountSnapshot | None:
    if snapshot_date is not None:
        return db.scalar(
            select(AccountSnapshot).where(AccountSnapshot.snapshot_date == snapshot_date)
        )
    return db.scalar(
        select(AccountSnapshot).order_by(AccountSnapshot.snapshot_date.desc()).limit(1)
    )
