"""Middleware для логирования завершения HTTP-запроса.

Этот middleware логирует окончание HTTP-запроса с указанием времени обработки, статуса,
метода, версии HTTP и полного URL, включая строку запроса.
"""

import time
import urllib.parse
from collections.abc import MutableMapping
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.app.infrastructure.container import AppContainer

if TYPE_CHECKING:
    from typing import Any

    from starlette.requests import Request
    from starlette.responses import Response
    from starlette.types import ASGIApp


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования завершения HTTP-запроса.

    Логирует окончание HTTP-запроса, включая время обработки, HTTP-метод, версию HTTP,
    статус-код и URL запроса.

    Attributes:
        exclude_urls_from_logging: Множество URL, которые исключены из логирования.
    """

    def __init__(self, app: 'ASGIApp', exclude_urls_from_logging: frozenset[str] = frozenset()) -> None:
        """Инициализирует middleware для логирования запросов.

        Args:
            app: Объект приложения ASGI.
            exclude_urls_from_logging: Множество URL для исключения из логирования.
        """
        super().__init__(app)
        self.exclude_urls_from_logging: frozenset[str] = exclude_urls_from_logging

    @staticmethod
    def get_path_with_query_string(scope: 'MutableMapping[str, Any]') -> str:
        """Возвращает полный путь к запрашиваемому ресурсу, включая параметры URL.

        Args:
            scope: Словарь с информацией о запросе.

        Returns:
            Строка с путем и строкой запроса.
        """
        path_with_query_string: str = urllib.parse.quote(scope['path'])

        if query := scope.get('query_string'):
            decoded = query.decode('ascii')
            path_with_query_string = f'{path_with_query_string}?{decoded}'

        return path_with_query_string

    async def dispatch(self, request: 'Request', call_next: 'RequestResponseEndpoint') -> 'Response':
        """Обрабатывает входящий запрос, логируя его завершение с HTTP-статусом.

        Args:
            request: Входящий HTTP-запрос.
            call_next: Функция передачи запроса следующему обработчику.

        Returns:
            Response: HTTP-ответ с логированием времени выполнения.
        """
        logger = AppContainer.logger()
        start_time = time.perf_counter_ns()
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            logger.error('unhandled_exception', error=str(exc))
            raise
        finally:
            elapsed_time: int = (time.perf_counter_ns() - start_time) // 1_000_000
            status_code: int = response.status_code if 'response' in locals() else 500
            host: str | None = request.client.host if request.client else None
            url: str = self.get_path_with_query_string(request.scope)
            http_method: str = request.method
            http_version: str = request.scope.get('http_version', '')

            if url not in self.exclude_urls_from_logging:
                logger.info(
                    f'{host} - {http_method} {url} HTTP/{http_version} {status_code}',
                    elapsed_time=elapsed_time,
                    client={'host': host},
                    http={
                        'method': http_method,
                        'status_code': status_code,
                        'version': http_version,
                        'url': url,
                    },
                )

        return response
