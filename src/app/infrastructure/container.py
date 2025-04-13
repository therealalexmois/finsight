"""Контtinkoff_invest_gatewayейнер зависимостей для управления синглтонами приложения."""

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

from src.app.domain.constants import LOGGER_NAME
from src.app.infrastructure.adapters.logger.structlog_logger import StructlogLogger
from src.app.infrastructure.adapters.tinkoff.client import TinkoffInvestApiClient

if TYPE_CHECKING:
    from src.app.application.ports.gateways.tinkoff_gateway import TinkoffInvestGateway
    from src.app.application.ports.logger import Logger


class AppContainer(containers.DeclarativeContainer):
    """Контейнер централизованного хранения и предоставления зависимостей приложения."""

    config = providers.Configuration()

    logger: 'providers.Provider[Logger]' = providers.Factory(
        StructlogLogger,
        name=LOGGER_NAME,
    )

    tinkoff_invest_gateway: 'providers.Provider[TinkoffInvestGateway]' = providers.Singleton(
        TinkoffInvestApiClient,
        token=providers.Callable(lambda c: c['tinkoff_invest_api']['token'].get_secret_value(), config),
        logger=logger,
    )
