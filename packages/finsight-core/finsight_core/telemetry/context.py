"""Контекст запроса для structlog: хранение и доступ к X-Request-ID.

Общий модуль для сервисов FinSight. Хранит идентификатор запроса в ContextVar,
доступный на всём протяжении обработки запроса.
"""

import uuid
from contextvars import ContextVar
from typing import Final, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from fastapi import Request

_request_id_ctx: ContextVar[str | None] = ContextVar('request_id_ctx', default=None)

DEFAULT_REQUEST_ID_HEADER: Final[str] = 'X-Request-ID'


def extract_request_id(request: 'Request') -> str | None:
    """Извлекает идентификатор запроса из заголовка X-Request-ID.

    Args:
        request: Входящий HTTP-запрос.

    Returns:
        Значение X-Request-ID из заголовков или None, если заголовок не передан.
    """
    return request.headers.get(DEFAULT_REQUEST_ID_HEADER)


def set_request_id(
    value: str | None = None,
    request_id_generator: 'Callable[[], str] | None' = None,
) -> str:
    """Устанавливает идентификатор запроса в контекст переменных.

    Args:
        value: Явно переданный идентификатор запроса. Если None — генерируется автоматически.
        request_id_generator: Функция генерации request_id. По умолчанию — UUID4-генератор.

    Returns:
        Установленное значение идентификатора запроса.
    """
    generator = request_id_generator or _default_generator
    request_id = value or generator()
    _request_id_ctx.set(request_id)
    return request_id


def get_request_id() -> str | None:
    """Возвращает текущий X-Request-ID из контекста выполнения.

    Returns:
        Идентификатор запроса или None, если он ещё не установлен.
    """
    return _request_id_ctx.get()


def _default_generator() -> str:
    """Генерирует уникальный идентификатор запроса (UUID4).

    Returns:
        Сгенерированный уникальный идентификатор запроса.
    """
    return str(uuid.uuid4())
