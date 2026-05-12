import graph_creation
import heapq


class Algo:

    @staticmethod
    def build_path(came_from: dict, end: graph_creation.Hub, start: graph_creation.Hub):
        path = [end]
        name = end.name
        while True:
            path.append(came_from[name])
            name = came_from[name].name
            if name == start.name:
                break
        return path

    @staticmethod
    def dijkestra(
        graph: graph_creation.Graph,
        start: graph_creation.Hub,
        end: graph_creation.Hub,
    ) -> list:

        distances: dict = {hub.name: float("inf") for hub in graph.hubs}

        distances[start.name] = 0

        came_from: dict = {}
        heap = [(0, id(start), start)]

        while heap:
            current_cost, _, current_node = heapq.heappop(heap)
            if current_cost > distances[current_node.name]:
                continue
            for connection in current_node.connections:
                neighbor = connection.hub
                neighbor_cost = 1 + int(neighbor.zone == "restricted")
                potential_cost = neighbor_cost + current_cost
                if potential_cost < distances[neighbor.name]:
                    distances[neighbor.name] = potential_cost
                    came_from[neighbor.name] = current_node
                    heapq.heappush(
                        heap, (potential_cost, id(neighbor), neighbor)
                    )
        return list(reversed(Algo.build_path(came_from, end, start)))
