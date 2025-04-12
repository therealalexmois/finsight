"""Модуль содержит тип-значение TransactionType.

Определяет тип финансовой транзакции: покупка или продажа.
"""

from enum import Enum, unique


@unique
class TransactionType(Enum):
    """Тип транзакции: покупка или продажа."""

    BUY = 'buy'
    SELL = 'sell'
