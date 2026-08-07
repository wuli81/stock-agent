from datetime import date

import httpx
from executor.receiver.client import BackendClient

from shared.enums import Side
from shared.models import OrderReport


def _fake_response(payload):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return payload

    return FakeResponse


def test_fetch_plan_parses(monkeypatch):
    payload = {
        "code": 0,
        "message": "ok",
        "data": {
            "plans": [
                {
                    "plan_id": 1,
                    "plan_date": "2026-08-07",
                    "status": "published",
                    "items": [
                        {"item_id": 10, "code": "600000", "side": "buy", "quantity": 100}
                    ],
                }
            ],
            "total": 1,
        },
    }
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _fake_response(payload)())
    plan = BackendClient("http://localhost:8000/api/v1", "dev-key").fetch_plan(date(2026, 8, 7))
    assert plan is not None
    assert plan.plan_date.isoformat() == "2026-08-07"
    assert plan.items[0].code == "600000"
    assert plan.items[0].side.value == "buy"


def test_fetch_plan_none(monkeypatch):
    payload = {"code": 0, "message": "ok", "data": {"plans": [], "total": 0}}
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _fake_response(payload)())
    plan = BackendClient("http://localhost:8000/api/v1", "dev-key").fetch_plan(date(2026, 8, 8))
    assert plan is None


def test_report_order(monkeypatch):
    payload = {"code": 0, "message": "ok", "data": {"order_id": 42}}
    monkeypatch.setattr(httpx, "post", lambda *a, **k: _fake_response(payload)())
    report = OrderReport(
        client_request_id="r1",
        item_id=10,
        code="600000",
        side=Side.BUY,
        quantity=100,
    )
    order_id = BackendClient("http://localhost:8000/api/v1", "dev-key").report_order(report)
    assert order_id == 42
