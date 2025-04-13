"""Схема ответа со сводной информацией о счетах."""

from collections.abc import Sequence

from pydantic import BaseModel


class AccountSummaryResponse(BaseModel):
    """Ответ на запрос сводной информации о счетах.

    Содержит количество счетов и список их идентификаторов.

    Attributes:
        accounts_count: Общее количество счетов пользователя.
        account_ids: Список идентификаторов счетов.
    """

    accounts_count: int
    account_ids: Sequence[str]

    model_config = {
        'title': 'AccountSummaryResponse',
        'json_schema_extra': {
            'example': {
                'accounts_count': 2,
                'account_ids': ['123456', '789012'],
            },
        },
    }
