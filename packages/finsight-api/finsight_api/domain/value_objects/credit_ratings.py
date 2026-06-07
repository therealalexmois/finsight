"""Модуль содержит типы-значения кредитных рейтингов."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date

    from finsight_api.domain.value_objects.credit_rating_agency import CreditRatingAgency


# TODO: можно переписать `__getitem__`
@dataclass(frozen=True, slots=True, kw_only=True)
class CreditRating:
    """Кредитный рейтинг от конкретного агентства.

    Attributes:
        agency: Агентство рейтинга.
        value: Значение рейтинга (например, 'AAA(RU)', 'ruAA+').
        outlook: Прогноз/перспектива (например, 'стабильный'), если доступно.
        date_assigned: Дата присвоения рейтинга, если доступно.
        source: Источник рейтинга (например, 'dohod.ru'), если известен.
    """

    agency: 'CreditRatingAgency'
    value: str
    outlook: str | None = None
    date_assigned: 'date | None' = None
    source: str | None = None

    def __post_init__(self) -> None:
        """Проверяет базовые инварианты.

        Raises:
            ValueError: Если значение рейтинга пустое.
        """
        if not self.value.strip():
            raise ValueError('Credit rating value must be non-empty')


@dataclass(frozen=True, slots=True, kw_only=True)
class CreditRatings:
    """Набор кредитных рейтингов для инструмента.

    Attributes:
        items: Рейтинги (возможно пустой набор).
    """

    # TODO: можно сделать словарем
    items: tuple[CreditRating, ...]

    @classmethod
    def empty(cls) -> 'CreditRatings':
        """Создаёт пустой набор рейтингов.

        Returns:
            CreditRatings: Пустой набор рейтингов.
        """
        return cls(items=())

    @classmethod
    def from_iterable(cls, items: 'Iterable[CreditRating]') -> 'CreditRatings':
        """Создаёт набор рейтингов из последовательности.

        Args:
            items: Последовательность CreditRating.

        Returns:
            CreditRatings: Набор рейтингов.
        """
        unique: dict[CreditRatingAgency, CreditRating] = {}

        for item in items:
            unique[item.agency] = item

        return cls(items=tuple(unique.values()))

    def get(self, agency: 'CreditRatingAgency') -> CreditRating | None:
        """Возвращает рейтинг по агентству.

        Args:
            agency: Агентство рейтинга.

        Returns:
            CreditRating | None: Рейтинг или None, если не найден.
        """
        for item in self.items:
            if item.agency == agency:
                return item

        return None
