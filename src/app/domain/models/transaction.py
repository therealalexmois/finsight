"""Модель транзакции."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID

    from src.app.domain.value_objects.amount import Amount
    from src.app.domain.value_objects.currency import Currency
    from src.app.domain.value_objects.isin import ISIN
    from src.app.domain.value_objects.transaction_type import TransactionType


@dataclass(frozen=True)
class Transaction:
    """Модель транзакции, представляющая операцию покупки или продажи актива.

    Используется для фиксации движения средств пользователя в рамках его инвестиционного портфеля.

    Attributes:
        id: Уникальный идентификатор транзакции.
        user_id: Идентификатор пользователя, совершившего транзакцию.
        stock_isin: ISIN ценной бумаги, по которой совершена транзакция.
        amount: Сумма транзакции.
        currency: Валюта, в которой произведена транзакция.
        date: Дата и время совершения транзакции.
        type: Тип транзакции — покупка или продажа.
    """

    id: 'UUID'
    user_id: 'UUID'
    stock_isin: 'ISIN'
    amount: 'Amount'
    currency: 'Currency'
    date: 'datetime'
    type: 'TransactionType'
