"""Модели предметной области для исторических данных."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.finsight_worker.domain.value_objects import CandleInterval

if TYPE_CHECKING:
    from datetime import date


@dataclass(frozen=True)
class HistoricalDataRequest:
    """Запрос на загрузку исторических данных.

    Attributes:
        isin: Идентификатор инструмента (ISIN).
        from_date: Начальная дата периода (включительно).
        to_date: Конечная дата периода (включительно).
        interval: Интервал между свечами (по умолчанию — 'day').
    """

    isin: str
    from_date: 'date'
    to_date: 'date'
    interval: CandleInterval = CandleInterval.DAY
