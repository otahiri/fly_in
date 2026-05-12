all: run


run:
	python3 fly_in.py maps/hard/03_ultimate_challenge.txt

debug:

install:

clean:

lint:
	flake8
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
