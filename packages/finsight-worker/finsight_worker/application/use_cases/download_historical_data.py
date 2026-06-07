"""Use case для загрузки исторических рыночных данных."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from finsight_worker.domain.models import HistoricalDataRequest
from finsight_worker.domain.value_objects import CandleInterval

if TYPE_CHECKING:
    from datetime import date

    from finsight_worker.application.ports.gateway import MarketDataGateway
    from finsight_worker.application.ports.logger import Logger


@dataclass(frozen=True, slots=True, kw_only=True, repr=True, eq=False)
class DownloadHistoricalDataInputDto:
    """Входные параметры для загрузки исторических рыночных данных.

    Attributes:
        isin: Идентификатор инструмента (ISIN).
        from_date: Дата начала периода.
        to_date: Дата конца периода.
        interval: Интервал между свечами (например, 'day', 'hour').
    """

    isin: str
    from_date: 'date'
    to_date: 'date'
    interval: CandleInterval = CandleInterval.DAY


class DownloadHistoricalDataUseCase:
    """Сценарий загрузки исторических рыночных данных.

    Принимает параметры инструмента и периода, формирует HistoricalDataRequest,
    запрашивает свечи через MarketDataGateway и логирует начало и успешное
    завершение загрузки.
    """

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
        dto: DownloadHistoricalDataInputDto,
    ) -> None:
        """Загружает исторические свечи по инструменту и логирует ход операции.

        Формирует запрос из DTO, получает свечи через gateway и пишет события
        начала и успешного завершения с количеством загруженных свечей.

        Args:
            dto: Инструмент, период и интервал свечей.
        """
        self._logger.info(
            'download_historical_data_started',
            isin=dto.isin,
            from_date=dto.from_date.isoformat(),
            to_date=dto.to_date.isoformat(),
            interval=dto.interval,
        )

        request = HistoricalDataRequest(
            isin=dto.isin,
            from_date=dto.from_date,
            to_date=dto.to_date,
            interval=dto.interval,
        )

        candles = self._market_data_gateway.download_candles(request)

        self._logger.info(
            'download_historical_data_succeeded',
            count=len(candles),
        )
