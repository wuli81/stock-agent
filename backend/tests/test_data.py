from app.data.base import Bar, StockInfo
from app.repository import quotes as quotes_repo


def test_upsert_stocks(db):
    added = quotes_repo.upsert_stocks(
        db,
        [
            StockInfo(code="600519", name="贵州茅台"),
            StockInfo(code="601318", name="中国平安"),
        ],
    )
    assert added == 2
    added2 = quotes_repo.upsert_stocks(db, [StockInfo(code="600519", name="贵州茅台")])
    assert added2 == 0


def test_save_quotes_dedup(db):
    bars = [Bar(code="600519", date="2026-08-07", close=10.0)]
    assert quotes_repo.save_quotes(db, bars) == 1
    assert quotes_repo.save_quotes(db, bars) == 0
    quotes = quotes_repo.get_recent_quotes(db, "600519", days=10)
    assert len(quotes) == 1
    assert quotes[0].close == 10.0


def test_list_tracked_codes_fallback(db):
    quotes_repo.save_quotes(db, [Bar(code="600519", date="2026-08-07", close=10.0)])
    codes = quotes_repo.list_tracked_codes(db, [])
    assert codes == ["600519"]
