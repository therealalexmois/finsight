"""Адаптер парсинга кредитных рейтингов с analytics.dohod.ru.

Источник: публичные страницы вида https://analytics.dohod.ru/bond/<ISIN>.
Извлекаем рейтинги только от АКРА и Эксперт РА.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

import httpx

from finsight_api.application.ports.credit_ratings import CreditRatingsPort
from finsight_api.domain.value_objects.credit_rating_agency import CreditRatingAgency
from finsight_api.domain.value_objects.credit_ratings import CreditRating, CreditRatings

if TYPE_CHECKING:
    from finsight_api.application.ports.logger import LoggerPort
    from finsight_api.domain.value_objects.isin import ISIN


_ACRA_PATTERN = re.compile(r'АКРА\s*-\s*([^\(\r\n]+)')
_EXPERT_PATTERN = re.compile(r'Эксперт\s*-\s*([^\(\r\n]+)')


@dataclass(frozen=True, slots=True, kw_only=True)
class DohodAdapterSettings:
    """Настройки адаптера.

    Attributes:
        base_url: Базовый URL страниц аналитики.
        timeout_seconds: Таймаут HTTP-запросов в секундах.
    """

    base_url: str = 'https://analytics.dohod.ru'
    timeout_seconds: float = 10.0


class DohodCreditRatingsAdapter(CreditRatingsPort):
    """Реализация порта CreditRatingsPort поверх публичных страниц analytics.dohod.ru.

    Загружает HTML страницы облигации по ISIN и извлекает рейтинги агентств АКРА
    и Эксперт РА регулярными выражениями. Сетевые ошибки не пробрасываются: при
    сбое запроса возвращается пустой набор рейтингов и пишется warning в лог.
    """

    def __init__(
        self,
        *,
        http: httpx.AsyncClient,
        logger: LoggerPort,
        settings: DohodAdapterSettings | None = None,
    ) -> None:
        """Инициализирует адаптер.

        Args:
            http: Асинхронный HTTP-клиент.
            logger: Логгер приложения.
            settings: Настройки адаптера. Если None — используются настройки по умолчанию.
        """
        self._http = http
        self._logger = logger
        self._settings = settings or DohodAdapterSettings()

    async def get_ratings(self, *, isin: ISIN) -> CreditRatings:
        """Возвращает кредитные рейтинги для указанного ISIN.

        Логика:
        - Загружает страницу analytics.dohod.ru/bond/<ISIN>
        - Парсит текстовые вхождения блоков "АКРА - ..." и "Эксперт - ..."
        - Возвращает CreditRatings (может быть пустым)

        Args:
            isin: ISIN инструмента.

        Returns:
            CreditRatings: Набор рейтингов (может быть пустым).
        """
        url = f'{self._settings.base_url}/bond/{isin.value}'

        try:
            response = await self._http.get(
                url,
                headers={'User-Agent': 'FinSight/1.0'},
                timeout=self._settings.timeout_seconds,
            )
            response.raise_for_status()
        except Exception as exc:
            # Ошибка не должна “ронять” приложение без явного решения выше.
            # Возвращаем пустой набор и логируем причину.
            self._logger.warning(f'Failed to fetch dohod.ru ratings: url={url} error={exc!r}')
            return CreditRatings.empty()

        items = self._parse_ratings_from_html(response.text)
        return CreditRatings.from_iterable(items)

    def _parse_ratings_from_html(self, html: str) -> tuple[CreditRating, ...]:
        """Извлекает рейтинги АКРА и Эксперт РА из HTML страницы.

        Args:
            html: HTML страницы analytics.dohod.ru.

        Returns:
            tuple[CreditRating, ...]: Найденные рейтинги (может быть пустым).
        """
        # Страницы dohod.ru содержат человекочитаемый текст рейтингов в HTML.
        # Парсим регулярными выражениями без зависимостей на HTML-парсеры.
        acra = self._extract_one(_ACRA_PATTERN, html)
        expert = self._extract_one(_EXPERT_PATTERN, html)

        items: list[CreditRating] = []
        if acra is not None:
            items.append(CreditRating(agency=CreditRatingAgency.ACRA, value=acra))
        if expert is not None:
            items.append(CreditRating(agency=CreditRatingAgency.EXPERT, value=expert))

        return tuple(items)

    @staticmethod
    def _extract_one(pattern: re.Pattern[str], text: str) -> str | None:
        """Извлекает одно значение по паттерну и нормализует пробелы.

        Args:
            pattern: Компилированный паттерн.
            text: Текст для поиска.

        Returns:
            str | None: Значение или None.
        """
        match = pattern.search(text)
        if match is None:
            return None
        value = match.group(1).strip()
        # Нормализация: удаляем неразрывные пробелы и двойные пробелы.
        value = value.replace('\xa0', ' ')
        value = re.sub(r'\s+', ' ', value).strip()
        return value or None
