"""Маршрут REST API для получения портфеля пользователя.

Обрабатывает GET-запрос на получение информации о текущем портфеле пользователя
по идентификатору счёта, используя бизнес-сценарий `GetPortfolioUseCase`.
"""

from http import HTTPStatus

from fastapi import APIRouter

from src.finsight_api.presentation.mappers.portfolio_mapper import map_portfolio_to_response
from src.finsight_api.presentation.schemas.portfolio import PortfolioResponse  # noqa: TC001
from src.finsight_api.presentation.webserver.dependencies.get_portfolio_use_case import (
    PortfolioUseCaseDep,  # noqa: TC001
)

router = APIRouter(
    prefix='/account',
    tags=['Account'],
)


@router.get(
    '/{account_id}/portfolio',
    status_code=HTTPStatus.OK,
    summary='Получение портфеля пользователя по ID счёта',
)
async def get_portfolio(account_id: str, use_case: PortfolioUseCaseDep) -> PortfolioResponse:
    """Обработчик запроса получения портфеля пользователя по ID счёта.

    Args:
        account_id: Идентификатор счёта.
        use_case: Сценарий получения портфеля.

    Returns:
        Схема ответа PortfolioResponse с информацией о портфеле.
    """
    result = await use_case.execute(account_id)
    return map_portfolio_to_response(result)
