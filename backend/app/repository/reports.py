"""每日报告数据访问。"""

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import DailyReport


def get_by_date(db: Session, report_date: str) -> DailyReport | None:
    return db.scalar(select(DailyReport).where(DailyReport.report_date == report_date))


def save_report(db: Session, report_date: str, summary: dict) -> DailyReport:
    row = db.scalar(select(DailyReport).where(DailyReport.report_date == report_date))
    if row is None:
        row = DailyReport(report_date=report_date)
        db.add(row)
    row.summary_json = json.dumps(summary, ensure_ascii=False)
    db.commit()
    db.refresh(row)
    return row
