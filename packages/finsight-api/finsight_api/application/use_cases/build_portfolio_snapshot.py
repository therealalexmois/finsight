"""Use Case сборки снапшота портфеля с обогащением по позициям.

UC строит снапшот на основе портфеля (positions) и дополнительных данных по
инструментам (bond_by_figi, coupons, order_book). Обогащение выполняется
по каждой позиции независимо: ошибки не прерывают сборку всего снапшота.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime, UTC
from typing import TYPE_CHECKING

from finsight_api.domain.value_objects.instrument_type import InstrumentType

if TYPE_CHECKING:
    from finsight_api.application.ports.logger import LoggerPort
    from finsight_api.application.ports.tinkoff import TinkoffInvestPort
    from finsight_api.domain.entities.bond import BondEntity
    from finsight_api.domain.entities.portfolio import PortfolioEntity
    from finsight_api.domain.value_objects.bond_coupon import BondCoupon
    from finsight_api.domain.value_objects.order_book import OrderBook
    from finsight_api.domain.value_objects.portfolio_position import PortfolioPosition


@dataclass(frozen=True, slots=True, kw_only=True)
class BuildPortfolioSnapshotInput:
    """Входные параметры Use Case сборки снапшота портфеля.

    Attributes:
        account_id: Идентификатор счёта.
        order_book_depth: Глубина стакана для snapshot.
        coupons_from_date: Нижняя граница периода купонов (включительно).
        coupons_to_date: Верхняя граница периода купонов (включительно).
    """

    account_id: str
    order_book_depth: int = 1
    coupons_from_date: 'date | None' = None
    coupons_to_date: 'date | None' = None


@dataclass(frozen=True, slots=True, kw_only=True)
class EnrichmentError:
    """Ошибка обогащения для конкретной позиции портфеля.

    Attributes:
        figi: FIGI позиции.
        step: Шаг обогащения (bond_by_figi / coupons / order_book).
        error_type: Класс/тип ошибки.
        message: Краткое описание ошибки.
    """

    figi: str
    step: str
    error_type: str
    message: str


@dataclass(frozen=True, slots=True, kw_only=True)
class BondEnrichment:
    """Обогащение для облигационной позиции.

    Attributes:
        bond: Метаданные облигации (None при ошибке получения).
        coupons: Купоны облигации.
        order_book: Снимок стакана (может быть None при ошибке/отсутствии).
        credit_ratings: Кредитные рейтинги. На текущем этапе не поддерживаются.
            Всегда None (не “пустой список”), чтобы явно обозначать отсутствие
            источника данных/подсистемы.
    """

    bond: 'BondEntity | None'
    coupons: Sequence['BondCoupon']
    order_book: 'OrderBook | None'
    credit_ratings: None


@dataclass(frozen=True, slots=True, kw_only=True)
class PositionSnapshot:
    """Снапшот одной позиции портфеля.

    Attributes:
        position: Базовая позиция портфеля (VO).
        enrichment: Обогащение (только для bond; иначе None).
    """

    position: 'PortfolioPosition'
    enrichment: 'BondEnrichment | None'


@dataclass(frozen=True, slots=True, kw_only=True)
class BuildPortfolioSnapshotOutput:
    """Результат Use Case сборки снапшота портфеля.

    Attributes:
        created_at: Время генерации снапшота (UTC).
        portfolio: Агрегат портфеля.
        positions: Список позиций с обогащением.
        enrichment_errors: Ошибки обогащения (по позициям).
        enrichment_failed_count: Количество ошибок обогащения.
    """

    created_at: 'datetime'
    portfolio: 'PortfolioEntity'
    # TODO: Здесь дублируется инфомация с PortfolioEntity.positions
    positions: Sequence['PositionSnapshot']
    enrichment_errors: Sequence['EnrichmentError']
    enrichment_failed_count: int


class BuildPortfolioSnapshotUseCase:
    """Собирает снапшот портфеля и обогащает позиции внешними данными.

    Загружает портфель через TinkoffInvestPort и для каждой bond-позиции
    дополнительно запрашивает метаданные облигации, купоны и стакан. Обогащение
    по каждой позиции и каждому шагу изолировано: ошибки шага логируются и
    фиксируются в результате, не прерывая сборку остального снапшота.
    """

    def __init__(self, *, tinkoff: 'TinkoffInvestPort', logger: 'LoggerPort') -> None:
        """Инициализирует Use Case.

        Args:
            tinkoff: Порт интеграции с Tinkoff Invest API.
            logger: Логгер приложения.
        """
        self._tinkoff = tinkoff
        self._logger = logger

    async def execute(self, data: BuildPortfolioSnapshotInput) -> BuildPortfolioSnapshotOutput:
        """Строит снапшот портфеля с обогащением.

        Обогащение выполняется по каждой позиции независимо. Ошибки не
        прерывают обработку остальных позиций и фиксируются в выходе.

        Args:
            data: Входные параметры Use Case.

        Returns:
            BuildPortfolioSnapshotOutput: Снапшот портфеля.
        """
        portfolio = await self._tinkoff.get_portfolio(data.account_id)

        positions: list[PositionSnapshot] = []
        errors: list[EnrichmentError] = []

        for pos in portfolio.positions:
            if pos.instrument_type != InstrumentType.BOND:
                positions.append(PositionSnapshot(position=pos, enrichment=None))
                continue

            enrichment, pos_errors = await self._enrich_bond_position(
                figi=pos.figi,
                order_book_depth=data.order_book_depth,
                coupons_from_date=data.coupons_from_date,
                coupons_to_date=data.coupons_to_date,
            )
            errors.extend(pos_errors)
            positions.append(PositionSnapshot(position=pos, enrichment=enrichment))

        return BuildPortfolioSnapshotOutput(
            created_at=datetime.now(tz=UTC),
            portfolio=portfolio,
            positions=positions,
            enrichment_errors=tuple(errors),
            enrichment_failed_count=len(errors),
        )

    async def _enrich_bond_position(
        self,
        *,
        figi: str,
        order_book_depth: int,
        coupons_from_date: date | None,
        coupons_to_date: date | None,
    ) -> tuple[BondEnrichment, list[EnrichmentError]]:
        """Обогащает одну bond-позицию.

        Args:
            figi: FIGI инструмента.
            order_book_depth: Глубина стакана.
            coupons_from_date: Нижняя граница периода купонов (включительно).
            coupons_to_date: Верхняя граница периода купонов (включительно).

        Returns:
            tuple[BondEnrichment, list[EnrichmentError]]: Обогащение и список ошибок.
        """
        bond: BondEntity | None = None
        coupons: Sequence[BondCoupon] = ()
        order_book: OrderBook | None = None

        errors: list[EnrichmentError] = []

        try:
            bond = await self._tinkoff.get_bond_by_figi(figi)
        except Exception as exc:
            errors.append(self._build_error(figi=figi, step='bond_by_figi', exc=exc))
            self._logger.warning(f'Position enrichment failed for {figi} at step bond_by_figi: {exc!r}')

        try:
            coupons = await self._tinkoff.get_bond_coupons(
                figi=figi,
                from_date=coupons_from_date,
                to_date=coupons_to_date,
            )
        except Exception as exc:
            errors.append(self._build_error(figi=figi, step='coupons', exc=exc))
            self._logger.warning(f'Position enrichment failed for {figi} at step coupons: {exc!r}')

        try:
            order_book = await self._tinkoff.get_order_book(figi=figi, depth=order_book_depth)
        except Exception as exc:
            errors.append(self._build_error(figi=figi, step='order_book', exc=exc))
            self._logger.warning(f'Position enrichment failed for {figi} at step order_book: {exc!r}')

        return (
            BondEnrichment(
                bond=bond,
                coupons=coupons,
                order_book=order_book,
                credit_ratings=None,
            ),
            errors,
        )

    def _build_error(self, *, figi: str, step: str, exc: Exception) -> EnrichmentError:
        """Строит объект ошибки обогащения.

        Args:
            figi: FIGI позиции.
            step: Шаг обогащения.
            exc: Исключение.

        Returns:
            EnrichmentError: Ошибка обогащения.
        """
        return EnrichmentError(
            figi=figi,
            step=step,
            error_type=type(exc).__name__,
            message=str(exc),
        )
