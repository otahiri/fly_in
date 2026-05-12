import graph_creation
import heapq


class Algo:

    @staticmethod
    def build_path(
        parent_node: dict,
        parent_edge: dict,
        start: graph_creation.Hub,
        end: graph_creation.Hub,
    ) -> dict:
        if start.name == end.name:
            return {}
        rev: list = []
        node = end.name
        while node != start.name:
            if node not in parent_node or node not in parent_edge.keys():
                raise ValueError("unsolvable map")
            parent = parent_node[node]
            rev.append((parent, parent_edge[node]))
            node = parent

        rev.reverse()
        return {node: conn for node, conn in rev}

    @staticmethod
    def dijkestra(
        graph: graph_creation.Graph,
        start: graph_creation.Hub,
        end: graph_creation.Hub,
    ) -> graph_creation.Connection | None:
        if start.name == end.name:
            return None

        distances: dict = {hub.name: float("inf") for hub in graph.hubs}

        distances[start.name] = 0

        parent_node: dict[str, str] = {}
        parent_edge: dict[str, graph_creation.Connection] = {}
        heap = [(0, id(start), start)]

        while heap:
            current_cost, _, current_node = heapq.heappop(heap)
            if current_cost > distances[current_node.name]:
                continue
            for connection in current_node.connections:
                neighbor = connection
                neighbor_cost = (
                    1
                    + int(neighbor.hub.zone == "restricted")
                    + int(connection.size >= connection.max_cap)
                    + int(connection.hub.size >= connection.hub.cap)
                )
                potential_cost = neighbor_cost + current_cost
                if potential_cost < distances[neighbor.hub.name]:
                    distances[neighbor.hub.name] = potential_cost
                    parent_node[neighbor.hub.name] = current_node.name
                    parent_edge[neighbor.hub.name] = connection
                    heapq.heappush(
                        heap, (potential_cost, id(neighbor), neighbor.hub)
                    )
        path = Algo.build_path(parent_node, parent_edge, start, end)
        return path[start.name]
