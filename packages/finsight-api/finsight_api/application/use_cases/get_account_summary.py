"""Сценарий получения сводной информации о счетах пользователя через Tinkoff API."""

from collections.abc import Collection
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from finsight_api.application.ports.tinkoff import TinkoffInvestPort
    from finsight_api.domain.entities.account import AccountEntity


class GetAccountsUseCase:
    """Прикладной сценарий получения списка счетов пользователя."""

    def __init__(self, invest: 'TinkoffInvestPort') -> None:
        """Инициализирует UseCase с заданным шлюзом.

        Args:
            invest: Порт интеграции с Tinkoff Invest API.
        """
        self._invest = invest

    async def execute(self) -> 'Collection[AccountEntity]':
        """Возвращает список счетов пользователя.

        Returns:
            Collection[AccountEntity]: доменные сущности счетов.
        """
        return await self._invest.get_accounts()
