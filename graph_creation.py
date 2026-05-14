from enum import Enum
from typing import List
import parsing


class State(Enum):
    BLOCKED = 1
    WAITING = 2
    EXECUTING = 3
    READY = 4


class Hub:
    def __init__(self, hub: parsing.ParsedHub | None) -> None:
        if not hub:
            return
        self.name = hub.name
        self.cod: tuple[int | None, int | None] = (hub.x, hub.y)
        self.color = hub.color
        self.zone = hub.zone
        self.cap = hub.max_drones if hub.max_drones else 1
        self.size = 0
        self.connections: list[Connection] = []


class Connection:
    def __init__(self, hub: Hub, cap: int) -> None:
        self.hub: Hub = hub
        self.max_cap: int = cap
        self.size = 0


class Drone:
    def __init__(self, id: int, start: Hub) -> None:
        self.id = id
        self.zone: Hub = start
        self.state: State = State.READY
        self.destination: Connection | None = None
        self.connection: str = ""
        self.moved = False
        self.in_transit = False
        self.visited = [self.zone.name]
        self.path: List[str] = []

    def choose_zone(self, connection: Connection | None) -> None:
        if not connection:
            return
        if (
            connection.size >= connection.max_cap
            or connection.hub.size >= connection.hub.cap
        ):
            self.state = State.WAITING
            return
        self.destination = connection
        self.destination.size += 1
        self.state = State.READY

    def move_drone(self) -> None:
        if not self.destination:
            return
        if self.state == State.WAITING:
            self.destination.size -= 1
            self.state = State.READY
            return
        self.zone.size -= 1
        self.zone = self.destination.hub
        self.destination.size -= 1
        self.zone.size += 1


class Graph:
    def __init__(self, lines: list[str]) -> None:
        parsed_graph = parsing.GraphData(lines)
        self.hubs = [Hub(hub) for hub in parsed_graph.hubs]

        start = Hub(parsed_graph.start)
        goal = Hub(parsed_graph.finish)

        self.start: Hub = next(
            filter(lambda x: x.name == start.name, self.hubs)
        )
        self.finish: Hub = next(
            filter(lambda x: x.name == goal.name, self.hubs)
        )

        self.drone_num = parsed_graph.drone_num
        self.start.cap = self.drone_num
        self.finish.cap = self.drone_num
        self.set_connections(parsed_graph.connections)
        self.start.size = self.drone_num

        self.drones: List[Drone] = [
            Drone(id + 1, self.start) for id in range(self.drone_num)
        ]

    def set_connections(self, connections: list) -> None:
        hubs = {hub.name: hub for hub in self.hubs}

        for conn in connections:
            a_name = conn.get("node_a")
            b_name = conn.get("node_b")
            capacity = conn.get("cap")
            hub_a = hubs.get(a_name)
            hub_b = hubs.get(b_name)

            if hub_a and hub_b:
                hub_a.connections.append(Connection(hub_b, capacity))
                hub_b.connections.append(Connection(hub_a, capacity))
