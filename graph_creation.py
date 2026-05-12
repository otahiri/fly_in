from typing import List
import parsing


class Hub:
    def __init__(self, hub: parsing.ParsedHub | None) -> None:
        if not hub:
            return
        self.name = hub.name
        self.cod: tuple = (hub.x, hub.y)
        self.color = hub.color
        self.zone = hub.zone
        self.cap = hub.max_drones
        self.connections: list = []


class Connection:
    def __init__(self, hub: Hub, cap: int) -> None:
        self.hub: Hub = hub
        self.max_cap: int = cap


class Graph:
    def __init__(self, lines: list) -> None:
        parsed_graph = parsing.GraphData(lines)
        self.hubs = [Hub(hub) for hub in parsed_graph.hubs]
        self.start = Hub(parsed_graph.start)
        self.finish = Hub(parsed_graph.finish)
        self.drone_num = parsed_graph.drone_num
        self.connections: List[Connection] = []
        self.set_connections(parsed_graph.connections)

    def set_connections(self, connections: list) -> None:
        hub_name = ""
        for hub in self.hubs:
            for connection in connections:
                if hub.name in [connection["node_a"], connection["node_b"]]:
                    hub_name = (
                        connection["node_a"]
                        if hub.name == connection["node_b"]
                        else connection["node_b"]
                    )

                    hub.connections.append(
                        Connection(
                            next(
                                filter(lambda x: hub_name == x.name, self.hubs)
                            ),
                            connection["cap"],
                        )
                    )
