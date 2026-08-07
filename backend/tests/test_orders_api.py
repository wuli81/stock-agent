from app.models.entities import Stock


def _ensure_stock(db):
    if db.get(Stock, "600000") is None:
        db.add(Stock(code="600000", name="浦发银行"))
        db.commit()


def test_report_order_idempotent(client, db, auth_headers):
    _ensure_stock(db)
    payload = {
        "client_request_id": "ord-0001",
        "item_id": 10,
        "order_no": "BK001",
        "code": "600000",
        "side": "buy",
        "quantity": 100,
        "price": 10.75,
        "status": "filled",
    }
    r1 = client.post("/api/v1/orders", json=payload, headers=auth_headers)
    assert r1.status_code == 201
    order_id = r1.json()["data"]["order_id"]

    r2 = client.post("/api/v1/orders", json=payload, headers=auth_headers)
    assert r2.status_code == 201
    assert r2.json()["data"]["order_id"] == order_id

    resp = client.get("/api/v1/orders", headers=auth_headers)
    assert resp.json()["data"]["total"] == 1
    assert resp.json()["data"]["orders"][0]["status"] == "filled"


def test_orders_requires_auth(client):
    assert client.post("/api/v1/orders", json={}).status_code == 401
