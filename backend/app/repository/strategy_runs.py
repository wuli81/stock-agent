"""策略运行记录数据访问。"""

import json
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import StrategyRun
from app.repository import strategies as strategies_repo
from app.strategy.base import Candidate


def record_run(
    db: Session,
    strategy_name: str,
    run_date: date,
    candidates: list[Candidate],
    error: str | None = None,
) -> StrategyRun:
    strategy = strategies_repo.get_or_create(db, strategy_name, class_name=strategy_name)
    run = db.scalar(
        select(StrategyRun).where(
            StrategyRun.strategy_id == strategy.id,
            StrategyRun.run_date == run_date.isoformat(),
        )
    )
    if run is None:
        run = StrategyRun(strategy_id=strategy.id, run_date=run_date.isoformat())
        db.add(run)
    run.status = "failed" if error else "success"
    run.finished_at = datetime.now(UTC)
    run.candidates_json = json.dumps(
        [c.__dict__ for c in candidates], ensure_ascii=False
    )
    run.error = error
    db.commit()
    db.refresh(run)
    return run
