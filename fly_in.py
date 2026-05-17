"""CLI entrypoint for running the fly-in drone simulation."""

import sys
from graph_creation import Graph
from parsing import ParsingError
from algo import Dijkestra
from visualize import Renderer


def main() -> None:
    """Load a map file, run turns, and print drone movements."""
    lines = list()

    with open(sys.argv[1], "r") as map:
        lines = [
            line.strip()
            for line in map
            if len(line.strip()) and not line.strip().startswith("#")
        ]
    graph = Graph(lines)
    while True:
        if graph.finish.size == graph.drone_num:
            break
        for drone in graph.drones:
            Dijkestra.choose_zone(drone, graph)
        for drone in sorted(graph.drones, key=lambda x: len(x.path))[::-1]:
            Dijkestra.move_drone(drone)
        if any([drone.moved for drone in graph.drones]):
            Renderer.print_moves(graph)
            print()


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
