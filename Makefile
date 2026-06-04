.PHONY: all run debug install clean lint

MAP= maps/easy//01_linear_path.txt



all: run


run:
	@uv run python3 fly_in.py $(MAP)

debug:
	python3 -m pdb fly_in.py $(MAP)

install:
	uv sync

clean:
	rm -rf .mypy_cache __pycache__

lint:
	uv run flake8 --exclude .venv .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
