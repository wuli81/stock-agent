"""运行日志数据访问。"""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.entities import Log


def add_log(
    db: Session,
    level: str,
    module: str,
    message: str,
    extra_json: str | None = None,
) -> Log:
    row = Log(
        ts=datetime.now(UTC).isoformat(),
        level=level,
        module=module,
        message=message,
        extra_json=extra_json,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
