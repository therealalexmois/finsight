"""Модуль для создания и настройки FastAPI приложения."""

from itertools import chain
from typing import TYPE_CHECKING

from fastapi import FastAPI

from finsight_api.domain.exceptions import BaseAppError
from finsight_api.presentation.rest.public.v1.router import api_v1_router
from finsight_api.presentation.rest.system.router import system_router
from finsight_api.presentation.webserver.error_handler import base_app_error_handler, validation_error_handler
from finsight_api.presentation.webserver.middlewares.request_id import RequestIDMiddleware
from finsight_api.presentation.webserver.middlewares.request_logging import RequestLoggingMiddleware

if TYPE_CHECKING:
    from finsight_api.infrastructure.config import Settings


class AppFactory:
    """Фабрика для создания и настройки экземпляра FastAPI приложения."""

    def __init__(self, settings: 'Settings') -> None:
        """Инициализирует фабрику заданными настройками приложения.

        Args:
            settings: Объект настроек для конфигурации приложения.
        """
        self.settings = settings

    def create_app(self) -> FastAPI:
        """Создает и настраивает экземпляр FastAPI-приложения.

        Returns:
            Объект FastAPI с подключёнными маршрутами.
        """
        app = FastAPI(
            docs_url=None,
            redoc_url='/',
            title=self.settings.app.name,
            version=self.settings.app.version,
            description=self.settings.app.description,
            debug=self.settings.app.debug,
        )

        for router in chain([system_router, api_v1_router]):
            app.include_router(router)

        exception_handlers = [
            (BaseAppError, base_app_error_handler),
            (Exception, validation_error_handler),
        ]

        for exc_type, handler in chain(exception_handlers):
            app.add_exception_handler(exc_type, handler)

        exclude_urls_from_logging = frozenset({'/health', '/metrics'})

        app.add_middleware(RequestLoggingMiddleware, exclude_urls_from_logging=exclude_urls_from_logging)
        app.add_middleware(RequestIDMiddleware)

        return app
