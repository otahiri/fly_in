import sys
from graph_creation import Drone, Graph, Hub
from parsing import ParsingError
import algo
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
    while True:
        if all([drone.zone == graph.finish for drone in graph.drones]):
            break
        print(", ".join([' '.join([drone.zone.name, str(drone.zone.size)]) for drone in graph.drones]))
        step += 1
        print(step)
        for drone in graph.drones:
            if drone.zone == graph.finish:
                continue
            choice = algo.Algo.dijkestra(graph, drone.zone, graph.finish)
            drone.choose_zone(choice)
        for drone in graph.drones:
            if drone.zone == graph.finish:
                continue
            drone.move_drone()
    print(", ".join([drone.zone.name for drone in graph.drones]))


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
