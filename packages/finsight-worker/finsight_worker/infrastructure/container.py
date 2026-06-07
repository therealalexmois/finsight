"""Контейнер зависимостей для finsight_worker."""

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

from finsight_worker.domain.constants import LOGGER_NAME
from finsight_worker.infrastructure.adapters.logger.structlog_logger import StructlogLogger

if TYPE_CHECKING:
    from finsight_worker.application.ports.logger import Logger


class WorkerContainer(containers.DeclarativeContainer):
    """DI-контейнер воркера.

    Собирает конфигурацию и провайдеры зависимостей (логгер на основе structlog).

    Attributes:
        config: Провайдер конфигурации воркера.
        logger: Провайдер логгера StructlogLogger.
    """

    config = providers.Configuration()

    logger: 'providers.Provider[Logger]' = providers.Factory(
        StructlogLogger,
        name=LOGGER_NAME,
    )
