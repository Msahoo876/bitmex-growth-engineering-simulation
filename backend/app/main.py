"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app import __version__
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError, ResourceNotFoundError
from app.services.analytics_service import FunnelNotFoundError
from app.core.logging_config import configure_logging
from app.core.middleware import SecurityHeadersMiddleware
from app.db.base import import_models

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan — register models on startup."""
    settings = get_settings()
    configure_logging(settings)
    import_models()
    logger.info("Application started env=%s", settings.app_env)
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="Growth Engineering Analytics Platform API",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
        lifespan=lifespan,
        debug=settings.app_debug,
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.app_env == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],
        )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.exception_handler(ResourceNotFoundError)
    async def not_found_handler(_request: Request, exc: ResourceNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(FunnelNotFoundError)
    async def funnel_not_found_handler(_request: Request, exc: FunnelNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.message, "code": exc.code})

    @app.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        return {
            "service": settings.app_name,
            "version": __version__,
            "docs": f"{settings.api_v1_prefix}/docs",
        }

    return app


app = create_app()
