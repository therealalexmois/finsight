"""Модуль содержит тип-значение типа инвестиционного счёта."""

from enum import IntEnum, unique


@unique
class AccountType(IntEnum):
    """Тип инвестиционного счёта.

    Значения соответствуют перечислению в Tinkoff Invest API и сохраняются
    как устойчивые числовые коды для БД/кэша.
    """

    ACCOUNT_TYPE_UNSPECIFIED = 0
    ACCOUNT_TYPE_TINKOFF = 1
    ACCOUNT_TYPE_TINKOFF_IIS = 2
    ACCOUNT_TYPE_INVEST_BOX = 3
    ACCOUNT_TYPE_INVEST_FUND = 4
