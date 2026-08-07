"""pytest 全局配置：使用内存数据库，避免污染开发库。"""

import os

os.environ.setdefault("STOCK_AGENT_DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("STOCK_AGENT_API_KEYS", "test-key")
os.environ.setdefault("STOCK_AGENT_ENABLE_SCHEDULER", "false")
os.environ.setdefault("STOCK_AGENT_TRACKED_STOCKS", "600000,000001")

import pytest
from app.main import app
from app.models.base import Base
from app.repository.db import SessionLocal, engine, get_db
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def _setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture()
def client():
    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers() -> dict:
    return {"Authorization": "Bearer test-key"}
