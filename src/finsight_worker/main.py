"""Точка входа для приложения finsight_worker.

Загружает зависимости, настраивает Celery и импортирует задачи.
"""

from src.finsight_worker.infrastructure.config import Settings
from src.finsight_worker.infrastructure.container import WorkerContainer
from src.finsight_worker.infrastructure.tasks import download_historical_data
from src.finsight_worker.worker import create_celery_app

settings = Settings()
container = WorkerContainer()
container.config.from_pydantic(settings)

celery_app = create_celery_app(settings)

download_historical_data.register_tasks(celery_app)

__all__ = ['celery_app']
