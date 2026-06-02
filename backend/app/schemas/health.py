"""Health check response schemas."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    version: str


class ReadinessResponse(BaseModel):
    status: str
    checks: dict[str, str] = Field(default_factory=dict)
