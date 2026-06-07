"""Порт операций Tinkoff Invest API.

Содержит контракты для методов, относящихся к операциям и состоянию портфеля.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Collection

    from finsight_api.domain.entities.account import AccountEntity
    from finsight_api.domain.entities.portfolio import PortfolioEntity


class TinkoffOperationsPort(ABC):
    """Интерфейс операций Tinkoff Invest API."""

    # TODO:
    # Добавить доменные ошибки порта и маппинг SDK-ошибок на них.
    # Добавить входные/выходные DTO порта для стабильных контрактов use cases.

    @abstractmethod
    async def get_accounts(self) -> 'Collection[AccountEntity]':
        """Возвращает список счетов пользователя.

        Returns:
            Collection[AccountEntity]: доменные сущности счетов.
        """

    @abstractmethod
    async def get_portfolio(self, account_id: str) -> 'PortfolioEntity':
        """Возвращает актуальное состояние портфеля пользователя.

        Args:
            account_id: Идентификатор счёта.

        Returns:
            Доменная сущность портфеля со списком позиций и агрегатами.
        """
