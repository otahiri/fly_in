"""Command-line entry point for the fly-in drone simulation."""

import sys
from typing import List
from graph_creation import Drone, Graph
from parsing import ParsingError
from algo import Dijkestra, MapError
from visualize import Renderer


def main() -> None:
    """Run the simulation loop

    The function reads the map file, strips blank lines and comments,
    builds the graph model, executes moves routing, and prints
    them for each turn until every drone reaches the finish hub.

    Returns:
        None

    Raises:
        ParsingError: If the input map content is invalid.
        IsADirectoryError: If the provided path points to a directory.
        PermissionError: If the map file cannot be read.
        FileNotFoundError: If the map file path does not exist.
    """
    lines = list()

    with open(sys.argv[1], "r") as map:
        lines = [
            line.strip()
            for line in map
            if len(line.strip()) and not line.strip().startswith("#")
        ]
        if not lines:
            raise ParsingError("empty map")
        lines = [line[0:line.index('#')].strip()
                 if '#' in line else line.strip() for line in lines]
    graph = Graph(lines)
    drones: List[Drone] = graph.drones
    while True:
        if graph.finish.size == graph.drone_num:
            break
        for drone in drones:
            if drone.in_transit or drone.destination is not None:
                drone.distance_to_finish = float('inf')
            else:
                path = Dijkestra.algo(graph, drone)
                drone.distance_to_finish = len(path) if path else float('inf')
        for drone in sorted(graph.drones, key=lambda x: x.distance_to_finish):
            drone.choose_zone(graph)
        for drone in sorted(graph.drones, key=lambda x: (x.path_len, x.id)):
            drone.move_drone()
        Renderer.print_moves(graph)
        print()


if __name__ == "__main__":
    try:
        main()
    except (
        ParsingError,
        MapError,
        IsADirectoryError,
        PermissionError,
        FileNotFoundError,
    ) as e:
        print(e, file=sys.stderr)
    except (KeyboardInterrupt):
        print("Exit by user")
    except Exception as e:
        print(e)
