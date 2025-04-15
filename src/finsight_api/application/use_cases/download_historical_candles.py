"""Сценарий загрузки исторических свечей по ISIN.

Используется для получения исторических котировок инструмента с Tinkoff Invest API
и сохранения их в локальное хранилище для последующего анализа и обучения модели.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from src.finsight_api.application.ports.gateways.tinkoff_gateway import TinkoffInvestGateway
    from src.finsight_api.domain.repositories.candle_repository import CandleRepository
    from src.finsight_api.domain.value_objects.candle_interval import CandleInterval


class DownloadHistoricalCandlesUseCase:
    """Сценарий получения и сохранения исторических свечей."""

    def __init__(
        self,
        gateway: 'TinkoffInvestGateway',
        repository: 'CandleRepository',
    ) -> None:
        """Инициализирует use case с API-шлюзом и репозиторием хранения свечей.

        Args:
            gateway: Шлюз для обращения к Tinkoff Invest API.
            repository: Репозиторий для сохранения свечей.
        """
        self._gateway = gateway
        self._repository = repository

    async def execute(self, isin: str, from_: 'datetime', to: 'datetime', interval: 'CandleInterval') -> None:
        """Выполняет загрузку и сохранение исторических свечей.

        Args:
            isin: ISIN инструмента.
            from_: Начальная дата.
            to: Конечная дата.
            interval: Интервал свечей (например, 'day', 'hour').
        """
        candles = await self._gateway.get_candles_by_isin(isin, from_, to, interval)
        await self._repository.save_all(candles)
