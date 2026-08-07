"""聚合所有路由。"""

from fastapi import APIRouter

from app.api.routes import account, health, heartbeat, reports, strategies, trade_plans, trades

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(trade_plans.router)
api_router.include_router(trades.router)
api_router.include_router(account.router)
api_router.include_router(reports.router)
api_router.include_router(strategies.router)
api_router.include_router(heartbeat.router)
