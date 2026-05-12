import re
import sys

class ParsingError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class graph:
    hub_regex = r"^hub:\s+(?P<name>\S+)\s(?P<X>-?\d+)\s(?P<Y>-?\d+)(?:\s+\[(?P<meta_data>.*?)\])?$"
    start_regex = r"^start_hub:\s+(?P<name>\S+)\s+(?P<X>-?\d+)\s+(?P<Y>-?\d+)(?:\s+\[(?P<meta_data>.*?)\])?$"
    goal_regex = r"^end_hub:\s+(?P<name>\S+)\s+(?P<X>-?\d+)\s+(?P<Y>-?\d+)(?:\s+\[(?P<meta_data>.*?)\])?$"
    drone_num_regex = r"^nb_drones:\s+(?P<num>-?\d+)"
    connections_regex = r"connection:\s+(?P<node1>\S+)-(?P<node2>\S+)"
    def __init__(self) -> None:
        lines: list = []
        with open(sys.argv[1], 'r') as map:
            lines = [line.strip('\n') for line in map  if len(line.strip()) and not line.strip().startswith('#')]
        self.drone_num = re.search(graph.drone_num_regex, lines.pop(0))
        if not self.drone_num:
            raise ParsingError("no drone number detected")
        self.start = re.search(graph.start_regex, lines.pop(0))
        if not self.start:
            raise ParsingError("no start hub detected")
        self.hubs = []
        while re.search(graph.hub_regex, lines[0]):
            self.hubs.append(re.search(graph.hub_regex, lines.pop(0)))
        if not len(self.hubs):
            raise ParsingError("no hub detected")
        self.finish = re.search(graph.goal_regex, lines.pop(0))
        if not self.finish:
            raise ParsingError("invalid finish")
        self.connections = [re.search(graph.connections_regex, lines.pop(0)) if lines and re.search(graph.connections_regex, lines[0]) else None]
        if not len(self.connections):
            raise ParsingError("not enough connections")

def main():

    lines = [line.strip('\n') for line in  if len(line.strip()) and not line.strip().startswith('#')]
    if len(lines):
        raise ParsingError("invalid map")
    for con in connections:
        print(con.groupdict()["node2"])

