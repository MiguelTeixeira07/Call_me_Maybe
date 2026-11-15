VENV := .venv/bin/

FUNC_DEF := data/input/functions_definition.json
PROMPTS := data/input/function_calling_tests.json
OUTPUT := data/output/function_calling_results.json


export UV_PROJECT_ENVIRONMENT := .venv

install:
	python3 -m venv .venv
	$(VENV)python -m pip install uv
	$(VENV)uv sync
	mkdir -p data/output


run: install
	$(VENV)uv run python3 -m src \
	--functions_definition $(FUNC_DEF) \
	--input $(PROMPTS) \
	--output $(OUTPUT)


debug: install
	$(VENV_PY) -m pdb -m src \
	--functions_definition $(FUNC_DEF) \
	--input $(PROMPTS) \
	--output $(OUTPUT)


clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache .ruff_cache .venv data/output
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -f uv.lock


lint: install
	$(VENV)flake8 src
	$(VENV)mypy src \
		--warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs


lint-strict: install
	$(VENV)flake8 src
	$(VENV)mypy src --strict


.PHONY: install run debug clean lint lint-strict
