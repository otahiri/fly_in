all: run


run:
	python3 fly_in.py maps/easy/01_linear_path.txt

debug:

install:

clean:

lint:
	flake8
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
