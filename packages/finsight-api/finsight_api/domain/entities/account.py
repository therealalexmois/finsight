"""Entity инвестиционного счёта пользователя."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from finsight_api.domain.value_objects.account_status import AccountStatus
    from finsight_api.domain.value_objects.account_type import AccountType


@dataclass(frozen=True, slots=True, kw_only=True)
class AccountEntity:
    """Инвестиционный счёт пользователя.

    Идентичность определяется `id`.

    Attributes:
        id: Идентификатор счёта в провайдере.
        type: Тип счёта.
        name: Название счёта (человекочитаемое).
        status: Статус счёта.
    """

    id: str
    type: 'AccountType'
    name: str
    status: 'AccountStatus'
