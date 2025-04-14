"""Модель свечи для представления исторических данных о ценных бумагах."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from src.app.domain.value_objects.candle_interval import CandleInterval


@dataclass(frozen=True)
class CandleModel:
    """Модель свечи для отображения исторических котировок.

    Отображает информацию о цене открытия, закрытия, максимума, минимума,
    объеме торгов и времени свечи за один торговый интервал.

    Attributes:
        figi: Идентификатор инструмента.
        time: Временная метка свечи.
        open: Цена открытия.
        close: Цена закрытия.
        high: Максимальная цена за интервал.
        low: Минимальная цена за интервал.
        volume: Объём торгов за интервал.
        interval: Интервал свечи (например, '1min', 'day').
    """

    figi: str
    time: 'datetime'
    open: float
    close: float
    high: float
    low: float
    volume: int
    interval: 'CandleInterval'
