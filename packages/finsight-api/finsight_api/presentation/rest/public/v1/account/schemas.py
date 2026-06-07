"""Схема ответа со сводной информацией о счетах."""

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from finsight_api.domain.entities.account import AccountEntity


class AccountResponse(BaseModel):
    """Представление одного счёта в ответе API.

    Attributes:
        id: Идентификатор счёта.
        type: Тип счёта.
        name: Название счёта.
        status: Статус счёта.
    """

    model_config = ConfigDict(
        extra='ignore',
        title='AccountSummaryResponse',
        json_schema_extra={
            'example': {
                'accounts_count': 2,
                'account_ids': ['123456', '789012'],
            },
        },
    )

    id: str
    type: str
    name: str
    status: str

    @classmethod
    def from_entity(cls, entity: 'AccountEntity') -> 'AccountResponse':
        """Строит ответ из доменной сущности счёта.

        Args:
            entity: Доменная сущность счёта.

        Returns:
            Схему AccountResponse с приведёнными к строке type и status.
        """
        return cls(
            id=entity.id,
            type=str(entity.type),
            name=entity.name,
            status=str(entity.status),
        )


class AccountsResponse(BaseModel):
    """Сводный ответ со списком счетов пользователя.

    Attributes:
        accounts_count: Общее количество счетов.
        accounts: Список счетов.
    """

    model_config = ConfigDict(extra='ignore')

    accounts_count: int
    accounts: list[AccountResponse]
