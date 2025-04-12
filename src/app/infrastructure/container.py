"""Контейнер зависимостей для управления синглтонами приложения."""

from dependency_injector import containers, providers

from src.app.domain.constants import LOGGER_NAME
from src.app.infrastructure.adapters.logger.structlog_logger import StructlogLogger


class AppContainer(containers.DeclarativeContainer):
    """Контейнер централизованного хранения и предоставления зависимостей приложения."""

    config = providers.Configuration()
    # settings: providers.Provider[Settings] = providers.Singleton(Settings)
    logger: providers.Provider[StructlogLogger] = providers.Singleton(StructlogLogger, name=LOGGER_NAME)
