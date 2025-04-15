"""Роуты для получения информации об аккаунтах."""

from http import HTTPStatus

from fastapi import APIRouter

from src.finsight_api.presentation.schemas.account_summary import AccountSummaryResponse
from src.finsight_api.presentation.webserver.dependencies.get_account_summary_use_case import (
    AccountSummaryUseCaseDep,  # noqa: TC001
)

router = APIRouter(
    prefix='/account',
    tags=['Account'],
)


@router.get(
    '/summary',
    status_code=HTTPStatus.OK,
    summary='Получение сводной информации о счетах',
)
async def get_account_summary(use_case: AccountSummaryUseCaseDep) -> AccountSummaryResponse:
    """Обработчик запроса на получение сводной информации о счетах.

    Args:
        use_case: Сценарий получения информации о счетах через Tinkoff API.

    Returns:
        Схема ответа AccountSummaryResponse с количеством счетов и их идентификаторами.
    """
    result = await use_case.execute()

    return AccountSummaryResponse(
        accounts_count=result.accounts_count,
        account_ids=result.account_ids,
    )
