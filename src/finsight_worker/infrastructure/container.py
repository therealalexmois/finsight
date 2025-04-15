"""Контейнер зависимостей для finsight_worker."""

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

from src.finsight_worker.domain.constants import LOGGER_NAME
from src.finsight_worker.infrastructure.adapters.logger.structlog_logger import StructlogLogger

if TYPE_CHECKING:
    from src.finsight_worker.application.ports.logger import Logger


class WorkerContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей воркера."""

    config = providers.Configuration()

    logger: 'providers.Provider[Logger]' = providers.Factory(
        StructlogLogger,
        name=LOGGER_NAME,
    )
