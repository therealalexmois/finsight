"""Порт маркет-данных Tinkoff Invest API.

Содержит контракты для получения свечей, стакана и других данных рынка.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import date

    from finsight_api.domain.entities.candle import CandleEntity
    from finsight_api.domain.value_objects.candle_interval import CandleInterval
    from finsight_api.domain.value_objects.order_book import OrderBook


class TinkoffMarketDataPort(ABC):
    """Интерфейс маркет-данных Tinkoff Invest API."""

    # TODO:
    # - Добавить доменные ошибки порта и маппинг SDK-ошибок на них.
    # - Добавить входные/выходные DTO порта для стабильных контрактов use cases.

    @abstractmethod
    async def get_candles_by_isin(
        self,
        isin: str,
        from_date: 'date',
        to_date: 'date',
        interval: 'CandleInterval',
    ) -> 'Sequence[CandleEntity]':
        """Возвращает историю котировок по ISIN за указанный период.

        Args:
            isin: ISIN-идентификатор ценной бумаги.
            from_date: Начальная дата интервала.
            to_date: Конечная дата интервала.
            interval: Интервал свечей.

        Returns:
            Последовательность доменных сущностей свечей.
        """

    @abstractmethod
    async def get_order_book(self, *, figi: str, depth: int = 1) -> 'OrderBook':
        """Возвращает стакан по инструменту.

        Args:
            figi: FIGI инструмента.
            depth: Глубина стакана.

        Returns:
            Value object стакана.
        """
