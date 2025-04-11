"""Интерфейс логгера для использования в приложении."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class Logger(ABC):
    """Интерфейс логгера, абстрагирующий реализацию логирования."""

    @abstractmethod
    def info(self, event: str, **kwargs: 'Any') -> None:
        """Логирует информационное сообщение."""
        pass

    @abstractmethod
    def warning(self, event: str, **kwargs: 'Any') -> None:
        """Логирует предупреждение."""
        pass

    @abstractmethod
    def error(self, event: str, **kwargs: 'Any') -> None:
        """Логирует ошибку."""
        pass

    @abstractmethod
    def clear_context_vars(self) -> None:
        """Очищает все привязанные контекстные переменные."""
        pass

    @abstractmethod
    def bind_context_vars(self, **kwargs: 'Any') -> None:
        """Добавляет переменные в контекст логгера."""
        pass

    @abstractmethod
    def unbind_context_vars(self, *keys: str) -> None:
        """Удаляет переменные из контекста логгера по ключам."""
        pass
