"""行情与股票基础信息数据访问。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.base import Bar, StockInfo
from app.models.entities import DailyQuote, Stock


def upsert_stocks(db: Session, stocks: list[StockInfo]) -> int:
    """新增/更新股票基础信息，返回新增数量。"""
    added = 0
    for info in stocks:
        row = db.get(Stock, info.code)
        if row is None:
            db.add(Stock(code=info.code, name=info.name))
            added += 1
        elif row.name != info.name:
            row.name = info.name
    db.commit()
    return added


def save_quotes(db: Session, bars: list[Bar]) -> int:
    """批量保存日线行情（按 code+date 去重），返回新增数量。"""
    saved = 0
    for bar in bars:
        exists = db.scalar(
            select(DailyQuote.id).where(
                DailyQuote.code == bar.code, DailyQuote.date == bar.date
            )
        )
        if exists is not None:
            continue
        db.add(
            DailyQuote(
                code=bar.code,
                date=bar.date,
                open=bar.open,
                high=bar.high,
                low=bar.low,
                close=bar.close,
                pre_close=bar.pre_close,
                volume=bar.volume,
                amount=bar.amount,
                turn_rate=bar.turn_rate,
            )
        )
        saved += 1
    db.commit()
    return saved


def get_recent_quotes(db: Session, code: str, days: int = 60) -> list[DailyQuote]:
    return list(
        db.scalars(
            select(DailyQuote)
            .where(DailyQuote.code == code)
            .order_by(DailyQuote.date.desc())
            .limit(days)
        )
    )


def list_tracked_codes(db: Session, codes: list[str] | None = None) -> list[str]:
    """优先使用配置的代码列表；否则返回已有行情记录的股票代码。"""
    if codes:
        return codes
    rows = db.execute(
        select(DailyQuote.code).distinct().order_by(DailyQuote.code)
    ).all()
    return [r[0] for r in rows]
