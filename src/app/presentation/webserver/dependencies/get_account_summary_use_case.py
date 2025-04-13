"""FastAPI зависимости для получения информации о счетах."""

from typing import Annotated

from fastapi import Depends

from src.app.application.use_cases.get_account_summary import GetAccountSummaryUseCase
from src.app.infrastructure.container import AppContainer


def get_account_summary_use_case() -> GetAccountSummaryUseCase:
    """Создаёт экземпляр сценария получения сводной информации о счетах.

    Returns:
        Экземпляр GetAccountSummaryUseCase с внедрённым шлюзом.
    """
    container = AppContainer()
    return GetAccountSummaryUseCase(gateway=container.tinkoff_invest_gateway())


AccountSummaryUseCaseDep = Annotated[GetAccountSummaryUseCase, Depends(get_account_summary_use_case)]
