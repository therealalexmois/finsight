"""Модуль содержит тип-значение статуса инвестиционного счёта."""

from enum import IntEnum, unique


@unique
class AccountStatus(IntEnum):
    """Статус инвестиционного счёта.

    Значения соответствуют перечислению в Tinkoff Invest API и сохраняются
    как устойчивые числовые коды для БД/кэша.
    """

    ACCOUNT_STATUS_UNSPECIFIED = 0
    ACCOUNT_STATUS_NEW = 1
    ACCOUNT_STATUS_OPEN = 2
    ACCOUNT_STATUS_CLOSED = 3
