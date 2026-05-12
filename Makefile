all: run


run:
	python3 fly_in.py maps/hard/01_maze_nightmare.txt

visual:
	python3 visualizer.py maps/challenger/01_the_impossible_dream.txt

debug:

install:

clean:

lint:
	flake8
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
