import re
import pygame
from typing import List


class ParsingError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ParsedHub:
    def __init__(self, match: re.Match):
        raw_x = match.groupdict().get("x")
        raw_y = match.groupdict().get("y")
        valid_keys = ["zone", "color", "max_drones"]
        raw_meta = match.groupdict().get("meta_data")
        meta = (
            dict(word.split("=") for word in raw_meta.split())
            if raw_meta and all("=" in word for word in raw_meta.split())
            else dict()
        )
        raw_max_drones = meta.get("max_drones")
        for word in meta.keys():
            if word not in valid_keys:
                raise ValueError("invalid meta data")
        self.name: str = str(match.groupdict().get("name"))
        self.x: int | None = int(raw_x) if raw_x else None
        self.y: int | None = int(raw_y) if raw_y else None
        self.zone: str = meta.get("zone", "normal")
        if self.zone not in ["normal", "blocked", "restricted", "priority"]:
            raise ValueError("invalid zone type")
        self.color: str = meta.get("color", "None")
        color_dict = pygame.color.__dict__.get("THECOLORS")
        if not color_dict:
            return
        if self.color not in color_dict.keys():
            raise ValueError("invalid color")
        self.max_drones: int = int(raw_max_drones) if raw_max_drones else 1
        if self.max_drones <= 0:
            raise ValueError("invalid drone num")


class GraphData:

    def __init__(self, lines: List[str]) -> None:
        hub_regex = re.compile(
            r"^hub:\s+(?P<name>\S+)\s(?P<x>-?\d+)\s(?P<y>-?\d+)\s+"
            r"(\[(?P<meta_data>.*?)\])?$"
        )
        start_regex = re.compile(
            r"^start_hub:\s+(?P<name>\S+)\s+(?P<x>-?\d+)\s+(?P<y>-?\d+)\s+"
            r"(\[(?P<meta_data>.*?)\])?$"
        )
        goal_regex = re.compile(
            r"^end_hub:\s+(?P<name>\S+)\s+(?P<x>-?\d+)\s+(?P<y>-?\d+)\s+"
            r"(\[(?P<meta_data>.*?)\])?$"
        )
        drone_num_regex = re.compile(r"^nb_drones:\s+(?P<num>\S+)\s*$")
        connections_regex = re.compile(
            r"connection:\s+(?P<node_a>\S+)-(?P<node_b>\S+)"
            r"(?:\s+\[max_link_capacity=(?P<cap>-?\S+)\])?\s*$"
        )

        idx = 0
        self.start = None
        self.finish = None
        self.drone_num: int = -1
        self.hubs: List = []
        self.connections: List[dict] = []
        for line in lines:
            idx += 1
            if match := start_regex.search(line):
                if self.start:
                    raise ParsingError(f"duplicated start hub {line}")
                try:
                    self.start = ParsedHub(match)
                except Exception as e:
                    raise ParsingError(f"{e} {line}")
                if self.start.zone == "blocked":
                    raise ParsingError(f"start zone cannot be blocked {line}")
                self.hubs.append(self.start)

            elif match := goal_regex.search(line):
                if self.finish:
                    raise ParsingError(f"duplicated goal hub {line}")
                try:
                    self.finish = ParsedHub(match)
                except Exception:
                    raise ParsingError(f"invalid finish hub {line}")
                if self.finish.zone == "blocked":
                    raise ParsingError(f"finish zone cannot be blocked {line}")
                self.hubs.append(self.finish)

            elif match := drone_num_regex.search(line):
                raw_num = str(match.groupdict().get("num"))
                if not raw_num.isdigit():
                    raise ParsingError(f"invalid number of drones {line}")
                if self.drone_num != -1:
                    raise ParsingError(f"duplicated drone number {line}")
                try:
                    self.drone_num = int(str(raw_num))
                except ValueError:
                    raise ParsingError(f"invalid drone number {line}")
                if self.drone_num <= 0:
                    raise ParsingError(f"invalid drone number {line}")
            elif match := hub_regex.search(line):
                try:
                    self.hubs.append(ParsedHub(match))
                except Exception:
                    raise ParsingError(f"invalid hub {line}")
            elif match := connections_regex.search(line):
                raw_cap = match.groupdict().get("cap")
                raw_node_a = match.groupdict().get("node_a")
                raw_node_b = match.groupdict().get("node_b")
                if any(
                    {con["node_a"], con["node_b"]} == {raw_node_b, raw_node_a}
                    for con in self.connections
                ):
                    raise ParsingError(f"duplicated connections {line}")
                try:
                    self.connections.append(
                        {
                            "node_a": raw_node_a,
                            "node_b": raw_node_b,
                            "cap": int(raw_cap) if raw_cap else 1,
                        }
                    )
                except Exception:
                    raise ParsingError(f"invalid connection {line}")

            else:
                break
        if idx < len(lines):
            raise ParsingError("invalid map")
        self.validate_graph()

    def validate_graph(self):
        if not self.start:
            raise ParsingError("no start detected invalid map")
        if not self.finish:
            raise ParsingError("no finish detected invalid map")
        for huba in self.hubs:
            for hubb in self.hubs:
                if huba.name != hubb.name and (huba.x, huba.y) == (
                    hubb.x,
                    hubb.y,
                ):
                    raise ParsingError(
                        f"{huba.name} and {hubb.name} are overlapping"
                    )
