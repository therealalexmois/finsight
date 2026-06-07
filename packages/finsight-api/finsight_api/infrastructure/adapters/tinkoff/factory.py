"""Фабрики для создания асинхронных клиентов Tinkoff Invest API.

Содержит стандартную реализацию фабрики `async_client_factory`, которая создаёт
экземпляры клиента `AsyncClient` из официального SDK. Эта фабрика используется
адаптером `TinkoffInvestAdapter` по умолчанию, но может быть переопределена в
тестах или кастомных конфигурациях.

Фабрика — асинхронный контекстный менеджер, отдающий объект, реализующий интерфейс
`AsyncServices`.

Examples:
    async with async_client_factory(token) as client:
        await client.users.get_accounts()
"""

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from t_tech.invest import AsyncClient

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from t_tech.invest.async_services import AsyncServices


@asynccontextmanager
async def async_client_factory(token: str) -> 'AsyncGenerator[AsyncServices]':
    """Создаёт сессию клиента Tinkoff Invest API.

    Args:
        token: Токен авторизации в Tinkoff Invest API.

    Yields:
        Экземпляр клиента AsyncClient, реализующий интерфейс AsyncServices.
    """
    async with AsyncClient(token) as client:
        yield client
