"""Реализация интерфейса логгера с использованием библиотеки structlog."""

from typing import TYPE_CHECKING

import structlog

from src.app.application.ports.logger import Logger

if TYPE_CHECKING:
    from typing import Any


class StructlogLogger(Logger):
    """Логгер, реализующий интерфейс Logger через structlog."""

    def __init__(self, name: str) -> None:
        """Инициализирует экземпляр structlog логгера.

        Args:
            name: Имя логгера.
        """
        self._logger = structlog.get_logger(name)

    def info(self, event: str, **kwargs: 'Any') -> None:
        """Логгирует информационное сообщение.

        Args:
            event: Название события.
            **kwargs: Дополнительные параметры события.
        """
        self._logger.info(event, **kwargs)

    def warning(self, event: str, **kwargs: 'Any') -> None:
        """Логгирует предупреждающее сообщение.

        Args:
            event: Название события.
            **kwargs: Дополнительные параметры события.
        """
        self._logger.warning(event, **kwargs)

    def error(self, event: str, **kwargs: 'Any') -> None:
        """Логгирует сообщение об ошибке.

        Args:
            event: Название события.
            **kwargs: Дополнительные параметры события.
        """
        self._logger.error(event, **kwargs)

    def clear_context_vars(self) -> None:
        """Очищает все привязанные контекстные переменные."""
        structlog.contextvars.clear_contextvars()

    def bind_context_vars(self, **kwargs: 'Any') -> None:
        """Добавляет переменные в контекст логгера."""
        structlog.contextvars.bind_contextvars(**kwargs)

    def unbind_context_vars(self, *keys: str) -> None:
        """Удаляет переменные из контекста логгера по ключам."""
        structlog.contextvars.unbind_contextvars(*keys)
