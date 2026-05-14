MAP= maps/easy//01_linear_path.txt



all: run


run:
	uv run python3 fly_in.py $(MAP)

visual:
	python3 visualizer.py $(MAP)

debug:
	python3 -m pdb fly_in.py $(MAP)

install:

clean:
	rm -rf .mypy_cache __pycache__

lint:
	flake8
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
