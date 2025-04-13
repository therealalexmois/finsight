"""Фабрики для создания асинхронных клиентов Tinkoff Invest API.

Содержит стандартную реализацию фабрики `default_async_client_factory`,
которая создает экземпляры клиента `AsyncClient` из официального SDK.
Эта фабрика используется адаптером `TinkoffInvestApiClient` по умолчанию,
но может быть переопределена в тестах или кастомных конфигурациях.

Пример использования:
    async with default_async_client_factory(token) as client:
        await client.users.get_accounts()

Фабрика возвращает объект, реализующий интерфейс `AsyncServices`.
"""

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from tinkoff.invest import AsyncClient

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from tinkoff.invest.async_services import AsyncServices


@asynccontextmanager
async def async_client_factory(token: str) -> 'AsyncGenerator[AsyncServices]':
    """Создаёт сессию клиента Tinkoff Invest API.

    Yields:
        Экземпляр клиента AsyncClient, реализующий интерфейс AsyncServices.
    """
    async with AsyncClient(token) as client:
        yield client
