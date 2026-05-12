import sys
from graph_creation import Drone, Graph, Hub
from parsing import ParsingError
from algo import Dijkestra
import time


def main():
    step = 0
    lines = list()
    choice = None
    with open(sys.argv[1], "r") as map:
        lines = [
            line.strip()
            for line in map
            if len(line.strip()) and not line.strip().startswith("#")
        ]
    graph = Graph(lines)
    Dijkestra.choose_zone(graph.drones[0], graph)


if __name__ == "__main__":
    try:
        main()
    except (
        ParsingError,
        IsADirectoryError,
        PermissionError,
        FileNotFoundError,
    ) as e:
        print(e)
