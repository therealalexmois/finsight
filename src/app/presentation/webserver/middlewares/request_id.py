"""Middleware для привязки X-Request-ID и установки контекста логгера."""

from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware

from src.app.infrastructure.adapters.logger.context import (
    DEFAULT_REQUEST_ID_HEADER,
    extract_request_id,
    set_request_id,
)

if TYPE_CHECKING:
    from starlette.middleware.base import RequestResponseEndpoint
    from starlette.requests import Request
    from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления X-Request-ID и установки контекста структурированного логгера.

    Этот middleware извлекает идентификатор запроса из входящего HTTP-запроса,
    устанавливает его с помощью функции set_request_id, а затем добавляет его в качестве заголовка
    в ответ.

    Args:
        None.
    """

    async def dispatch(self, request: 'Request', call_next: 'RequestResponseEndpoint') -> 'Response':
        """Обрабатывает входящий запрос, добавляя в ответ заголовок X-Request-ID.

        Args:
            request: Входящий HTTP-запрос.
            call_next: Функция вызова следующего middleware/обработчика запроса.

        Returns:
            Response: HTTP-ответ с добавленным заголовком X-Request-ID.
        """
        request_id = extract_request_id(request)
        request_id = set_request_id(request_id)
        response = await call_next(request)
        response.headers[DEFAULT_REQUEST_ID_HEADER] = request_id
        return response
