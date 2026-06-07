"""Контейнер зависимостей приложения."""

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

from finsight_api.infrastructure.adapters.telemetry.logger import StructlogLogger
from finsight_api.infrastructure.adapters.tinkoff.adapter import TinkoffInvestAdapter
from finsight_api.infrastructure.adapters.tinkoff.factory import (
    async_client_factory as async_tinkoff_api_client_factory,
)
from finsight_api.infrastructure.config import Settings

if TYPE_CHECKING:
    from finsight_api.application.ports.logger import LoggerPort
    from finsight_api.application.ports.tinkoff import TinkoffInvestPort
    from finsight_api.infrastructure.adapters.tinkoff.adapter import AsyncClientFactory


def async_client_factory(token: str) -> 'AsyncClientFactory':
    """Возвращает фабрику без аргументов, открывающую сессию клиента Tinkoff API.

    Замыкает переданный токен, чтобы адаптеру не нужно было знать о нём при создании
    клиента.

    Args:
        token: Токен авторизации в Tinkoff Invest API.

    Returns:
        Вызываемый объект, возвращающий асинхронный контекстный менеджер клиента.
    """
    return lambda: async_tinkoff_api_client_factory(token)


class AppContainer(containers.DeclarativeContainer):
    """DI-контейнер приложения finsight_api.

    Attributes:
        settings: Singleton настроек приложения (Settings).
        logger: Factory логгера StructlogLogger, реализующего LoggerPort.
        tinkoff_client_factory: Factory фабрики async-клиента Tinkoff с подставленным токеном.
        tinkoff_invest: Singleton адаптера TinkoffInvestAdapter (порт TinkoffInvestPort).
    """

    settings = providers.Singleton(Settings)

    logger: 'providers.Provider[LoggerPort]' = providers.Factory(
        StructlogLogger,
        app_name=settings.provided.app.name,
        app_version=settings.provided.app.version,
        app_env=settings.provided.app.env,
        app_instance=settings.provided.app.host,
        log_level=settings.provided.logging.log_level,
    )

    tinkoff_client_factory = providers.Factory(
        async_client_factory,
        token=settings.provided.tinkoff_invest_api.token,
    )

    tinkoff_invest: 'providers.Provider[TinkoffInvestPort]' = providers.Singleton(
        TinkoffInvestAdapter,
        token=settings.provided.tinkoff_invest_api.token,
        logger=logger,
        client_factory=tinkoff_client_factory,
    )


app_container = AppContainer()
