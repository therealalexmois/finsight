"""Порт для интеграции с Tinkoff Invest API."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import date

    from src.app.domain.models.account_summary import AccountSummaryModel
    from src.app.domain.models.candle import CandleModel
    from src.app.domain.models.portfolio import PortfolioModel


class TinkoffInvestGateway(ABC):
    """Интерфейс взаимодействия с Tinkoff Invest API.

    Предоставляет абстракции для работы с внешним API Tinkoff Invest,
    включая получение информации о счёте и исторических данных о котировках.
    Используется в слое приложения для изоляции от конкретной реализации клиента.
    """

    @abstractmethod
    async def get_account_summary(self) -> 'AccountSummaryModel':
        """Возвращает сводную информацию о счетах пользователя.

        Возвращает агрегированную модель, включающую количество счетов
        и их уникальные идентификаторы.

        Returns:
            Модель AccountSummaryModel с данными о счетах.
        """
        pass

    @abstractmethod
    async def get_candles_by_isin(self, isin: str, from_date: 'date', to_date: 'date') -> 'Sequence[CandleModel]':
        """Возвращает историю котировок по ISIN за указанный период.

        Используется для получения дневных OHLCV-данных (открытие, максимум,
        минимум, закрытие, объём) за заданный временной интервал.

        Args:
            isin: Международный идентификатор ценной бумаги (ISIN).
            from_date: Начальная дата интервала.
            to_date: Конечная дата интервала.

        Returns:
            Последовательность моделей CandleModel, представляющих данные по свечам.
        """
        pass

    @abstractmethod
    async def verify_token(self, debug: bool = False) -> bool:
        """Проверяет действительность токена Tinkoff Invest API.

        При включенном debug режиме также выводит подробную отладочную
        информацию: список счетов, лимиты, тарифы и сведения о пользователе.

        Args:
            debug: Если True, включается вывод отладочной информации.

        Returns:
            True, если токен действителен. Иначе False.
        """
        pass

    @abstractmethod
    async def get_portfolio(self, account_id: str) -> 'PortfolioModel':
        """Возвращает актуальное состояние портфеля пользователя.

        Args:
            account_id: Идентификатор счёта.

        Returns:
            Модель PortfolioModel с информацией о бумагах, позициях и их стоимости.
        """
        pass
