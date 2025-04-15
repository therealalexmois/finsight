"""Сценарий получения сводной информации о счетах пользователя через Tinkoff API."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.finsight_api.application.ports.gateways.tinkoff_gateway import TinkoffInvestGateway
    from src.finsight_api.domain.models.account_summary import AccountSummaryModel


class GetAccountSummaryUseCase:
    """Сценарий получения сводной информации о счетах.

    Использует шлюз к Tinkoff Invest API для получения сведений о количестве счетов
    и их идентификаторах.
    """

    def __init__(self, gateway: 'TinkoffInvestGateway') -> None:
        """Инициализирует UseCase с заданным шлюзом.

        Args:
            gateway: Шлюз к Tinkoff Invest API.
        """
        self._gateway = gateway

    async def execute(self) -> 'AccountSummaryModel':
        """Выполняет сценарий получения информации о счетах.

        Returns:
            Доменная модель AccountSummaryModel.
        """
        return await self._gateway.get_account_summary()
