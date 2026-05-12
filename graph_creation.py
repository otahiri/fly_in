from enum import Enum
from typing import List
import parsing


class State(Enum):
    MOVING = 1
    STATIC = 2


class Hub:
    def __init__(self, hub: parsing.ParsedHub | None) -> None:
        if not hub:
            return
        self.name = hub.name
        self.cod: tuple = (hub.x, hub.y)
        self.color = hub.color
        self.zone = hub.zone
        self.cap = hub.max_drones
        self.size = 0
        self.connections: list[Connection] = []


class Drone:
    def __init__(self, id: int, zone: Hub) -> None:
        self.id = id
        self.zone: Hub
        self.state: State = State.STATIC
        self.destination: Hub
        self.move_drone(zone)

    def move_drone(self, zone: Hub) -> None:
        if self.state == State.MOVING:
            self.state = State.STATIC
            self.zone = self.destination
            self.zone.size += 1
            return
        if zone.zone == "restricted":
            self.state = State.MOVING
            self.destination = zone
            return
        else:
            self.zone = zone
            self.zone.size += 1
            self.state = State.STATIC


class Connection:
    def __init__(self, hub: Hub, cap: int) -> None:
        self.hub: Hub = hub
        self.max_cap: int = cap


class Graph:
    def __init__(self, lines: list) -> None:
        parsed_graph = parsing.GraphData(lines)
        self.hubs = [Hub(hub) for hub in parsed_graph.hubs]
        start = Hub(parsed_graph.start)
        goal = Hub(parsed_graph.finish)
        self.start = next(filter(lambda x: x.name == start.name, self.hubs))
        self.finish = next(filter(lambda x: x.name == goal.name, self.hubs))
        self.drone_num = parsed_graph.drone_num
        self.set_connections(parsed_graph.connections)
        self.drones: List[Drone] = [
            Drone(id, self.start) for id in range(self.drone_num)
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
