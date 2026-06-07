"""Константы, используемые в веб-сервере FastAPI."""

from typing import Final  # noqa: TC003

DEFAULT_DISABLED_LOGGER_NAMES: Final[frozenset[str]] = frozenset(['uvicorn.access'])
