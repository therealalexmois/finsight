.PHONY: \
	start \
	install install-dev install-test \
	lint lint-fix lint-format lint-format-check lint-and-format \
	test test-with-coverage \
	type-check \
	check-project \
	install-pre-commit pre-commit \
	clean \
	ci-checks \
	default \
	activate

PYTHON := poetry run python
POETRY := poetry
PRE_COMMIT := poetry run pre-commit
RUFF := poetry run ruff
PYTEST := poetry run pytest
MYPY := poetry run mypy

# Активировать виртуальную среду
activate:
	@echo "Выполните следующую команду в оболочке, чтобы активировать среду:"
	@echo "$$(poetry env activate)"

check-project:
	@echo "Проверка целостности pyproject.toml и poetry.lock"
	@$(POETRY) check --lock
	@echo "Запуск хуков по всем файлам"
	@$(PRE_COMMIT) run --all-files

# Установка всех зависимостей
install:
	@echo "Установка всех зависимостей..."
	@$(POETRY) install

# Установка dev зависимостей
install-dev:
	@echo "Установка dev зависимостей..."
	@$(POETRY) install --with dev

# Установка test зависимостей
install-test:
	@echo "Установка test зависимостей..."
	@$(POETRY) install --with test

build:
	@$(POETRY) build

# Запуск линтера
lint:
	@echo "Линтинг кода с помощью Ruff"
	@$(RUFF) check .

# Запуск линтера и исправление ошибок
lint-fix:
	@echo "Линтинг кода с исправлениями с помощью Ruff"
	@$(RUFF) check . --fix

# Форматирование кода
lint-format:
	@echo "Форматирование кода с помощью Ruff"
	@$(RUFF) format .

# Форматирование кода и исправление
lint-format-check:
	@echo "Список файлов, которые Ruff может отформатировать"
	@$(RUFF) format . --check

lint-and-format: lint-fix lint-format

# Запуск проверки типов
type-check:
	@$(MYPY) --config-file=pyproject.toml --no-incremental src tests

# Запуск тестов
test:
	$(PYTEST) -p no:cacheprovider $(ARGS)

# Запуск тестов с покрытием
test-with-coverage:
	$(PYTEST) -p no:cacheprovider --cov=src --cov-report=term-missing $(ARGS)

# Установка pre-commit hooks
install-pre-commit:
	@$(PRE_COMMIT) install

# Запуск pre-commit hooks
pre-commit:
	@$(PRE_COMMIT) run --all-files

# Очистка кэша и временных файлов
clean:
	@find . -name "__pycache__" -type d -exec rm -rf {} +
	@rm -rf .mypy_cache .pytest_cache .coverage htmlcov .ruff_cache log/ reports/

ci-checks: lint type-check

start:
	$(PYTHON) -m src.app.main $(ARGS)

# Цель по умолчанию (установка зависимостей)
default: install
