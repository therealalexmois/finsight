"""Контракт порта доступа к источнику рыночных данных."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from src.finsight_worker.domain.models import HistoricalDataRequest


class MarketDataGateway(ABC):
    """Порт для доступа к историческим рыночным данным."""

    @abstractmethod
    def download_candles(self, request: 'HistoricalDataRequest') -> 'Sequence[object]':
        """Загружает исторические свечи по запросу.

        Args:
            request: Параметры запроса к источнику данных.

        Returns:
            Список свечей.
        """
        raise NotImplementedError
