"""执行器心跳接口。"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.repository import logs as logs_repo

router = APIRouter(
    prefix="/executor",
    tags=["executor"],
    dependencies=[Depends(require_api_key)],
)


class HeartbeatRequest(BaseModel):
    executor_id: str
    status: str  # idle | running | error
    message: str = ""


@router.post("/heartbeat")
def heartbeat(payload: HeartbeatRequest, db: Session = Depends(get_db)) -> dict:
    logs_repo.add_log(
        db,
        level="INFO",
        module="executor-heartbeat",
        message=f"{payload.executor_id} -> {payload.status}",
        extra_json=payload.message,
    )
    return {"code": 0, "message": "ok", "data": {"accepted": True}}
