RUN_FILENAME = run_bot.py
CODE = $(RUN_FILENAME) src/
POETRY_CMD = poetry run
EXCLUDE =

.PHONY: format run test lint clean

format:
	$(POETRY_CMD) black $(CODE) --exclude=$(EXCLUDE)
	$(POETRY_CMD) isort $(CODE) --skip=$(EXCLUDE)

run:
	$(POETRY_CMD) python $(RUN_FILENAME)

test:
	$(POETRY_CMD) pytest -k "$(TEST_NAME)" -m "$(MARKERS)" -q --cov=$(CODE) --cov-report=term-missing

lint:
	$(POETRY_CMD) ruff check $(CODE) --exclude=$(EXCLUDE)

clean:
	find . -type d -name "__pycache__" ! -path "./.venv/*" -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name "*.pyd" \) ! -path "./.venv/*" -delete
	rm -rf .coverage .pytest_cache .ruff_cache
