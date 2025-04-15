"""Контейнер зависимостей для управления синглтонами приложения."""

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

from src.finsight_api.domain.constants import LOGGER_NAME
from src.finsight_api.infrastructure.adapters.logger.structlog_logger import StructlogLogger
from src.finsight_api.infrastructure.adapters.tinkoff.client_factory import (
    async_client_factory as async_tinkoff_api_client_factory,
)
from src.finsight_api.infrastructure.adapters.tinkoff.invest_client import TinkoffInvestApiClient

if TYPE_CHECKING:
    from src.finsight_api.application.ports.gateways.tinkoff_gateway import TinkoffInvestGateway
    from src.finsight_api.application.ports.logger import Logger
    from src.finsight_api.infrastructure.adapters.tinkoff.invest_client import AsyncClientFactory


def async_client_factory(token: str) -> 'AsyncClientFactory':
    """Фабрика, возвращающая функцию создания клиента Tinkoff API."""
    return lambda: async_tinkoff_api_client_factory(token)


class AppContainer(containers.DeclarativeContainer):
    """Контейнер централизованного хранения и предоставления зависимостей приложения."""

    config = providers.Configuration()

    logger: 'providers.Provider[Logger]' = providers.Factory(
        StructlogLogger,
        name=LOGGER_NAME,
    )

    tinkoff_client_factory = providers.Factory(
        async_client_factory,
        token=config.tinkoff_invest_api.token,
    )

    tinkoff_invest_gateway: 'providers.Provider[TinkoffInvestGateway]' = providers.Singleton(
        TinkoffInvestApiClient,
        token=config.tinkoff_invest_api.token,
        logger=logger,
        client_factory=tinkoff_client_factory,
    )
