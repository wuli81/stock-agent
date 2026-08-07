"""每日报告接口。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.repository import reports as reports_repo

router = APIRouter(
    prefix="/daily-reports",
    tags=["reports"],
    dependencies=[Depends(require_api_key)],
)


@router.get("/{report_date}")
def get_daily_report(report_date: str, db: Session = Depends(get_db)) -> dict:
    report = reports_repo.get_by_date(db, report_date)
    if report is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 2001, "message": "报告不存在"},
        )
    return {
        "code": 0,
        "message": "ok",
        "data": {
            "report_date": report.report_date,
            "summary": report.summary_json,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        },
    }
