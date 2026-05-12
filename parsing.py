import re
import sys
from typing import Any, List


class ParsingError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Graph:
    hub_regex = (
        r"^hub:\s+(?P<name>\S+)\s(?P<X>-?\d+)\s(?P<Y>-?\d+)"
        r"(?:\s+\[(?P<meta_data>.*?)\])?$"
    )
    start_regex = (
        r"^start_hub:\s+(?P<name>\S+)\s+(?P<X>-?\d+)\s+(?P<Y>-?\d+)"
        r"(?:\s+\[(?P<meta_data>.*?)\])?$"
    )
    goal_regex = (
        r"^end_hub:\s+(?P<name>\S+)\s+(?P<X>-?\d+)\s+(?P<Y>-?\d+)"
        r"(?:\s+\[(?P<meta_data>.*?)\])?$"
    )
    drone_num_regex = r"^nb_drones:\s+(?P<num>-?\d+)"
    connections_regex = r"connection:\s+(?P<node_a>\S+)-(?P<node_b>\S+)"

    def __init__(self) -> None:
        lines: list = []
        with open(sys.argv[1], "r") as map:
            lines = [
                line.strip("\n")
                for line in map
                if len(line.strip()) and not line.strip().startswith("#")
            ]
        self.start: Any = None
        self.finish: Any = None
        self.drone_num: Any = None
        self.hubs: List = []
        self.connections: List = []
        self.parse_drones(lines)
        self.parse_start(lines)
        self.parse_hubs(lines)
        self.parse_finish(lines)
        self.parse_connection(lines)
        if len(lines):
            raise ParsingError("invalid map")

    def parse_start(self, lines: List[str]) -> None:
        for i, line in enumerate(lines):
            match = re.search(Graph.start_regex, line)
            if match:
                self.start = match
                lines.pop(i)
                return
        if not self.start:
            raise ParsingError("no start hub detected")

    def parse_drones(self, lines: List[str]) -> None:
        for i, line in enumerate(lines):
            match = re.search(Graph.drone_num_regex, line)
            if match:
                self.drone_num = match
                lines.pop(i)
                return
        if not self.drone_num:
            raise ParsingError("no drone number detected")

    def parse_hubs(self, lines: List[str]) -> None:
        rev = 0
        for i in range(len(lines)):
            match = re.search(Graph.hub_regex, lines[i - rev])
            if match:
                self.hubs.append(match)
                lines.pop(i - rev)
                rev += 1
        if not len(self.hubs):
            raise ParsingError("no hubs detected")

    def validate_connections(self, connection: re.Match[str] | None) -> bool:
        if not connection:
            return False
        node_a = connection.groupdict()["node_a"]
        node_b = connection.groupdict()["node_b"]
        valid_names = {node.groupdict()["name"] for node in self.hubs}
        valid_names.add(self.start.groupdict()["name"])
        valid_names.add(self.finish.groupdict()["name"])
        return node_a in valid_names and node_b in valid_names

    def parse_finish(self, lines: List[str]) -> None:
        for i, line in enumerate(lines):
            match: re.Match[str] | None = re.search(Graph.goal_regex, line)
            if match:
                self.finish = match
                lines.pop(i)
                return
        if not self.finish:
            raise ParsingError("no finish line detected")

    def parse_connection(self, lines: List[str]) -> None:
        rev = 0
        for i in range(len(lines)):
            match = re.search(Graph.connections_regex, lines[i - rev])
            if self.validate_connections(match):
                self.connections.append(match)
                lines.pop(i - rev)
                rev += 1
        if not len(self.hubs):
            raise ParsingError("invalid connection")
