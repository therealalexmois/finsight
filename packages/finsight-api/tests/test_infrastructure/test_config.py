import tomllib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from pytest import MonkeyPatch

import pytest

from finsight_api.domain.constants import AppEnv, LogLevel
from finsight_api.infrastructure.config import (
    _BASE_ENV_PREFIX as BASE_ENV_PREFIX,
)
from finsight_api.infrastructure.config import Settings
from finsight_api.infrastructure.container import AppContainer
from finsight_api.infrastructure.utils.pyproject import extract_project_field


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
        result = extract_project_field('name', sample_pyproject)
        assert result == 'finsight'

    @staticmethod
    def test_extract_version__ok(sample_pyproject: 'Path') -> None:
        """Должен корректно извлекать поле version."""
        result = extract_project_field('version', sample_pyproject)
        assert result == '1.2.3'

    @staticmethod
    def test_missing_field__raises_key_error(sample_pyproject: 'Path') -> None:
        """Должен выбрасывать KeyError при отсутствии поля."""
        with pytest.raises(KeyError):
            extract_project_field('description', sample_pyproject)

    @staticmethod
    def test_invalid_toml__raises_error(tmp_path: 'Path') -> None:
        """Должен выбрасывать TOMLDecodeError при неверном синтаксисе TOML."""
        bad_file = tmp_path / 'pyproject.toml'
        bad_file.write_text('not a valid TOML file')

        with pytest.raises(tomllib.TOMLDecodeError):
            extract_project_field('name', bad_file)

    @staticmethod
    def test_load_settings_from_env__ok(monkeypatch: 'MonkeyPatch') -> None:
        """Должен загружать вложенные настройки из переменных окружения."""
        monkeypatch.setenv(f'{BASE_ENV_PREFIX}APP__ENV', 'dev')
        monkeypatch.setenv(f'{BASE_ENV_PREFIX}APP__HOST', '0.0.0.0')
        monkeypatch.setenv(f'{BASE_ENV_PREFIX}APP__PORT', '9000')
        monkeypatch.setenv(f'{BASE_ENV_PREFIX}LOGGING__LOG_LEVEL', 'info')
        monkeypatch.setenv(f'{BASE_ENV_PREFIX}TINKOFF_INVEST_API__TOKEN', 'test-token')

        settings = Settings()

        test_port = 9000

        assert settings.app.env == AppEnv.DEV
        assert settings.app.host == '0.0.0.0'
        assert settings.app.port == test_port
        assert settings.logging.log_level == LogLevel.INFO

    @staticmethod
    def test_invalid_app_env_raises_error(monkeypatch: 'MonkeyPatch') -> None:
        """Должен выбрасывать ошибку валидации при некорректном APP_APP__ENV."""
        monkeypatch.setenv(f'{BASE_ENV_PREFIX}TINKOFF_INVEST_API__TOKEN', 'test-token')
        monkeypatch.setenv(f'{BASE_ENV_PREFIX}APP__ENV', 'invalid_env')
        with pytest.raises(ValueError):
            _ = Settings()

    @staticmethod
    def test_invalid_log_level_raises_error(monkeypatch: 'MonkeyPatch') -> None:
        """Должен выбрасывать ошибку валидации при некорректном APP_LOGGING__LOG_LEVEL."""
        monkeypatch.setenv(f'{BASE_ENV_PREFIX}TINKOFF_INVEST_API__TOKEN', 'test-token')
        monkeypatch.setenv(f'{BASE_ENV_PREFIX}LOGGING__LOG_LEVEL', 'invalid_level')
        with pytest.raises(ValueError):
            _ = Settings()

    @staticmethod
    def test_get_settings_is_cached(monkeypatch: 'MonkeyPatch') -> None:
        """Должен возвращать один и тот же экземпляр настроек (Singleton)."""
        monkeypatch.setenv(f'{BASE_ENV_PREFIX}TINKOFF_INVEST_API__TOKEN', 'test-token')
        AppContainer.settings.reset()
        settings1 = AppContainer.settings()

        monkeypatch.setenv(f'{BASE_ENV_PREFIX}APP__PORT', '1234')

        settings2 = AppContainer.settings()

        assert settings1 is settings2
