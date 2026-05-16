from graph_creation import Connection, Drone, Hub, Graph
import heapq

from parsing import ParsingError


class Dijkestra:
    @staticmethod
    def move_drone(drone: Drone) -> None:
        if not drone.destination:
            return
        if not drone.in_transit:
            drone.moved = True
            drone.destination.size -= 1
            drone.connection = (drone.zone, drone.destination.hub)
            drone.zone = drone.destination.hub
            drone.destination = None
            drone.in_transit = drone.zone.zone == "restricted"
            drone.visited.append(drone.zone.name)

    @staticmethod
    def choose_zone(drone: Drone, graph: Graph) -> None:
        drone.moved = False
        zone: Hub | None
        path: list[str]
        if drone.in_transit:
            drone.in_transit = False
            return
        if drone.destination is not None:
            return
        zone, path = Dijkestra.algo(graph, drone.zone)
        if not zone:
            return
        if zone.name in drone.visited:
            return
        connection: Connection | None = next(
            filter(
                lambda conn: conn.hub.name == zone.name, drone.zone.connections
            ),
            None,
        )
        if not connection:
            return
        if (
            connection.size >= connection.max_cap
            or connection.hub.size >= connection.hub.cap
        ):
            return
        drone.destination = connection
        drone.path = path
        drone.destination.size += 1
        drone.destination.hub.size += 1
        drone.zone.size -= 1

    @staticmethod
    def build_path(parent_edges: dict, zone: Hub, finish: Hub) -> list:
        path: list = []
        while zone.name != finish.name:
            path.append(zone)
            zone = parent_edges[zone.name]
        return path

    @staticmethod
    def algo(graph: Graph, zone: Hub) -> tuple:

        distances: dict = {hub.name: float("inf") for hub in graph.hubs}
        distances[graph.finish.name] = 0
        if zone.name == graph.finish.name:
            return None, None

        parent_edges: dict = {}

        hq: list = [(0, id(graph.finish), graph.finish)]

        while hq:
            current_cost, _, current_node = heapq.heappop(hq)
            if current_node.name == zone.name:
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
                    neighbor_cost // int(neighbor.zone == "priority") * 2
                    if neighbor.zone == "priority"
                    else neighbor_cost
                )

                possible_cost = neighbor_cost + current_cost
                if possible_cost < distances[neighbor.name]:
                    distances[neighbor.name] = possible_cost
                    parent_edges[neighbor.name] = current_node
                    heapq.heappush(hq, (possible_cost, id(neighbor), neighbor))
        try:
            ret = parent_edges[zone.name]
        except KeyError:
            raise ParsingError("impossible map")
        ret = None if ret.size >= ret.cap else ret
        return ret, Dijkestra.build_path(parent_edges, zone, graph.finish)
