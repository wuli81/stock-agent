from datetime import date, timedelta

from app.data.base import Bar, DataProvider, StockInfo
from app.models.entities import StrategyRun
from app.repository import plans as plans_repo
from app.repository import reports as reports_repo
from app.scheduler.jobs import run_daily_analysis
from sqlalchemy import select


class FakeProvider(DataProvider):
    name = "fake"

    def __init__(self, uptrend_codes=("600000",), downtrend_codes=("000001",)):
        self.uptrend_codes = set(uptrend_codes)
        self.downtrend_codes = set(downtrend_codes)

    def fetch_stock_basics(self):
        return [
            StockInfo(code="600000", name="浦发银行"),
            StockInfo(code="000001", name="平安银行"),
        ]

    def fetch_daily(self, code, start, end):
        uptrend = code in self.uptrend_codes
        bars = []
        for i in range(30):
            d = (start + timedelta(days=i)).isoformat()
            close = 10.0 + (0.1 if uptrend else -0.1) * i
            bars.append(
                Bar(
                    code=code,
                    date=d,
                    open=close,
                    high=close,
                    low=close,
                    close=close,
                    volume=1000,
                    amount=1000 * close,
                    turn_rate=1.0,
                )
            )
        return bars


def test_run_daily_analysis_creates_plan_and_report(db):
    report = run_daily_analysis(
        plan_date=date(2026, 8, 10),
        provider=FakeProvider(),
        strategy_name="ma_cross",
    )
    assert report["candidate_count"] == 1  # 仅上升趋势的 600000 入选
    assert report["plan_items"] == 1
    assert report["quotes_codes"] == ["000001", "600000"]

    plan = plans_repo.get_plan_by_date(db, date(2026, 8, 10))
    assert plan is not None
    assert len(plan.items) == 1
    assert plan.items[0].code == "600000"

    daily = reports_repo.get_by_date(db, "2026-08-10")
    assert daily is not None
    assert "candidate_count" in daily.summary_json

    run = db.scalar(select(StrategyRun).where(StrategyRun.run_date == "2026-08-10"))
    assert run is not None
    assert run.status == "success"


def test_run_daily_analysis_empty_plan_when_no_candidates(db):
    report = run_daily_analysis(
        plan_date=date(2026, 8, 8),
        provider=FakeProvider(uptrend_codes=(), downtrend_codes=("600000", "000001")),
        strategy_name="ma_cross",
    )
    assert report["candidate_count"] == 0
    assert report["plan_items"] == 0

    plan = plans_repo.get_plan_by_date(db, date(2026, 8, 8))
    assert plan is not None
    assert plan.items == []

    daily = reports_repo.get_by_date(db, "2026-08-08")
    assert daily is not None
