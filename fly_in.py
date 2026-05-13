import sys
from graph_creation import Graph
from parsing import ParsingError
from algo import Dijkestra


def main():
    step = 0
    lines = list()
    with open(sys.argv[1], "r") as map:
        lines = [
            line.strip()
            for line in map
            if len(line.strip()) and not line.strip().startswith("#")
        ]
    graph = Graph(lines)
    print(
        " ".join(
            [str(drone.id) + "-" + drone.zone.name for drone in graph.drones]
        ),
        step,
    )
    while True:
        if all([drone.zone == graph.finish for drone in graph.drones]):
            break
        for drone in graph.drones:
            Dijkestra.choose_zone(drone, graph)
        for drone in graph.drones:
            if drone.in_transit:
                continue
            Dijkestra.move_drone(drone)
        step += 1
        print(
            " ".join(
                [
                    str(drone.id) + "-" + drone.zone.name
                    for drone in graph.drones
                ]
            ),
            step,
        )


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
