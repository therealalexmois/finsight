"""Сценарий бизнес-логики для получения портфеля пользователя.

Модуль содержит UseCase `GetPortfolioUseCase`, который инкапсулирует процесс
получения портфеля пользователя с помощью шлюза к Tinkoff Invest API.
"""

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from finsight_api.application.ports.tinkoff import TinkoffInvestPort
    from finsight_api.domain.entities.portfolio import PortfolioEntity


class GetPortfolioUseCase:
    """Сценарий получения информации о портфеле пользователя по ID счёта."""

    def __init__(self, gateway: 'TinkoffInvestPort') -> None:
        """Инициализирует UseCase с переданным шлюзом.

        Args:
            gateway: Шлюз для обращения к Tinkoff Invest API.
        """
        self._gateway = gateway

    async def execute(self, account_id: str) -> 'PortfolioEntity':
        """Выполняет запрос на получение портфеля для указанного счёта.

        Загружает портфель через TinkoffInvestPort и пересобирает PortfolioEntity
        с пересчитанным total_value как суммой стоимостей позиций.

        Args:
            account_id: Идентификатор счёта.

        Returns:
            Доменная сущность портфеля PortfolioEntity.
        """
        portfolio = await self._gateway.get_portfolio(account_id)
        total_value = sum((p.value for p in portfolio.positions), start=Decimal(0))

        return replace(portfolio, total_value=total_value)
