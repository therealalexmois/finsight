"""Use Case получения облигаций по списку ISIN."""

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from finsight_api.application.ports.logger import LoggerPort
    from finsight_api.application.ports.tinkoff.instruments import TinkoffInstrumentsPort
    from finsight_api.domain.entities.bond import BondEntity
    from finsight_api.domain.value_objects.isin import ISIN


@dataclass(frozen=True, slots=True, kw_only=True)
class GetBondsByIsinInput:
    """Входные данные для bulk-получения облигаций по ISIN.

    Attributes:
        isins: Список ISIN.
        concurrency: Максимальное число параллельных запросов к провайдеру.
    """

    isins: 'Sequence[ISIN]'
    concurrency: int = 5


@dataclass(frozen=True, slots=True, kw_only=True)
class BondFetchError:
    """Ошибка получения данных по конкретному ISIN.

    Attributes:
        isin: ISIN облигации.
        error: Текст ошибки.
    """

    isin: 'ISIN'
    error: str


@dataclass(frozen=True, slots=True, kw_only=True)
class GetBondsByIsinOutput:
    """Результат bulk-получения облигаций по ISIN.

    Attributes:
        bonds: Успешно полученные облигации.
        errors: Ошибки по отдельным ISIN.
        failed_count: Количество ISIN, по которым получить данные не удалось.
    """

    bonds: 'Sequence[BondEntity]'
    errors: 'Sequence[BondFetchError]'
    failed_count: int


class GetBondsByIsinUseCase:
    """Use Case bulk-получения облигаций по ISIN."""

    def __init__(self, *, tinkoff: 'TinkoffInstrumentsPort', logger: 'LoggerPort') -> None:
        """Инициализирует Use Case.

        Args:
            tinkoff: Порт инструментов Tinkoff.
            logger: Логгер приложения.
        """
        self._tinkoff = tinkoff
        self._logger = logger

    async def execute(self, data: GetBondsByIsinInput) -> GetBondsByIsinOutput:
        """Выполняет bulk-получение облигаций по ISIN.

        Запросы к TinkoffInstrumentsPort выполняются параллельно с ограничением
        по concurrency. Ошибка по отдельному ISIN логируется и попадает в errors,
        не прерывая обработку остальных.

        Args:
            data: Входные данные.

        Returns:
            Результат bulk-получения.

        Raises:
            ValueError: Если concurrency не является положительным числом.
        """
        if data.concurrency <= 0:
            raise ValueError('Concurrency must be a positive integer')

        semaphore = asyncio.Semaphore(data.concurrency)
        bonds: list[BondEntity] = []
        errors: list[BondFetchError] = []

        async def _fetch_one(isin: 'ISIN') -> None:
            async with semaphore:
                try:
                    bond = await self._tinkoff.get_bond_by_isin(isin)
                    bonds.append(bond)
                except Exception as exc:
                    self._logger.error(f'Failed to fetch bond by ISIN {isin.value}: {exc!r}')
                    errors.append(BondFetchError(isin=isin, error=str(exc)))

        await asyncio.gather(*(_fetch_one(isin) for isin in data.isins))

        return GetBondsByIsinOutput(
            bonds=tuple(bonds),
            errors=tuple(errors),
            failed_count=len(errors),
        )
