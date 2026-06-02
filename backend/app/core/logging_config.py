"""Application-wide logging configuration."""

import logging
import sys

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    level = logging.DEBUG if settings.app_debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
