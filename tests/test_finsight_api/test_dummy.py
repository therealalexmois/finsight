import pytest


@pytest.mark.critical
def test_dummy__always_passes() -> None:
    """Проверяет, что критический тест срабатывает корректно."""
    assert True
