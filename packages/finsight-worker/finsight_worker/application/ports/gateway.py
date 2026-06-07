"""Контракт порта доступа к источнику рыночных данных."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from finsight_worker.domain.models import HistoricalDataRequest


class MarketDataGateway(ABC):
    """Порт доступа к источнику исторических рыночных данных.

    Абстрагирует use case от конкретной реализации источника (например,
    Tinkoff Invest API).
    """

    @abstractmethod
    def download_candles(self, request: 'HistoricalDataRequest') -> 'Sequence[object]':
        """Загружает исторические свечи по параметрам запроса.

        Args:
            request: Инструмент, период и интервал свечей.

        Returns:
            Последовательность свечей за указанный период.
        """
        raise NotImplementedError
