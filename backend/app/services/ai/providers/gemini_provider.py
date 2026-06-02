"""Gemini provider using the google-genai SDK."""

import json
import logging
import time
from typing import Any

from app.services.ai.providers.base_provider import AIInsightDraft, AIProviderError

logger = logging.getLogger(__name__)


class GeminiProvider:
    def __init__(
        self,
        *,
        api_key: str | None,
        model_name: str = "gemini-2.5-flash",
        retries: int = 2,
        backoff_seconds: float = 0.5,
    ) -> None:
        self.api_key = api_key
        self.model_name = model_name
        self.retries = retries
        self.backoff_seconds = backoff_seconds

    def generate(self, *, prompt: str, metrics: dict[str, Any]) -> AIInsightDraft:
        if not self.api_key:
            raise AIProviderError("GEMINI_API_KEY is not configured.")

        try:
            from google import genai
        except ImportError as exc:
            raise AIProviderError("google-genai is not installed.") from exc

        client = genai.Client(api_key=self.api_key)
        payload = (
            f"{prompt}\n\n"
            "Return only valid JSON with keys: title, summary, recommendations, priority.\n"
            f"Structured metrics:\n{json.dumps(metrics, default=str)}"
        )

        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=payload,
                )
                data = self._parse_json(getattr(response, "text", "") or "")
                return AIInsightDraft(
                    title=str(data.get("title") or "Growth Insight"),
                    summary=str(data.get("summary") or data.get("executive_summary") or ""),
                    recommendations=self._normalize_recommendations(
                        data.get("recommendations", [])
                    ),
                    priority=str(data.get("priority") or "medium"),
                    model_name=self.model_name,
                )
            except Exception as exc:  # pragma: no cover - provider behavior is external.
                last_error = exc
                logger.warning("Gemini insight attempt failed attempt=%s error=%s", attempt + 1, exc)
                if attempt < self.retries:
                    time.sleep(self.backoff_seconds * (attempt + 1))

        raise AIProviderError("Gemini failed to generate an insight.") from last_error

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.removeprefix("json").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start >= 0 and end > start:
                return json.loads(cleaned[start : end + 1])
            raise AIProviderError("Gemini returned non-JSON content.")

    @staticmethod
    def _normalize_recommendations(value: Any) -> list[dict[str, str]]:
        if not isinstance(value, list):
            return []
        normalized: list[dict[str, str]] = []
        for item in value[:6]:
            if isinstance(item, str):
                normalized.append(
                    {"text": item, "category": "growth", "impact": "medium", "effort": "medium"}
                )
            elif isinstance(item, dict):
                normalized.append(
                    {
                        "text": str(item.get("text") or item.get("recommendation") or ""),
                        "category": str(item.get("category") or "growth"),
                        "impact": str(item.get("impact") or "medium"),
                        "effort": str(item.get("effort") or "medium"),
                    }
                )
        return [item for item in normalized if item["text"]]
