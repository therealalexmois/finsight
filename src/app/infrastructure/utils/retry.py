"""Утилиты для повторных попыток вызова внешних API (только для async функций)."""

import asyncio
import functools
import logging
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')


def retry_on_exception(
    retry_count: int = 5,
    delay_seconds: float = 0.5,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    logger: logging.Logger | None = None,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Декоратор с повторными попытками при ошибках внешнего API для async-функций.

    Args:
        retry_count: Количество попыток.
        delay_seconds: Начальная задержка между попытками.
        backoff_factor: Множитель для экспоненциальной задержки.
        exceptions: Ошибки, при которых будет выполнен повтор.
        logger: Логгер для вывода информации о повторах. Если не указан, используется стандартный логгер.

    Returns:
        Обёртка с реализацией повторных попыток при ошибках вызываемой асинхронной функции.
    """
    log = logger or logging.getLogger(__name__)

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        if not hasattr(func, '__name__') or not hasattr(func, '__code__') or not asyncio.iscoroutinefunction(func):
            raise TypeError('retry_on_exception поддерживает только асинхронные функции')

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if retry_count < 1:
                return await func(*args, **kwargs)

            current_attempt = 1
            delay_time = delay_seconds

            while current_attempt <= retry_count:
                try:
                    return await func(*args, **kwargs)
                except exceptions as exc:
                    log.warning(f'Попытка {current_attempt}/{retry_count} завершилась ошибкой: {exc!r}')
                    if current_attempt == retry_count:
                        raise exc
                    await asyncio.sleep(delay_time)
                    delay_time *= backoff_factor
                    current_attempt += 1

            raise RuntimeError('Unreachable code in retry_on_exception wrapper')

        return wrapper

    return decorator
