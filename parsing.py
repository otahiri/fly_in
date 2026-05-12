import re
import sys
from typing import Any, List
from pydantic import BaseModel, field_validator


class ParsingError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


lines: list = []
with open(sys.argv[1], "r") as map:
    lines = [
        line.strip("\n")
        for line in map
        if len(line.strip()) and not line.strip().startswith("#")
    ]


class Line(BaseModel):
    name: str
    x: int
    y: int
    meta_data: dict

    @field_validator("meta_data", mode="before")
    @classmethod
    def parse_line(cls, value: Any) -> Any:
        parsed = {}
        if isinstance(value, str):
            for pair in value.split():
                if "=" not in pair:
                    raise ValueError(f"invalid meta data {value}")
                k, v = pair.split("=", 1)
                parsed[k] = v
            return parsed


class Graph:
    hub_regex = re.compile(
        r"^hub:\s+(?P<name>\S+)\s(?P<x>-?\d+)\s(?P<y>-?\d+)"
        r"(?:\s+\[(?P<meta_data>.*?)\])?$"
    )
    start_regex = re.compile(
        r"^start_hub:\s+(?P<name>\S+)\s+(?P<x>-?\d+)\s+(?P<y>-?\d+)"
        r"(?:\s+\[(?P<meta_data>.*?)\])?$"
    )
    goal_regex = re.compile(
        r"^end_hub:\s+(?P<name>\S+)\s+(?P<x>-?\d+)\s+(?P<y>-?\d+)"
        r"(?:\s+\[(?P<meta_data>.*?)\])?$"
    )
    drone_num_regex = re.compile(r"^nb_drones:\s+(?P<num>-?\d+)")
    connections_regex = re.compile(
        r"connection:\s+(?P<node_a>\S+)-(?P<node_b>\S+)"
    )

    def __init__(self, lines: List[str]) -> None:
        self.start: Line | None
        self.finish: Line | None
        self.drone_num: int | 
        self.hubs: List[Line] = []
        self.connections: List[dict] = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            if match := Graph.start_regex.search(line):
                if self.start:
                    raise ParsingError(f"duplicated start hub {line}")
                self.start = Line.model_validate(match.groupdict())
                lines.pop(i)

            elif match := Graph.goal_regex.search(line):
                if self.finish:
                    raise ParsingError(f"duplicated goal hub {line}")
                self.finish = Line.model_validate(match.groupdict())
                lines.pop(i)

            elif match := Graph.drone_num_regex.search(line):
                if self.drone
