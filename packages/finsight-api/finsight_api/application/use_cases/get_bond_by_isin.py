"""Use Case получения облигации по ISIN."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from finsight_api.domain.value_objects.isin import ISIN

if TYPE_CHECKING:
    from finsight_api.application.ports.logger import LoggerPort
    from finsight_api.application.ports.tinkoff.instruments import TinkoffInstrumentsPort
    from finsight_api.domain.entities.bond import BondEntity


@dataclass(frozen=True, slots=True, kw_only=True)
class GetBondByIsinInput:
    """Входные данные для получения облигации по ISIN.

    Attributes:
        isin: ISIN облигации.
    """

    isin: ISIN


@dataclass(frozen=True, slots=True, kw_only=True)
class GetBondByIsinOutput:
    """Результат получения облигации по ISIN.

    Attributes:
        isin: ISIN облигации.
        bond: Доменная сущность облигации, если найдена.
        error: Текст ошибки, если получить данные не удалось.
    """

    isin: ISIN
    bond: 'BondEntity | None'
    error: str | None


class GetBondByIsinUseCase:
    """Use Case получения облигации по ISIN."""

    def __init__(self, *, tinkoff: 'TinkoffInstrumentsPort', logger: 'LoggerPort') -> None:
        """Инициализирует Use Case.

        Args:
            tinkoff: Порт инструментов Tinkoff.
            logger: Логгер приложения.
        """
        self._tinkoff = tinkoff
        self._logger = logger

    async def execute(self, data: GetBondByIsinInput) -> GetBondByIsinOutput:
        """Выполняет получение облигации по ISIN через TinkoffInstrumentsPort.

        Ошибка получения не пробрасывается: она логируется и возвращается в
        поле error результата с пустым bond.

        Args:
            data: Входные данные.

        Returns:
            Результат получения облигации по ISIN.
        """
        try:
            bond = await self._tinkoff.get_bond_by_isin(data.isin)
            return GetBondByIsinOutput(isin=data.isin, bond=bond, error=None)
        except Exception as exc:
            self._logger.error(f'Failed to fetch bond by ISIN {data.isin.value}: {exc!r}')
            return GetBondByIsinOutput(isin=data.isin, bond=None, error=str(exc))
