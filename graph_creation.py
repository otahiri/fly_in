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


class Connection:
    def __init__(self, connnection: dict) -> None:
        self.hub_a = connnection["node_a"]
        self.hub_b = connnection["node_b"]
        self.max_cap = connnection["cap"]


class Graph:
    def __init__(self, lines: list):
        parsed_graph = parsing.GraphData(lines)
        self.hubs = [Hub(hub) for hub in parsed_graph.hubs]
        self.connections = [
            Connection(connnection) for connnection in parsed_graph.connections
        ]
        self.start = Hub(parsed_graph.start)
        self.finish = Hub(parsed_graph.finish)
        self.drone_num = parsed_graph.drone_num
