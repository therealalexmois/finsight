"""Порт получения кредитных рейтингов по инструменту.

Порт описывает контракт на получение кредитных рейтингов (например, АКРА, Эксперт РА)
из внешнего источника данных.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from finsight_api.domain.value_objects.credit_ratings import CreditRatings
    from finsight_api.domain.value_objects.isin import ISIN


class CreditRatingsPort(ABC):
    """Интерфейс источника кредитных рейтингов."""

    @abstractmethod
    async def get_ratings_by_isin(self, isin: 'ISIN') -> 'CreditRatings':
        """Возвращает кредитные рейтинги для указанного ISIN.

        Args:
            isin: ISIN инструмента.

        Returns:
            CreditRatings: Набор кредитных рейтингов (может быть пустым).
        """
