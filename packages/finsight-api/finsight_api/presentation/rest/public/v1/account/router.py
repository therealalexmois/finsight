"""Роуты для получения информации об аккаунтах."""

from http import HTTPStatus

from fastapi import APIRouter

from finsight_api.presentation.webserver.dependencies.get_account_summary_use_case import (
    GetAccountsUseCaseDep,  # noqa: TC001
)

from .schemas import AccountResponse, AccountsResponse

router = APIRouter(
    prefix='/account',
    tags=['Account'],
)


@router.get(
    '/accounts',
    status_code=HTTPStatus.OK,
    summary='Получение сводной информации о счетах',
)
async def get_account_summary(use_case: GetAccountsUseCaseDep) -> AccountsResponse:
    """Возвращает сводную информацию о счетах пользователя.

    Args:
        use_case: Сценарий получения информации о счетах через Tinkoff API.

    Returns:
        AccountsResponse с количеством счетов и списком счетов.
    """
    accounts = await use_case.execute()

    return AccountsResponse(
        accounts_count=len(accounts),
        accounts=[AccountResponse.from_entity(a) for a in accounts],
    )
