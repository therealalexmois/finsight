"""Модуль для создания и настройки FastAPI приложения."""

from itertools import chain
from typing import TYPE_CHECKING

from fastapi import FastAPI

from src.app.domain.exceptions import BaseAppError
from src.app.presentation.api.system.router import system_router
from src.app.presentation.webserver.exceptions import base_app_error_handler, validation_error_handler
from src.app.presentation.webserver.middlewares.request_id import RequestIDMiddleware
from src.app.presentation.webserver.middlewares.request_logging import RequestLoggingMiddleware

if TYPE_CHECKING:
    from src.app.infrastructure.config import Settings


class AppFactory:
    """Фабрика для создания и настройки экземпляра FastAPI приложения."""

    def __init__(self, settings: 'Settings') -> None:
        """Инициализирует фабрику с заданными настройками и зависимостями.

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

        for router in chain([system_router]):
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
