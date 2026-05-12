import re
import sys


class ParsingError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Graph:
    hub_regex = r"^hub:\s+(?P<name>\S+)\s(?P<X>-?\d+)\s(?P<Y>-?\d+)(?:\s+\
            \[(?P<meta_data>.*?)\])?$"
    start_regex = (
        r"^start_hub:\s+(?P<name>\S+)\s+(?P<X>-?\d+)\s+(?P<Y>-?\d+)(?:\s+\
            \[(?P<meta_data>.*?)\])?$"
    )
    goal_regex = (
        r"^end_hub:\s+(?P<name>\S+)\s+(?P<X>-?\d+)\s+(?P<Y>-?\d+)(?:\s+\
            \[(?P<meta_data>.*?)\])?$"
    )
    drone_num_regex = r"^nb_drones:\s+(?P<num>-?\d+)"
    connections_regex = r"connection:\s+(?P<node1>\S+)-(?P<node2>\S+)"

    def __init__(self) -> None:
        lines: list = []
        with open(sys.argv[1], "r") as map:
            lines = [
                line.strip("\n")
                for line in map
                if len(line.strip()) and not line.strip().startswith("#")
            ]
        self.drone_num = re.search(Graph.drone_num_regex, lines.pop(0))
        if not self.drone_num:
            raise ParsingError("no drone number detected")
        self.start = re.search(Graph.start_regex, lines.pop(0))
        if not self.start:
            raise ParsingError("no start hub detected")
        self.hubs = []
        while lines and re.search(Graph.hub_regex, lines[0]):
            self.hubs.append(re.search(Graph.hub_regex, lines.pop(0)))
        if not len(self.hubs):
            raise ParsingError("no hub detected")
        self.finish = re.search(Graph.goal_regex, lines.pop(0))
        if not self.finish:
            raise ParsingError("invalid finish")
        self.connections = []
        while lines and re.search(Graph.connections_regex, lines[0]):
            self.connections.append(
                re.search(Graph.connections_regex, lines.pop(0))
            )
        if not len(self.connections):
            raise ParsingError("not enough connections")
        if len(lines):
            raise ParsingError("invalid map")

    def validate_graph(self):
        pass
