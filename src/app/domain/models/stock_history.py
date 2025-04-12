"""Модель для исторических данных по акции."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from src.app.domain.value_objects.amount import Amount
    from src.app.domain.value_objects.isin import ISIN


@dataclass(frozen=True)
class StockHistory:
    """Модель исторических данных об акции."""

    isin: 'ISIN'
    date: 'date'
    open_price: 'Amount'
    close_price: 'Amount'
    high: 'Amount'
    low: 'Amount'
    volume: float
