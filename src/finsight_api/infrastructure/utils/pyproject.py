"""Утилиты для извлечения данных из pyproject.toml."""

import logging
import tomllib
from pathlib import Path
from typing import cast

logger = logging.getLogger(__name__)


def find_pyproject_path(start: Path | None = None) -> Path:
    """Ищет файл pyproject.toml в текущей и родительских директориях.

    Args:
        start: Начальная директория для поиска. По умолчанию используется текущая рабочая директория.

    Returns:
        Путь до найденного файла pyproject.toml.

    Raises:
        FileNotFoundError: Если файл pyproject.toml не найден ни в одной из родительских директорий.
    """
    path = start or Path.cwd()
    for parent in [path] + list(path.parents):
        candidate = parent / 'pyproject.toml'
        if candidate.exists():
            return candidate

    raise FileNotFoundError('pyproject.toml не найден ни в одной из родительских директорий.')


def extract_project_field(field_name: str, app_config_path: 'Path') -> str | None:
    """Извлекает поле из секции [project] файла pyproject.toml.

    Args:
        field_name: Название поля (например, 'name', 'version').
        app_config_path: Путь к pyproject.toml.

    Returns:
        Значение поля в виде строки.

    Raises:
        OSError: Ошибка при открытии файла.
        tomllib.TOMLDecodeError: Ошибка при разборе TOML.
        KeyError: Указанное поле не найдено.
    """
    try:
        with open(app_config_path, 'rb') as file:
            data = tomllib.load(file)
            return cast('str', data['project'][field_name])
    except OSError as error:
        logger.error(f'Ошибка при открытии {app_config_path}: {error}')
        raise
    except tomllib.TOMLDecodeError as error:
        logger.error(f'Ошибка при разборе TOML файла {app_config_path}: {error}')
        raise
    except KeyError as error:
        logger.error(f'Поле {field_name!r} не найдено в секции [project] файла {app_config_path}: {error}')
        raise
