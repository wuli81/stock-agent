"""策略元数据数据访问。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Strategy


def get_or_create(
    db: Session, name: str, class_name: str = "", version: str = "0.1.0"
) -> Strategy:
    row = db.scalar(select(Strategy).where(Strategy.name == name))
    if row is None:
        row = Strategy(name=name, class_name=class_name, version=version)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row
