"""Value Objects для стакана (order book)."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from finsight_api.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True, kw_only=True)
class OrderBookLevel:
    """Один уровень стакана.

    Attributes:
        price: Цена уровня.
        quantity: Объём (количество) на уровне.
    """

    price: 'Money'
    quantity: int


@dataclass(frozen=True, slots=True, kw_only=True)
class OrderBook:
    """Снимок стакана на момент времени.

    Attributes:
        figi: FIGI инструмента.
        depth: Глубина стакана.
        bids: Список bid-уровней.
        asks: Список ask-уровней.
        last_price: Последняя цена (если присутствует).
        close_price: Цена закрытия (если присутствует).
        timestamp: Время снимка стакана (orderbook_ts).
    """

    figi: str
    depth: int
    bids: list['OrderBookLevel']
    asks: list['OrderBookLevel']
    last_price: 'Money | None'
    close_price: 'Money | None'
    timestamp: 'datetime | None'
