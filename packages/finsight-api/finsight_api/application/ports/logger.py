"""Интерфейс логгера для использования в приложении."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class LoggerPort(ABC):
    """Интерфейс логгера, абстрагирующий реализацию логирования."""

    @abstractmethod
    def info(self, event: str, **kwargs: 'Any') -> None:
        """Логирует информационное сообщение.

        Args:
            event: Имя или текст события.
            **kwargs: Дополнительные структурированные поля записи.
        """
        pass

    @abstractmethod
    def warning(self, event: str, **kwargs: 'Any') -> None:
        """Логирует предупреждение.

        Args:
            event: Имя или текст события.
            **kwargs: Дополнительные структурированные поля записи.
        """
        pass

    @abstractmethod
    def error(self, event: str, **kwargs: 'Any') -> None:
        """Логирует ошибку.

        Args:
            event: Имя или текст события.
            **kwargs: Дополнительные структурированные поля записи.
        """
        pass

    @abstractmethod
    def clear_context_vars(self) -> None:
        """Очищает все привязанные контекстные переменные."""
        pass

    @abstractmethod
    def bind_context_vars(self, **kwargs: 'Any') -> None:
        """Добавляет переменные в контекст логгера.

        Args:
            **kwargs: Контекстные переменные, добавляемые ко всем последующим записям.
        """
        pass

    @abstractmethod
    def unbind_context_vars(self, *keys: str) -> None:
        """Удаляет переменные из контекста логгера по ключам.

        Args:
            *keys: Ключи контекстных переменных для удаления.
        """
        pass
