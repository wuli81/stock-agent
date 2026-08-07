"""跨端共享枚举。"""

from enum import IntEnum, StrEnum


class Side(StrEnum):
    BUY = "buy"
    SELL = "sell"


class PlanStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    EXECUTING = "executing"
    DONE = "done"
    CANCELLED = "cancelled"


class ItemStatus(StrEnum):
    PENDING = "pending"
    EXECUTING = "executing"
    FILLED = "filled"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OrderStatus(StrEnum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL = "partial"
    FILLED = "filled"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunStatus(StrEnum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class ErrorCode(IntEnum):
    OK = 0
    AUTH_FAILED = 1001
    INVALID_PARAMS = 1002
    PLAN_NOT_FOUND = 2001
    PLAN_NOT_EXECUTABLE = 2002
    QUOTE_MISSING = 3001
    DUPLICATE_REPORT = 4001
    INTERNAL_ERROR = 5000
