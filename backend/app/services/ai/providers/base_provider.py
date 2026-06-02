"""Provider contract for AI insight generation."""

from dataclasses import dataclass, field
from typing import Any, Protocol


class AIProviderError(Exception):
    """Raised when an AI provider cannot complete a request."""


@dataclass(slots=True)
class AIInsightDraft:
    title: str
    summary: str
    recommendations: list[dict[str, str]] = field(default_factory=list)
    priority: str = "medium"
    model_name: str = "local-rules"


class AIInsightProvider(Protocol):
    model_name: str

    def generate(self, *, prompt: str, metrics: dict[str, Any]) -> AIInsightDraft:
        """Generate a single insight draft from structured metrics."""
