"""Контейнер зависимостей для управления синглтонами приложения."""

from typing import TYPE_CHECKING

from src.app.domain.constants import LOGGER_NAME
from src.app.infrastructure.adapters.logger.structlog_logger import StructlogLogger
from src.app.infrastructure.config import get_settings

if TYPE_CHECKING:
    from src.app.application.ports.logger import Logger


settings = get_settings()


class AppContainer:
    """Контейнер синглтонов приложения.

    Служит для централизованного хранения и предоставления зависимостей.
    """

    @classmethod
    def logger(cls) -> 'Logger':
        """Возвращает синглтон логгера приложения.

        Returns:
            Экземпляр Logger.
        """
        return StructlogLogger(name=LOGGER_NAME)
