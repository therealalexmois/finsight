"""DTO для преобразования позиции портфеля из формата Tinkoff Invest SDK в доменную модель."""

from decimal import Decimal
from typing import TYPE_CHECKING

from src.app.domain.value_objects.portfolio_position import PortfolioPosition

if TYPE_CHECKING:
    from tinkoff.invest import PortfolioPosition as SDKPortfolioPosition


class PortfolioPositionDTO:
    """DTO для преобразования позиции портфеля из SDK Tinkoff в доменную модель."""

    def __init__(  # noqa: PLR0913
        self,
        figi: str,
        instrument_type: str,
        quantity: Decimal,
        expected_yield: Decimal,
        average_position_price: Decimal,
        current_price: Decimal,
        value: Decimal,
        instrument_uid: str,
    ) -> None:
        """Инициализирует DTO модели позиции портфеля.

        Args:
            figi: FIGI инструмента.
            instrument_type: Тип инструмента (например, bond, share).
            quantity: Количество лотов.
            expected_yield: Ожидаемая доходность.
            average_position_price: Средняя цена позиции.
            current_price: Текущая цена.
            value: Общая стоимость позиции.
            instrument_uid: Уникальный идентификатор инструмента.
        """
        self.figi = figi
        self.instrument_type = instrument_type
        self.quantity = quantity
        self.expected_yield = expected_yield
        self.average_position_price = average_position_price
        self.current_price = current_price
        self.value = value
        self.instrument_uid = instrument_uid

    @classmethod
    def from_sdk(cls, position: 'SDKPortfolioPosition') -> 'PortfolioPositionDTO':
        """Создаёт DTO из объекта PortfolioPosition SDK.

        Args:
            position: Объект позиции из Tinkoff Invest SDK.

        Returns:
            DTO, содержащий необходимые поля для бизнес-логики.
        """
        return cls(
            figi=position.figi,
            instrument_type=position.instrument_type,
            quantity=Decimal(position.quantity.units),
            expected_yield=Decimal(position.expected_yield.units),
            average_position_price=Decimal(position.average_position_price.units),
            current_price=Decimal(position.current_price.units),
            value=Decimal(position.current_price.units) * Decimal(position.quantity.units),
            instrument_uid=position.instrument_uid,
        )

    def to_model(self) -> PortfolioPosition:
        """Преобразует DTO в доменный value object PortfolioPosition.

        Returns:
            Доменный объект PortfolioPosition.
        """
        return PortfolioPosition(
            figi=self.figi,
            instrument_type=self.instrument_type,
            quantity=self.quantity,
            expected_yield=self.expected_yield,
            average_position_price=self.average_position_price,
            current_price=self.current_price,
            value=self.value,
            instrument_uid=self.instrument_uid,
        )
