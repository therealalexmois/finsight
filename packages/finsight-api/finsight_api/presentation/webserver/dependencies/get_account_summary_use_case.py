"""FastAPI зависимости для получения информации о счетах."""

from typing import Annotated

from fastapi import Depends

from finsight_api.application.use_cases.get_account_summary import GetAccountsUseCase
from finsight_api.infrastructure.container import AppContainer


def get_accounts_use_case() -> GetAccountsUseCase:
    """Создаёт экземпляр сценария получения информации о счетах.

    Returns:
        Экземпляр GetAccountsUseCase.
    """
    container = AppContainer()
    return GetAccountsUseCase(invest=container.tinkoff_invest())


GetAccountsUseCaseDep = Annotated[GetAccountsUseCase, Depends(get_accounts_use_case)]
