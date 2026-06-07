"""Модуль содержит тип-значение агентства кредитного рейтинга."""

from enum import auto, StrEnum, unique


# TODO: Не уверен, что это VO на уровне домена
@unique
class CreditRatingAgency(StrEnum):
    """Агентство кредитного рейтинга.

    Используем строковое перечисление для удобной сериализации и хранения.

    Attributes:
        ACRA: АКРА.
        EXPERT: Эксперт РА.
    """

    ACRA = auto()
    EXPERT = auto()
