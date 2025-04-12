"""Точка входа в приложение. Настраивает и запускает сервер."""

import os
import pathlib
from typing import TYPE_CHECKING

import uvicorn
from dependency_injector.wiring import inject, Provide

from src.app.infrastructure.adapters.logger.logging import configure_logging
from src.app.infrastructure.config import Settings
from src.app.infrastructure.container import AppContainer
from src.app.presentation.webserver.app_factory import AppFactory

if TYPE_CHECKING:
    from fastapi import FastAPI


@inject
def create_app(config: Settings = Provide[AppContainer.config]) -> 'FastAPI':
    """Создает экземпляр FastAPI-приложения.

    Аргументы:
        config: Конфигурация приложения, автоматически внедряемая из контейнера.

    Returns:
        Объект FastAPI с подключёнными маршрутами.
    """
    app = AppFactory(config).create_app()

    return app


def start_app() -> None:
    """Запускает приложение с помощью uvicorn."""
    settings = Settings()
    app_container = AppContainer()
    app_container.config.from_pydantic(settings)
    app_container.wire(modules=[__name__])

    configure_logging(
        app_name=settings.app.name,
        app_version=settings.app.version,
        env=settings.app.env,
        instance=settings.app.host,
        log_level=settings.logging.log_level,
    )

    logger = app_container.logger()

    current_dir = str(pathlib.Path.cwd())

    logger.info('Will watch for changes in these directories', extra={'directories': [current_dir]})
    logger.info(f'Uvicorn running on http://{settings.app.host}:{settings.app.port} (Press CTRL+C to quit)')
    logger.info('Started reloader process', extra={'pid': os.getpid(), 'reloader': 'StatReload'})

    uvicorn.run(
        'src.app.create_app',
        host=settings.app.host,
        port=settings.app.port,
        # TODO: Вынести в конфиг
        access_log=False,
        log_config=None,
        log_level=settings.logging.log_level.value,
        reload=settings.app.reload,
    )


if __name__ == '__main__':
    start_app()
