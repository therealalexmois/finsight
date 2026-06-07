"""Порт инструментов Tinkoff Invest API.

Содержит контракты для получения метаданных по инструментам, купонов и брендов.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from finsight_api.domain.entities.bond import BondEntity
    from finsight_api.domain.entities.brand import BrandEntity
    from finsight_api.domain.value_objects.bond_coupon import BondCoupon
    from finsight_api.domain.value_objects.isin import ISIN


class TinkoffInstrumentsPort(ABC):
    """Интерфейс инструментов Tinkoff Invest API."""

    # TODO:
    # - Добавить доменные ошибки порта и маппинг SDK-ошибок на них.
    # - Добавить входные/выходные DTO порта для стабильных контрактов use cases.

    @abstractmethod
    async def get_bond_by_figi(self, figi: str) -> 'BondEntity':
        """Возвращает метаданные облигации по FIGI.

        Args:
            figi: FIGI-идентификатор облигации.

        Returns:
            Доменная сущность облигации.
        """

    @abstractmethod
    async def get_bond_by_isin(self, isin: 'ISIN') -> 'BondEntity':
        """Возвращает метаданные облигации по ISIN.

        Args:
            isin: ISIN облигации.

        Returns:
            Доменная сущность облигации.
        """

    @abstractmethod
    async def get_bond_coupons(
        self,
        *,
        figi: str,
        from_date: 'date | None' = None,
        to_date: 'date | None' = None,
    ) -> list['BondCoupon']:
        """Возвращает список купонов по облигации.

        Args:
            figi: FIGI облигации.
            from_date: Начало диапазона (включительно). Если None — без нижней границы.
            to_date: Конец диапазона (включительно). Если None — без верхней границы.

        Returns:
            Список купонов как value objects.
        """

    @abstractmethod
    async def get_brands(self) -> list['BrandEntity']:
        """Возвращает список брендов.

        Returns:
            Список доменных сущностей Brand.
        """
