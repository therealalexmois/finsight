"""Модель для исторических данных по акции."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from src.finsight_api.domain.value_objects.amount import Amount
    from src.finsight_api.domain.value_objects.isin import ISIN


@dataclass(frozen=True)
class StockHistory:
    """Модель исторических данных об акции за конкретную дату.

    Представляет информацию о цене открытия, закрытия, максимальной и минимальной ценах,
    а также объёме торгов по конкретной акции.

    Attributes:
        isin: ISIN-идентификатор ценной бумаги.
        date: Дата, к которой относятся данные.
        open_price: Цена открытия.
        close_price: Цена закрытия.
        high: Максимальная цена за день.
        low: Минимальная цена за день.
        volume: Объём торгов за день.
    """

    isin: 'ISIN'
    date: 'date'
    open_price: 'Amount'
    close_price: 'Amount'
    high: 'Amount'
    low: 'Amount'
    volume: float
