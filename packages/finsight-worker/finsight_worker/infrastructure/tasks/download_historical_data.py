"""Фоновая задача для загрузки исторических рыночных данных."""

from datetime import date
from typing import TYPE_CHECKING

from finsight_worker.application.use_cases.download_historical_data import (
    DownloadHistoricalDataInputDto,
    DownloadHistoricalDataUseCase,
)
from finsight_worker.domain.value_objects import CandleInterval
from finsight_worker.infrastructure.container import WorkerContainer

if TYPE_CHECKING:
    from celery import Celery

container = WorkerContainer()


def register_tasks(app: 'Celery') -> None:
    """Регистрирует в Celery задачу download_historical_data.

    Args:
        app: Экземпляр Celery, в котором регистрируется задача.
    """
    app.task(name='download_historical_data')(download_historical_data_task)


def download_historical_data_task(
    isin: str,
    from_date: str,
    to_date: str,
    interval: CandleInterval = CandleInterval.DAY,
) -> None:
    """Celery-задача загрузки исторических данных по инструменту.

    Собирает зависимости из контейнера, парсит даты из ISO-формата и запускает
    DownloadHistoricalDataUseCase.

    Args:
        isin: ISIN инструмента.
        from_date: Начальная дата в формате YYYY-MM-DD.
        to_date: Конечная дата в формате YYYY-MM-DD.
        interval: Интервал между свечами (по умолчанию "day").
    """
    use_case = DownloadHistoricalDataUseCase(
        market_data_gateway=container.market_data_gateway(),
        logger=container.logger(),
    )

    use_case.execute(
        DownloadHistoricalDataInputDto(
            isin=isin,
            from_date=date.fromisoformat(from_date),
            to_date=date.fromisoformat(to_date),
            interval=interval,
        )
    )
