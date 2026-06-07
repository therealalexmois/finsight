"""Модуль содержит тип-значение TransactionType.

Определяет тип финансовой транзакции: покупка или продажа.
"""

from enum import auto, StrEnum, unique


@unique
class TransactionType(StrEnum):
    """Тип транзакции: покупка или продажа."""

    BUY = auto()
    SELL = auto()
