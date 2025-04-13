"""Юнит-тесты для декоратора retry_on_exception (async версии)."""

from typing import TYPE_CHECKING

import pytest

from src.app.infrastructure.utils.retry import retry_on_exception

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.mark.asyncio
class TestRetryOnException:
    RETRY_COUNT = 3
    DELAY_SECONDS = 0.01
    BACKOFF_FACTOR = 2.0

    async def test_retry_on_exception__should_succeed_after_retry(self, mocker: 'MockerFixture') -> None:
        """Должен выполнить функцию повторно и успешно при ошибке на первых попытках."""
        call_tracker = {'count': 0}

        async def flaky_func() -> str:
            call_tracker['count'] += 1
            if call_tracker['count'] < TestRetryOnException.RETRY_COUNT:
                raise ValueError('Temporary error')
            return 'success'

        logger = mocker.Mock()
        decorated = retry_on_exception(
            retry_count=TestRetryOnException.RETRY_COUNT,
            delay_seconds=TestRetryOnException.DELAY_SECONDS,
            backoff_factor=TestRetryOnException.BACKOFF_FACTOR,
            exceptions=(ValueError,),
            logger=logger,
        )(flaky_func)

        result = await decorated()
        assert result == 'success'
        assert call_tracker['count'] == TestRetryOnException.RETRY_COUNT
        # Предполагается, что предупреждения логируются при каждом провале, кроме последней попытки.
        assert logger.warning.call_count == TestRetryOnException.RETRY_COUNT - 1

    async def test_retry_on_exception__should_fail_after_all_retries(self, mocker: 'MockerFixture') -> None:
        """Должен выбрасывать исключение после всех неудачных попыток."""
        logger = mocker.Mock()

        async def always_fail() -> None:
            raise TimeoutError('Persistent failure')

        decorated = retry_on_exception(
            retry_count=TestRetryOnException.RETRY_COUNT,
            delay_seconds=TestRetryOnException.DELAY_SECONDS,
            backoff_factor=TestRetryOnException.BACKOFF_FACTOR,
            exceptions=(TimeoutError,),
            logger=logger,
        )(always_fail)

        with pytest.raises(TimeoutError):
            await decorated()

        # Ожидается RETRY_COUNT вызовов логгера (каждая попытка вызывает warning).
        assert logger.warning.call_count == TestRetryOnException.RETRY_COUNT

    async def test_retry_on_exception__should_not_retry_on_unexpected_exception(self, mocker: 'MockerFixture') -> None:
        """Не должен повторять попытки при исключении, не указанном в exceptions."""
        logger = mocker.Mock()

        async def raise_type_error() -> None:
            raise TypeError('Unexpected error')

        decorated = retry_on_exception(
            retry_count=TestRetryOnException.RETRY_COUNT,
            delay_seconds=TestRetryOnException.DELAY_SECONDS,
            backoff_factor=TestRetryOnException.BACKOFF_FACTOR,
            exceptions=(ValueError,),
            logger=logger,
        )(raise_type_error)

        with pytest.raises(TypeError):
            await decorated()

        assert logger.warning.call_count == 0

    async def test_retry_on_exception__should_not_retry_if_retry_count_is_zero(self, mocker: 'MockerFixture') -> None:
        """Не должен выполнять повторные попытки, если retry_count = 0."""
        logger = mocker.Mock()

        async def fn() -> str:
            return 'done'

        decorated = retry_on_exception(
            retry_count=0,
            delay_seconds=TestRetryOnException.DELAY_SECONDS,
            backoff_factor=TestRetryOnException.BACKOFF_FACTOR,
            exceptions=(Exception,),
            logger=logger,
        )(fn)

        result = await decorated()
        assert result == 'done'
        logger.warning.assert_not_called()

    async def test_retry_on_exception__should_not_retry_if_retry_count_is_zero_async(
        self, mocker: 'MockerFixture'
    ) -> None:
        """Не должен выполнять повторные попытки (async), если retry_count = 0."""
        logger = mocker.Mock()

        async def fn() -> str:
            return 'async done'

        wrapped = retry_on_exception(
            retry_count=0,
            delay_seconds=TestRetryOnException.DELAY_SECONDS,
            backoff_factor=TestRetryOnException.BACKOFF_FACTOR,
            exceptions=(Exception,),
            logger=logger,
        )(fn)

        result = await wrapped()
        assert result == 'async done'
        logger.warning.assert_not_called()
