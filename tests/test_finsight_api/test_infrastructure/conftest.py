"""Фикстуры и поддельные реализации для интеграционного тестирования TinkoffInvestApiClient."""

from contextlib import AbstractAsyncContextManager
from typing import Final, TYPE_CHECKING

import pytest
from grpc import StatusCode
from tinkoff.invest import RequestError

from src.finsight_api.infrastructure.adapters.logger.structlog_logger import StructlogLogger

if TYPE_CHECKING:
    import types
    from collections.abc import Callable

    from tinkoff.invest.async_services import AsyncServices

    from src.finsight_api.application.ports.logger import Logger


_TRANSIENT_FAIL_ATTEMPTS: Final[int] = 2


class FakeAccounts:
    accounts = [type('FakeAccount', (), {'id': 'test_acc'})()]


class FakeUsers:
    async def get_accounts(self) -> FakeAccounts:
        """Возвращает фиктивный результат."""
        return FakeAccounts()


class FakeClient:
    """Поддельный клиент Tinkoff Invest API для тестирования.

    Имитирует поведение клиента SDK с методом users.get_accounts(),
    который всегда выбрасывает исключение RequestError.
    """

    users: FakeUsers

    async def __aenter__(self) -> 'FakeClient':
        """Поддерживает асинхронный контекстный менеджер.

        Returns:
            Экземпляр FakeClient.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: 'types.TracebackType | None',
    ) -> None:
        """Завершает работу асинхронного контекстного менеджера.

        Args:
            exc_type: Тип исключения (если произошло).
            exc: Само исключение (если было).
            tb: Трассировка стека (если была).
        """
        pass


@pytest.fixture
def fake_session_failure() -> 'Callable[[], AbstractAsyncContextManager[AsyncServices]]':
    """Возвращает сессию клиента, которая всегда выбрасывает RequestError."""

    class FailureClient(FakeClient):
        users = FakeUsers()

    class FailureContextManager(AbstractAsyncContextManager['AsyncServices']):
        async def __aenter__(self) -> 'AsyncServices':
            return FailureClient()  # type: ignore[return-value]

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: 'types.TracebackType | None',
        ) -> None:
            pass

    return lambda: FailureContextManager()


@pytest.fixture
def fake_session_transient_success() -> 'Callable[[], AbstractAsyncContextManager[AsyncServices]]':
    """Сессия, которая дважды выбрасывает RequestError, а затем успешно возвращает данные.

    Возвращает фабрику контекстного менеджера, соответствующего интерфейсу AsyncServices.
    """
    call_counter = {'count': 0}

    class TransientFakeUsers(FakeUsers):
        async def get_accounts(self) -> FakeAccounts:
            call_counter['count'] += 1
            if call_counter['count'] <= _TRANSIENT_FAIL_ATTEMPTS:
                raise RequestError(
                    code=StatusCode.UNAVAILABLE,
                    details='Transient error',
                    metadata=None,
                )
            return FakeAccounts()

    class TransientFakeClient(FakeClient):
        users = TransientFakeUsers()

    class TransientContextManager(AbstractAsyncContextManager['AsyncServices']):
        async def __aenter__(self) -> 'AsyncServices':
            return TransientFakeClient()  # type: ignore[return-value]

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: 'types.TracebackType | None',
        ) -> None:
            pass

    return lambda: TransientContextManager()


@pytest.fixture
def dummy_logger() -> 'Logger':
    """Возвращает простой логгер Structlog без конфигурации — для подмены в тестах.

    Returns:
        Экземпляр логгера, реализующий интерфейс Logger.
    """
    return StructlogLogger(name='dummy-test-logger')
