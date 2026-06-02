"""API v1 route aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    attribution,
    analytics,
    event_explorer,
    event_health,
    health,
    insights,
    quality,
    tracking,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(tracking.router)
api_router.include_router(event_health.router)
api_router.include_router(event_explorer.router)
api_router.include_router(analytics.router)
api_router.include_router(attribution.router)
api_router.include_router(quality.router)
api_router.include_router(insights.router)
