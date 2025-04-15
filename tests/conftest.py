"""Общие фикстуры pytest для интеграционного тестирования.

Содержит фикстуры для:
- глобальных настроек приложения;
- создания экземпляра FastAPI-приложения;
- асинхронного клиента HTTP API;
- клиента для работы с Tinkoff Invest API.
"""

from typing import Final, TYPE_CHECKING

import pytest
from httpx import ASGITransport, AsyncClient

from src.finsight_api.infrastructure.config import Settings
from src.finsight_api.infrastructure.container import AppContainer
from src.finsight_api.presentation.webserver.app_factory import AppFactory

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from fastapi import FastAPI

    from src.finsight_api.application.ports.gateways.tinkoff_gateway import TinkoffInvestGateway


TEST_API_BASE_URL: Final[str] = 'http://test'


@pytest.fixture(scope='session')
def settings() -> 'Settings':
    """Возвращает глобальные настройки приложения.

    Читает настройки из конфигурационного класса `Settings` и
    инициализирует контейнер зависимостей.
    """
    settings = Settings()
    return settings


@pytest.fixture(scope='session')
def app_container(settings: 'Settings') -> AppContainer:
    """Создаёт и конфигурирует контейнер зависимостей приложения.

    Args:
        settings: Конфигурация приложения.

    Returns:
        Инициализированный контейнер зависимостей.
    """
    container = AppContainer()
    container.config.from_pydantic(settings)
    return container


@pytest.fixture
def fastapi_app(settings: 'Settings') -> 'FastAPI':
    """Создаёт и возвращает экземпляр FastAPI-приложения для тестирования.

    Args:
        settings: Настройки приложения.

    Returns:
        Инициализированный экземпляр FastAPI.
    """
    return AppFactory(settings).create_app()


@pytest.fixture
async def api_client(fastapi_app: 'FastAPI', base_url: str = TEST_API_BASE_URL) -> 'AsyncGenerator[AsyncClient]':
    """Асинхронный HTTP клиент для тестирования FastAPI API.

    Использует ASGITransport и позволяет отправлять запросы к тестовому приложению.

    Args:
        fastapi_app: Экземпляр FastAPI.
        base_url: Базовый URL, используемый в httpx-клиенте (по умолчанию 'http://test').

    Yields:
        Асинхронный HTTP-клиент.
    """
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url=base_url) as client:
        yield client


@pytest.fixture(scope='session')
def tinkoff_gateway(app_container: 'AppContainer') -> 'TinkoffInvestGateway':
    """Возвращает клиент Tinkoff Invest API из контейнера зависимостей.

    Используется для интеграционных тестов работы с Tinkoff API.

    Args:
        app_container: Контейнер приложения, с зарегистрированными зависимостями.

    Returns:
        Реализация порта TinkoffInvestGateway.
    """
    return app_container.tinkoff_invest_gateway()
