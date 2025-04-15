"""Use case для загрузки исторических рыночных данных."""

from typing import TYPE_CHECKING

from src.finsight_worker.domain.models import HistoricalDataRequest
from src.finsight_worker.domain.value_objects import CandleInterval

if TYPE_CHECKING:
    from datetime import date

    from src.finsight_worker.application.ports.gateway import MarketDataGateway
    from src.finsight_worker.application.ports.logger import Logger


class DownloadHistoricalDataUseCase:
    """Сценарий использования: загрузка исторических рыночных данных."""

    def __init__(self, market_data_gateway: 'MarketDataGateway', logger: 'Logger') -> None:
        """Инициализирует use case для загрузки исторических данных.

        Args:
            market_data_gateway: Интерфейс для получения рыночных данных.
            logger: Интерфейс для логирования действий use case.
        """
        self._market_data_gateway = market_data_gateway
        self._logger = logger

    def execute(
        self,
        isin: str,
        from_date: 'date',
        to_date: 'date',
        interval: CandleInterval = CandleInterval.DAY,
    ) -> None:
        """Выполняет загрузку исторических данных по заданному инструменту.

        Args:
            isin: Идентификатор инструмента (ISIN).
            from_date: Дата начала периода.
            to_date: Дата конца периода.
            interval: Интервал между свечами (например, 'day', 'hour').
        """
        self._logger.info(
            'Запуск загрузки исторических данных',
            extra={
                'isin': isin,
                'from_date': from_date.isoformat(),
                'to_date': to_date.isoformat(),
                'interval': interval,
            },
        )

        request = HistoricalDataRequest(
            isin=isin,
            from_date=from_date,
            to_date=to_date,
            interval=interval,
        )

        candles = self._market_data_gateway.download_candles(request)

        self._logger.info('Загрузка завершена', extra={'count': len(candles)})
