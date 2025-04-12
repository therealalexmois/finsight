"""Общие фикстуры pytest для интеграционного тестирования."""

from typing import TYPE_CHECKING

import pytest
from httpx import ASGITransport, AsyncClient

from src.app.infrastructure.container import AppContainer
from src.app.presentation.webserver.app_factory import AppFactory

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from fastapi import FastAPI


@pytest.fixture
def fastapi_app() -> 'FastAPI':
    """Предоставляет экземпляр приложения FastAPI для тестирования."""
    config = AppContainer.config()

    app_factory = AppFactory(config)

    return app_factory.create_app()


@pytest.fixture
async def async_api_client(fastapi_app: 'FastAPI') -> 'AsyncGenerator[AsyncClient]':
    """Клиент Async API - для параллельных/асинхронных интеграционных тестов."""
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url='http://test') as client:
        yield client
