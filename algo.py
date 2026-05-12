from graph_creation import Connection, Drone, Hub, Graph
import heapq


class Dijkestra:
    @staticmethod
    def move_drone(drone: Drone):
        pass

    @staticmethod
    def choose_zone(drone: Drone, graph: Graph):
        zone: Hub | None = Dijkestra.algo(graph, drone.zone)
        if not zone:
            return
        connection: Connection | None = next(
            filter(
                lambda conn: conn.hub.name == zone.name, drone.zone.connections
            ),
            None,
        )
        if not connection:
            return

        print(connection.hub.name)

    @staticmethod
    def build_path():
        pass

    @staticmethod
    def algo(graph: Graph, zone: Hub) -> Hub | None:

        distances: dict = {hub.name: float("inf") for hub in graph.hubs}
        distances[graph.finish.name] = 0
        if zone.name == graph.finish.name:
            return None

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
                neighbor_cost = (
                    (
                        1
                        + (neighbor.size >= neighbor.cap)
                        + (connection.size >= connection.max_cap)
                        + (connection.hub.zone == "restricted")
                    )
                    * 2
                ) - int(neighbor.zone == "priority")

                potential_cost = neighbor_cost + current_cost
                if potential_cost < distances[neighbor.name]:
                    distances[neighbor.name] = potential_cost
                    parent_edges[neighbor.name] = current_node
                    heapq.heappush(hq, (potential_cost, id(neighbor), neighbor))

        return parent_edges[zone.name]
