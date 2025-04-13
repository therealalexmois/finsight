"""Контейнер зависимостей для управления синглтонами приложения."""

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

from src.app.domain.constants import LOGGER_NAME
from src.app.infrastructure.adapters.logger.structlog_logger import StructlogLogger
from src.app.infrastructure.adapters.tinkoff.client import TinkoffInvestApiClient
from src.app.infrastructure.adapters.tinkoff.factories import (
    async_client_factory as async_tinkoff_api_client_factory,
)

if TYPE_CHECKING:
    from src.app.application.ports.gateways.tinkoff_gateway import TinkoffInvestGateway
    from src.app.application.ports.logger import Logger
    from src.app.infrastructure.adapters.tinkoff.client import AsyncClientFactory


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

    tinkoff_api_token = providers.Callable(lambda c: c['tinkoff_invest_api']['token'].get_secret_value(), config)

    tinkoff_client_factory = providers.Factory(
        async_client_factory,
        token=tinkoff_api_token,
    )

    tinkoff_invest_gateway: 'providers.Provider[TinkoffInvestGateway]' = providers.Singleton(
        TinkoffInvestApiClient,
        token=tinkoff_api_token,
        logger=logger,
        client_factory=tinkoff_client_factory,
    )
