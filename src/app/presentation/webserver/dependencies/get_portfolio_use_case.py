"""Зависимость FastAPI для получения экземпляра use case `GetPortfolioUseCase`.

Используется для внедрения бизнес-логики получения портфеля пользователя в обработчики маршрутов.
"""

from typing import Annotated

from fastapi import Depends

from src.app.application.use_cases.get_portfolio import GetPortfolioUseCase
from src.app.infrastructure.container import AppContainer


# TODO: Вынести tinkoff_invest_gateway через DI
def get_portfolio_use_case() -> GetPortfolioUseCase:
    """Создаёт экземпляр сценария получения портфеля пользователя.

    Returns:
        Экземпляр GetPortfolioUseCase.
    """
    container = AppContainer()
    return GetPortfolioUseCase(gateway=container.tinkoff_invest_gateway())


PortfolioUseCaseDep = Annotated[GetPortfolioUseCase, Depends(get_portfolio_use_case)]
