"""Сценарий бизнес-логики для получения портфеля пользователя.

Модуль содержит UseCase `GetPortfolioUseCase`, который инкапсулирует процесс
получения портфеля пользователя с помощью шлюза к Tinkoff Invest API.
"""

from typing import TYPE_CHECKING

from src.finsight_api.domain.models.portfolio import PortfolioModel

if TYPE_CHECKING:
    from src.finsight_api.application.ports.gateways.tinkoff_gateway import TinkoffInvestGateway


class GetPortfolioUseCase:
    """Сценарий получения информации о портфеле пользователя по ID счёта."""

    def __init__(self, gateway: 'TinkoffInvestGateway') -> None:
        """Инициализирует UseCase с переданным шлюзом.

        Args:
            gateway: Шлюз для обращения к Tinkoff Invest API.
        """
        self._gateway = gateway

    async def execute(self, account_id: str) -> PortfolioModel:
        """Выполняет запрос на получение портфеля для указанного счёта.

        Args:
            account_id: Идентификатор счёта.

        Returns:
            Доменная модель портфеля PortfolioModel.
        """
        portfolio = await self._gateway.get_portfolio(account_id)
        total_value = float(sum(p.value for p in portfolio.positions))
        return PortfolioModel(
            account_id=portfolio.account_id,
            total_value=total_value,
            currency=portfolio.currency,
            positions=portfolio.positions,
        )
