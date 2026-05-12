from os import error
import re
from typing import Any, List
from pydantic import BaseModel, Field, field_validator


class ParsingError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


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

    start: Line = Field()
    finish: Line = Field()
    drone_num: int = Field()
    hubs: List[Line] = Field()
    connections: List[tuple] = Field()

    def __init__(self, lines: List[str]) -> None:
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

        idx = 0
        parsed_start: Line | None = None
        parsed_finish: Line | None = None
        parsed_drone_num: int = -1
        parsed_hubs: List[Line] = []
        parsed_connections: List[tuple] = []
        for line in lines:
            idx += 1
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if match := start_regex.search(line):
                if parsed_start:
                    raise ParsingError(f"duplicated start hub {line}")
                parsed_start = Line.model_validate(match.groupdict())
                parsed_hubs.append(Line.model_validate(match.groupdict()))

            elif match := goal_regex.search(line):
                if parsed_finish:
                    raise ParsingError(f"duplicated goal hub {line}")
                parsed_finish = Line.model_validate(match.groupdict())
                parsed_hubs.append(Line.model_validate(match.groupdict()))

            elif match := drone_num_regex.search(line):
                if parsed_drone_num > -1:
                    raise ParsingError(f"duplicated drone number {line}")
                try:
                    parsed_drone_num = int(match.groupdict().get("num", -1))
                except ValueError:
                    raise ParsingError(f"invalid drone number {line}")
                if parsed_drone_num <= 0:
                    raise ParsingError(f"invalid drone number {line}")
            elif match := hub_regex.search(line):
                parsed_hubs.append(Line.model_validate(match.groupdict()))
            elif match := connections_regex.search(line):
                parsed_connections.append(
                    (
                        match.groupdict().get("node_a"),
                        match.groupdict().get("node_b"),
                    )
                )
                a, b = parsed_connections[-1]
                if a not in [hub.name for hub in parsed_hubs] or b not in [
                    hub.name for hub in parsed_hubs
                ]:
                    raise ParsingError(f"invalid connection {line}")
            else:
                break
        if idx < len(lines):
            raise ParsingError(f"invalid map additional lines {lines[idx::]}")
