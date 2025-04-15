"""Маппер для преобразования доменной модели портфеля в схему ответа API."""

from typing import TYPE_CHECKING

from src.finsight_api.presentation.schemas.portfolio import PortfolioResponse, Position

if TYPE_CHECKING:
    from src.finsight_api.domain.models.portfolio import PortfolioModel


def map_portfolio_to_response(model: 'PortfolioModel') -> PortfolioResponse:
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
                instrument_name='—',  # Заглушка, пока имя инструмента не извлекается
                balance=float(position.quantity),
                current_price=float(position.current_price),
                currency='—',  # Заглушка, пока валюта не извлекается
            )
            for position in model.positions
        ]
    )
