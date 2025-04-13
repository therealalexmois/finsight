"""DTO для преобразования информации о счетах из Tinkoff Invest API."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.app.domain.models.account_summary import AccountSummaryModel

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tinkoff.invest import Account


@dataclass(frozen=True, slots=True)
class AccountSummaryDTO:
    """DTO, представляющий сводку по аккаунтам пользователя."""

    accounts_count: int
    account_ids: 'Sequence[str]'

    @classmethod
    def from_sdk(cls, accounts: 'Sequence[Account]') -> 'AccountSummaryDTO':
        """Создаёт DTO из списка аккаунтов SDK.

        Args:
            accounts: Список аккаунтов из SDK.

        Returns:
            DTO со сводной информацией.
        """
        return cls(
            accounts_count=len(accounts),
            account_ids=[a.id for a in accounts],
        )

    def to_model(self) -> AccountSummaryModel:
        """Преобразует DTO в доменную модель.

        Returns:
            Доменная модель AccountSummaryModel.
        """
        return AccountSummaryModel(
            accounts_count=self.accounts_count,
            account_ids=self.account_ids,
        )
