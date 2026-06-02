"""Application-specific exceptions."""

from dataclasses import dataclass


@dataclass
class AppError(Exception):
    message: str
    code: str = "app_error"


class EventValidationError(AppError):
    """Raised when event payload fails validation before persistence."""

    def __init__(self, message: str, code: str = "validation_error") -> None:
        super().__init__(message=message, code=code)


class ResourceNotFoundError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="not_found")
