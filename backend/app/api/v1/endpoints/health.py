"""Health and readiness probes for infrastructure."""

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import DbSessionDep, RedisDep, SettingsDep
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check(settings: SettingsDep) -> HealthResponse:
    """Liveness probe — process is running."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.app_env,
        version="0.1.0",
    )


@router.get("/ready", response_model=ReadinessResponse)
def readiness_check(db: DbSessionDep, redis: RedisDep) -> ReadinessResponse:
    """Readiness probe — verifies PostgreSQL and Redis connectivity."""
    checks: dict[str, str] = {}

    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except SQLAlchemyError as exc:
        checks["database"] = f"error: {exc}"

    try:
        redis.ping()
        checks["redis"] = "ok"
    except Exception as exc:  # noqa: BLE001 — surface connection errors to ops
        checks["redis"] = f"error: {exc}"

    status = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return ReadinessResponse(status=status, checks=checks)
