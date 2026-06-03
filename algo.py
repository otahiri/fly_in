"""Pathfinding and movement scheduling helpers for drone routing."""

from graph_creation import Drone, Hub, Graph
import heapq

from parsing import ParsingError


class MapError(Exception):
    """Raised when an algorithm-specific map condition cannot be handled."""

    def __init__(self, *args: object) -> None:
        """Initialize an algorithm map error.

        Args:
            *args: Error message parts forwarded to ``Exception``.

        Returns:
            None
        """
        super().__init__(*args)


class Dijkestra:
    """Provide pathfinding and movement operations for drones."""

    @staticmethod
    def build_path(parent_edges: dict, drone: Drone, finish: Hub) -> list:
        """Build a path from the drone's current hub to the finish hub.

        Args:
            parent_edges: Parent hub mapping produced by the shortest-path run.
            drone: Drone whose current hub is used as path origin.
            finish: Finish hub used as path destination.

        Returns:
            list: Ordered hubs from origin to finish, or an empty list when
                finish is unreachable.
        """
        path: list = []
        zone = finish
        if drone.zone not in parent_edges.values():
            raise ParsingError("impossible map")
        while zone.name != drone.zone.name:
            path.append(zone)
            zone = parent_edges[zone.name]
        return path

    @staticmethod
    def algo(graph: Graph, drone: Drone) -> list:
        """Compute a lowest-cost route from the drone zone to the finish.

        Args:
            graph: Graph to search.
            drone: Drone whose current hub is the search start.

        Returns:
            list: Hubs representing the route from current zone to finish.
                Returns an empty list when the drone is already at finish or
                no route exists.
        """

        distances: dict = {hub.name: float("inf") for hub in graph.hubs}
        zone = drone.zone
        distances[zone.name] = 0

        if zone.name == graph.finish:
            return []

        parent_edges: dict = {}

        hq: list = [(0, id(zone), zone)]

        while hq:
            current_cost, _, current_node = heapq.heappop(hq)
            if current_node.name == graph.finish.name:
                break
            if current_cost > distances[current_node.name]:
                continue

            for connection in current_node.connections:
                neighbor = connection.hub
                if neighbor.zone == "blocked":
                    continue
                neighbor_cost = 2
                neighbor_cost += int(connection.hub.zone == "restricted") * 2
                neighbor_cost += neighbor.size
                neighbor_cost = (
                    neighbor_cost // 2 if neighbor.zone == "priority"
                    else neighbor_cost
                )

                possible_cost = neighbor_cost + current_cost
                if possible_cost < distances[neighbor.name]:
                    distances[neighbor.name] = possible_cost
                    parent_edges[neighbor.name] = current_node
                    heapq.heappush(hq, (possible_cost, id(neighbor), neighbor))
        try:
            path = Dijkestra.build_path(parent_edges, drone, graph.finish)
        except ParsingError as e:
            print(e)
            exit(0)
        path.reverse()
        return path
