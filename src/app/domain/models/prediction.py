"""Модель прогноза движения цены акции."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date
    from uuid import UUID

    from src.app.domain.value_objects.isin import ISIN
    from src.app.domain.value_objects.prediction_direction import PredictionDirection


@dataclass(frozen=True)
class Prediction:
    """Модель прогноза движения цены по акции."""

    id: 'UUID'
    isin: 'ISIN'
    date: 'date'
    direction: 'PredictionDirection'
    confidence: float
