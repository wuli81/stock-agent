from app.models.entities import Stock


def _ensure_stock(db):
    if db.get(Stock, "600000") is None:
        db.add(Stock(code="600000", name="浦发银行"))
        db.commit()


def test_report_trade_idempotent(client, db, auth_headers):
    _ensure_stock(db)
    payload = {
        "client_request_id": "exec-01-0001",
        "item_id": 10,
        "order_no": "BK001",
        "code": "600000",
        "side": "buy",
        "quantity": 100,
        "price": 10.62,
        "traded_at": "2026-08-08T09:31:05+08:00",
        "commission": 5.0,
    }
    r1 = client.post("/api/v1/trades", json=payload, headers=auth_headers)
    assert r1.status_code == 201
    trade_id = r1.json()["data"]["trade_id"]

    r2 = client.post("/api/v1/trades", json=payload, headers=auth_headers)
    assert r2.status_code == 201
    assert r2.json()["data"]["trade_id"] == trade_id

    resp = client.get("/api/v1/trades", headers=auth_headers)
    assert resp.json()["data"]["total"] == 1


def test_report_trade_with_order_id(client, db, auth_headers):
    _ensure_stock(db)
    payload = {
        "client_request_id": "exec-01-0002",
        "item_id": 10,
        "order_id": 123,
        "order_no": "BK002",
        "code": "600000",
        "side": "buy",
        "quantity": 100,
        "price": 10.62,
        "traded_at": "2026-08-08T09:31:05+08:00",
    }
    r1 = client.post("/api/v1/trades", json=payload, headers=auth_headers)
    assert r1.status_code == 201
    trade_id = r1.json()["data"]["trade_id"]
    detail = client.get(f"/api/v1/trades/{trade_id}", headers=auth_headers).json()
    assert detail["data"]["order_id"] == 123


def test_trades_requires_auth(client):
    assert client.post("/api/v1/trades", json={}).status_code == 401
