from datetime import date

import httpx
from executor.receiver.client import BackendClient


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
