"""Порт репозитория для сохранения исторических свечей."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Collection

    from finsight_api.domain.entities.candle import CandleEntity


class CandleRepository(ABC):
    """Доменный порт для сохранения исторических свечей.

    Реализации (адаптеры) находятся в инфраструктурном слое; домен зависит
    только от этого интерфейса.
    """

    @abstractmethod
    async def save_all(self, candles: 'Collection[CandleEntity]') -> None:
        """Сохраняет набор свечей в хранилище.

        Args:
            candles: Свечи для сохранения.
        """
