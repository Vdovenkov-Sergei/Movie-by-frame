APP_NAME = run_bot
CODE_PY = $(APP_NAME).py src/ tests/
CODE_IPYNB = notebooks/

MAX_LINE_LENGTH = 120
FAILS = 1

.PHONY: format run test update lint clean

format:
	poetry run black --line-length $(MAX_LINE_LENGTH) $(CODE_PY) $(CODE_IPYNB)

run:
	poetry run python $(APP_NAME).py

test:
	poetry run pytest -k "$(TEST_NAME)" -m "$(MARKERS)" --maxfail=$(FAILS) -q --cov=src/ --cov-report=term-missing

update:
	poetry update

lint:
	-poetry run flake8 $(CODE_PY) --max-line-length=$(MAX_LINE_LENGTH) --verbose
	poetry run nbqa flake8 --color=always $(CODE_IPYNB) --max-line-length=$(MAX_LINE_LENGTH) --verbose

clean:
	rm -rf **/__pycache__ **/*.pyc **/*.pyo .coverage .pytest_cache