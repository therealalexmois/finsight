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
    """Модель транзакции в доменном слое."""

    id: 'UUID'
    user_id: 'UUID'
    stock_isin: 'ISIN'
    amount: 'Amount'
    currency: 'Currency'
    date: 'datetime'
    type: 'TransactionType'
