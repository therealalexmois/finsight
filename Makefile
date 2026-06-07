.PHONY: \
	install install-dev sync \
	lint lint-fix lint-format lint-format-check lint-and-format \
	test test-with-coverage \
	type-check type-check-pyrefly type-check-pyrefly-watch \
	check-project \
	install-pre-commit pre-commit \
	clean \
	ci-checks \
	default \
	finsight-api-start finsight-api-dev finsight-worker-start

UV := uv
RUN := uv run

# Установка всех зависимостей workspace (все пакеты + группы dev/lint/test)
install:
	@echo "Синхронизация зависимостей workspace через uv..."
	@$(UV) sync

install-dev: install
sync: install

check-project:
	@echo "Проверка блокировки и хуков"
	@$(UV) lock --check
	@$(RUN) pre-commit run --all-files

build:
	@$(UV) build --all-packages

# Линтинг
lint:
	@echo "Линтинг кода с помощью Ruff"
	@$(RUN) ruff check .

lint-fix:
	@echo "Линтинг кода с исправлениями с помощью Ruff"
	@$(RUN) ruff check . --fix

lint-format:
	@echo "Форматирование кода с помощью Ruff"
	@$(RUN) ruff format .

lint-format-check:
	@$(RUN) ruff format . --check

lint-and-format: lint-fix lint-format

# Проверка типов (mypy strict)
type-check:
	@$(RUN) mypy --config-file=mypy.ini

# Быстрая проверка типов pyrefly
type-check-pyrefly:
	@$(RUN) pyrefly check

# Фоновая проверка типов pyrefly в режиме watch
type-check-pyrefly-watch:
	@$(RUN) pyrefly check --watch

# Тесты
test:
	@$(RUN) pytest -p no:cacheprovider $(ARGS)

test-with-coverage:
	@$(RUN) pytest -p no:cacheprovider --cov-report=term-missing $(ARGS)

# pre-commit
install-pre-commit:
	@$(RUN) pre-commit install

pre-commit:
	@$(RUN) pre-commit run --all-files

# Очистка
clean:
	@find . -name "__pycache__" -type d -exec rm -rf {} +
	@rm -rf .mypy_cache .pytest_cache .ruff_cache .coverage htmlcov log/ reports/

ci-checks: lint type-check

# Запуск сервисов
finsight-api-start:
	@$(RUN) finsight-api server start

finsight-api-dev:
	@$(RUN) finsight-api server start --reload

finsight-worker-start:
	@$(RUN) finsight-worker worker start

default: install
