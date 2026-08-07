"""健康检查。"""

from datetime import UTC, datetime

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict:
    return {
        "code": 0,
        "message": "ok",
        "data": {
            "status": "ok",
            "version": get_settings().version,
            "time": datetime.now(UTC).isoformat(),
        },
    }
