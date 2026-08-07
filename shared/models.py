"""跨端共享 Pydantic 数据结构（与 openapi.yaml 保持一致）。"""

from datetime import date, datetime

from pydantic import BaseModel, Field

from shared.enums import ItemStatus, PlanStatus, Side


class Candidate(BaseModel):
    """策略输出的候选标的。"""

    code: str
    name: str | None = None
    score: float = 0.0
    reason: str = ""


class TradePlanItem(BaseModel):
    item_id: int | None = None
    code: str
    name: str | None = None
    side: Side = Side.BUY
    quantity: int = Field(gt=0)
    price_min: float | None = None
    price_max: float | None = None
    expire_at: datetime | None = None
    status: ItemStatus = ItemStatus.PENDING
    reason: str | None = None


class TradePlan(BaseModel):
    plan_id: int | None = None
    plan_date: date
    status: PlanStatus = PlanStatus.DRAFT
    items: list[TradePlanItem] = Field(default_factory=list)


class TradeReport(BaseModel):
    """执行器上报成交的请求体。"""

    client_request_id: str
    item_id: int
    order_no: str | None = None
    code: str
    side: Side
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)
    traded_at: datetime
    commission: float = 0.0
