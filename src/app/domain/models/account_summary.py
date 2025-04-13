"""Доменная модель сводной информации о счетах пользователя."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True, slots=True)
class AccountSummaryModel:
    """Модель, представляющая сводку по аккаунтам пользователя.

    Attributes:
        accounts_count: Количество счетов.
        account_ids: Список идентификаторов счетов.
    """

    accounts_count: int
    account_ids: 'Sequence[str]'
