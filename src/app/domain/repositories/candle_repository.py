"""Порт репозитория для сохранения исторических свечей."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from src.app.domain.models.candle import CandleModel


class CandleRepository(ABC):
    """Интерфейс репозитория хранения исторических данных о свечах."""

    @abstractmethod
    async def save_all(self, candles: 'Sequence[CandleModel]') -> None:
        """Сохраняет список свечей в базу данных или хранилище."""
        pass
