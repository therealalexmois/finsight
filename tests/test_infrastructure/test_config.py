import tomllib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from pytest import MonkeyPatch

import pytest

from src.app.domain.constants import AppEnv, LogLevel
from src.app.infrastructure.config import _extract_project_field, Settings


@pytest.mark.unit
class TestConfig:
    @staticmethod
    @pytest.fixture()
    def sample_pyproject(tmp_path: 'Path') -> 'Path':
        """Создает временный pyproject.toml с базовой конфигурацией."""
        content = """
        [project]
        name = "finsight"
        version = "1.2.3"
        """
        file_path = tmp_path / 'pyproject.toml'
        file_path.write_text(content.strip())
        return file_path

    @staticmethod
    def test_extract_name__ok(sample_pyproject: 'Path') -> None:
        """Должен корректно извлекать поле name."""
        result = _extract_project_field('name', sample_pyproject)
        assert result == 'finsight'

    @staticmethod
    def test_extract_version__ok(sample_pyproject: 'Path') -> None:
        """Должен корректно извлекать поле version."""
        result = _extract_project_field('version', sample_pyproject)
        assert result == '1.2.3'

    @staticmethod
    def test_missing_field__raises_key_error(sample_pyproject: 'Path') -> None:
        """Должен выбрасывать KeyError при отсутствии поля."""
        with pytest.raises(KeyError):
            _extract_project_field('description', sample_pyproject)

    @staticmethod
    def test_invalid_toml__raises_error(tmp_path: 'Path') -> None:
        """Должен выбрасывать TOMLDecodeError при неверном синтаксисе TOML."""
        bad_file = tmp_path / 'pyproject.toml'
        bad_file.write_text('not a valid TOML file')

        with pytest.raises(tomllib.TOMLDecodeError):
            _extract_project_field('name', bad_file)

    @staticmethod
    def test_load_settings_from_env__ok(monkeypatch: 'MonkeyPatch') -> None:
        """Должен загружать настройки из переменных окружения."""
        monkeypatch.setenv('APP_ENV', 'dev')
        monkeypatch.setenv('APP_HOST', '0.0.0.0')
        monkeypatch.setenv('APP_PORT', '9000')
        monkeypatch.setenv('APP_LOG_LEVEL', 'info')

        settings = Settings()

        test_port = 9000

        assert settings.app.env == AppEnv.DEV
        assert settings.app.host == '0.0.0.0'
        assert settings.app.port == test_port
        assert settings.logging.level == LogLevel.INFO
