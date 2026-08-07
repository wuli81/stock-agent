"""数据源工厂。"""

from __future__ import annotations

from app.core.config import get_settings
from app.data.base import DataProvider


def create_provider(name: str | None = None) -> DataProvider:
    provider_name = (name or get_settings().data_provider).strip().lower()
    if provider_name in ("akshare", "ak"):
        from app.data.akshare_provider import AkshareDataProvider

        return AkshareDataProvider()
    raise ValueError(f"unknown data provider: {provider_name}")
