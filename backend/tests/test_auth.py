from datetime import date

from app.models.entities import Stock
from app.repository import plans as plans_repo


def _ensure_stock(db, code="600000"):
    if db.get(Stock, code) is None:
        db.add(Stock(code=code, name="浦发银行"))
        db.commit()


def test_trade_plans_requires_auth(client):
    resp = client.get("/api/v1/trade-plans", params={"date": "2026-08-07"})
    assert resp.status_code == 401


def test_trade_plans_with_auth(client, db, auth_headers):
    _ensure_stock(db)
    plans_repo.save_plan(
        db,
        plan_date=date(2026, 8, 7),
        status="published",
        total_budget=100000,
        items=[{"code": "600000", "side": "buy", "quantity": 100, "reason": "测试"}],
    )
    resp = client.get(
        "/api/v1/trade-plans", params={"date": "2026-08-07"}, headers=auth_headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert data["total"] == 1
    plan = data["plans"][0]
    assert plan["plan_date"] == "2026-08-07"
    assert plan["items"][0]["code"] == "600000"
    assert plan["items"][0]["side"] == "buy"


def test_plan_detail_not_found(client, auth_headers):
    resp = client.get("/api/v1/trade-plans/999", headers=auth_headers)
    assert resp.status_code == 404
