"""Создание и конфигурация приложения."""

from typing import TYPE_CHECKING

from celery import Celery

from finsight_worker.infrastructure.adapters.logger.logging import configure_logging

if TYPE_CHECKING:
    from finsight_worker.infrastructure.config import Settings


def create_celery_app(settings: 'Settings') -> 'Celery':
    """Создаёт и настраивает экземпляр Celery.

    Настраивает логирование по параметрам воркера и создаёт Celery с Redis в роли
    брокера и backend и JSON-сериализацией задач.

    Args:
        settings: Настройки воркера (имя, версия, окружение, Redis, логирование).

    Returns:
        Сконфигурированный экземпляр Celery.
    """
    configure_logging(
        app_name=settings.worker.name,
        app_version=settings.worker.version,
        env=settings.worker.env,
        instance=settings.worker.host,
        log_level=settings.logging.log_level,
    )

    app = Celery(
        main=settings.worker.name,
        broker=settings.redis.broker_url,
        backend=settings.redis.result_backend,
        task_track_started=True,
        task_serializer='json',
    )

    app.conf.update(
        result_serializer='json',
        accept_content=['json'],
        timezone='UTC',
        enable_utc=True,
    )

    return app
