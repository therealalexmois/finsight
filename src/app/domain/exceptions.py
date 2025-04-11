"""Доменные ошибки, связанные с бизнес-логикой."""

from http import HTTPStatus


class BaseAppError(Exception):
    """Базовая ошибка приложения."""

    def __init__(self, message: str, status_code: HTTPStatus = HTTPStatus.BAD_REQUEST) -> None:
        """Инициализирует ошибку приложения с сообщением и HTTP-статусом.

        Args:
            message: Текстовое описание ошибки.
            status_code: HTTP-код, возвращаемый клиенту.
        """
        self.message = message
        self.status_code = int(status_code)
