"""Схемы ответа API для отображения данных портфеля пользователя.

Содержит модели ответа `PortfolioResponse` и `Position`, используемые в endpoint'ах
для представления списка позиций по тикерам, количеству лотов, текущей цене и валюте.
"""

from collections.abc import Sequence

from pydantic import BaseModel


class Position(BaseModel):
    """Позиция в портфеле.

    Attributes:
        ticker: Тикер инструмента.
        instrument_name: Название инструмента.
        balance: Количество лотов.
        current_price: Текущая цена одного лота.
        currency: Валюта инструмента.
    """

    ticker: str
    instrument_name: str
    balance: float
    current_price: float
    currency: str


class PortfolioResponse(BaseModel):
    """Ответ с данными о портфеле пользователя.

    Attributes:
        positions: Список позиций в портфеле.
    """

    positions: Sequence[Position]

    model_config = {
        'title': 'PortfolioResponse',
        'json_schema_extra': {
            'example': {
                'positions': [
                    {
                        'ticker': 'SBER',
                        'instrument_name': 'Сбербанк',
                        'balance': 10.5,
                        'current_price': 251.34,
                        'currency': 'RUB',
                    },
                    {
                        'ticker': 'YNDX',
                        'instrument_name': 'Яндекс',
                        'balance': 3.0,
                        'current_price': 2934.0,
                        'currency': 'RUB',
                    },
                ]
            }
        },
    }
