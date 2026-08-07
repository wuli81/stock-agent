"""API 依赖汇总。"""

from app.core.security import require_api_key
from app.repository.db import get_db

__all__ = ["get_db", "require_api_key"]
