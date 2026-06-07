"""Базовый порт Tinkoff Invest API.

Содержит композитный контракт, объединяющий порты по подсервисам в единый тип.
"""

from abc import ABC

from .instruments import TinkoffInstrumentsPort
from .market_data import TinkoffMarketDataPort
from .operations import TinkoffOperationsPort


class TinkoffInvestPort(TinkoffOperationsPort, TinkoffInstrumentsPort, TinkoffMarketDataPort, ABC):
    """Композитный порт Tinkoff Invest API.

    Объединяет порты по подсервисам в единый контракт для адаптера и DI.
    """
