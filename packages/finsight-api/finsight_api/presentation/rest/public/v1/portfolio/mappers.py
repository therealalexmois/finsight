"""Маппер для преобразования доменной модели портфеля в схему ответа API."""

from typing import TYPE_CHECKING

from .schemas import PortfolioResponse, Position

if TYPE_CHECKING:
    from finsight_api.domain.entities.portfolio import PortfolioEntity


def map_portfolio_to_response(model: 'PortfolioEntity') -> PortfolioResponse:
    """Преобразует доменную модель портфеля в схему ответа API.

    Args:
        model: Доменная модель портфеля.

    Returns:
        Объект PortfolioResponse, совместимый с Pydantic.
    """
    return PortfolioResponse(
        positions=[
            Position(
                ticker=position.figi,
                instrument_name='UNKNOWN',  # Заглушка, пока имя инструмента не извлекается
                balance=float(position.quantity),
                current_price=float(position.current_price),
                currency='UNKNOWN',  # Заглушка, пока валюта не извлекается
            )
            for position in model.positions
        ]
    )
