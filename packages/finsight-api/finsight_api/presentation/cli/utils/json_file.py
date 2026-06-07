"""Утилиты для сохранения объектов в JSON-файлы.

Модуль предоставляет безопасную сериализацию доменных/прикладных DTO в JSON,
с корректной обработкой Decimal и datetime.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any


def write_json_file(*, obj: Any, path: Path) -> None:
    """Сохраняет объект в JSON-файл.

    Сериализация:
    - dataclass -> asdict
    - Decimal -> str (без потери точности)
    - datetime/date -> ISO 8601
    - Enum -> value
    - Path -> str
    - set/tuple -> list

    Запись выполняется атомарно: сначала во временный файл, затем replace.

    Args:
        obj: Объект для сериализации (обычно Output DTO use case).
        path: Путь к JSON-файлу (будут созданы родительские директории).

    Raises:
        OSError: Если не удалось создать директории или записать файл.
        TypeError: Если объект не сериализуем в JSON.
    """
    data = _normalize_json_obj(obj)
    content = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        default=_json_default,
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + '.tmp')

    tmp_path.write_text(content, encoding='utf-8')
    tmp_path.replace(path)


def _normalize_json_obj(obj: Any) -> Any:
    """Нормализует объект перед JSON-сериализацией.

    Args:
        obj: Любой объект.

    Returns:
        Any: JSON-совместимая структура.
    """
    if is_dataclass(obj):
        return _normalize_json_obj(asdict(obj))
    if isinstance(obj, dict):
        return {str(k): _normalize_json_obj(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_normalize_json_obj(v) for v in obj]
    return obj


def _json_default(value: Any) -> Any:
    """Обработчик неизвестных JSON-типов для json.dumps(default=...).

    Args:
        value: Значение.

    Returns:
        Any: JSON-совместимое значение.

    Raises:
        TypeError: Если тип не поддерживается.
    """
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f'Object of type {type(value).__name__} is not JSON serializable')
