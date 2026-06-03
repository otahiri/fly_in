"""Graph domain models and runtime entities for the fly-in simulation."""

from typing import List
import parsing


class Hub:
    """Graph node representing a map hub and its runtime occupancy."""

    def __init__(self, hub: parsing.ParsedHub | None) -> None:
        """Create a runtime hub from parsed map data.

        Args:
            hub: Parsed hub data. If ``None``, initialization is skipped.

        Returns:
            None
        """
        if not hub:
            return
        self.name = hub.name
        self.cod: tuple[int | None, int | None] = (hub.x, hub.y)
        self.color = hub.color
        self.zone = hub.zone
        self.cap = hub.cap if hub.cap else 1
        self.size = 0
        self.connections: list[Connection] = []


class Connection:
    """Directed view of a bidirectional map connection."""

    def __init__(self, hub: Hub, cap: int) -> None:
        """Initialize a connection toward a neighboring hub.

        Args:
            hub: Neighbor hub reached through this edge.
            cap: Maximum number of drones allowed on the link.

        Returns:
            None
        """
        self.hub: Hub = hub
        self.max_cap: int = cap
        self.size = 0


class Drone:
    """Runtime state holder for one simulated drone."""

    def __init__(self, id: int, start: Hub) -> None:
        """Initialize a drone positioned at the start hub.

        Args:
            id: Stable drone identifier used in output rendering.
            start: Start hub where the drone begins the simulation.

        Returns:
            None
        """
        self.id = id
        self.zone: Hub = start
        self.destination: Connection | None = None
        self.connection: tuple = ()
        self.moved = False
        self.in_transit = False
        self.visited = [self.zone.name]
        self.path_len: int = 0
        self.distance_to_finish = float('inf')

    def move_drone(self) -> None:
        """Apply one movement step for a drone during the current turn.

        Returns:
            None
        """
        if not self.destination:
            return
        if not self.in_transit:
            self.moved = True
            self.connection = (
                (self.destination.size, self.destination.max_cap),
                self.zone,
                self.destination.hub,
            )
            self.destination.size -= 1
            self.zone = self.destination.hub
            self.destination = None
            self.in_transit = self.zone.zone == "restricted"
            self.visited.append(self.zone.name)

    def choose_zone(self, graph: "Graph") -> None:
        """Select and reserve the next hub for a drone, when available.

        Args:
            graph: Graph containing hubs, links, and finish target.

        Returns:
            None
        """
        from algo import Dijkestra
        self.moved = False
        zone: Hub | None
        if self.in_transit:
            self.in_transit = False
            self.moved = True
            return
        if self.destination is not None:
            return
        path = Dijkestra.algo(graph, self)
        if not len(path):
            return
        zone = path[0]
        if not zone:
            return
        if zone.name in self.visited:
            return
        connection: Connection | None = next(
            filter(lambda conn: conn.hub.name == zone.name,
                   self.zone.connections),
            None,
        )
        if not connection:
            return
        if (
            connection.size >= connection.max_cap
            or connection.hub.size >= connection.hub.cap
        ):
            return
        self.destination = connection
        self.path_len = len(path)
        self.destination.size += 1
        self.destination.hub.size += 1
        self.zone.size -= 1


class Graph:
    """Container for hubs, connections, and drone collection."""

    def __init__(self, lines: list[str]) -> None:
        """Build a graph model and initialize drones from map lines.

        Args:
            lines: Map lines in fly-in text format.

        Returns:
            None
        """
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
        self.connections: list[Connection] = []
        self.finish.cap = self.drone_num
        self.set_connections(parsed_graph.connections)
        self.start.size = self.drone_num

        self.drones: List[Drone] = [
            Drone(id + 1, self.start) for id in range(self.drone_num)
        ]

    def set_connections(self, connections: list) -> None:
        """Attach bidirectional links between hubs.

        Args:
            connections: Parsed connection objects with node names and caps.

        Returns:
            None
        """
        hubs = {hub.name: hub for hub in self.hubs}

        for conn in connections:
            a_name = conn.get("node_a")
            b_name = conn.get("node_b")
            capacity = conn.get("cap")
            hub_a = hubs.get(a_name)
            hub_b = hubs.get(b_name)

            if hub_a and hub_b:
                conn_a = Connection(hub_b, capacity)
                conn_b = Connection(hub_a, capacity)
                self.connections.append(conn_a)
                self.connections.append(conn_b)
                hub_a.connections.append(conn_a)
                hub_b.connections.append(conn_b)
