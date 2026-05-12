import re
from typing import List, Optional


class ParsingError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Hub:
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
        for word in meta.keys():
            if word not in valid_keys:
                raise ValueError
        self.name: str = str(match.groupdict().get("name"))
        self.x: int | None = int(raw_x) if raw_x else None
        self.y: int | None = int(raw_y) if raw_y else None
        self.zone: str = meta.get("zone", "normal")
        self.color: str = meta.get("color", "None")
        self.max_drones: int = int(meta.get("max_drones", "1"))


class Graph:

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
        drone_num_regex = re.compile(r"^nb_drones:\s+(?P<num>-?\d+)")
        connections_regex = re.compile(
            r"connection:\s+(?P<node_a>\S+)-(?P<node_b>\S+)\s?"
            r"(\[?P<cap>max_link_capacity=\S+\])?"
        )

        idx = 0
        self.start: Optional[Hub] = None
        self.finish: Optional[Hub] = None
        self.drone_num: int = -1
        self.hubs: List[Hub | None] = []
        self.connections: List[dict] = []
        for line in lines:
            idx += 1
            if match := start_regex.search(line):
                if self.start:
                    raise ParsingError(f"duplicated start hub {line}")
                try:
                    self.start = Hub(match)
                except Exception:
                    raise ParsingError(f"invalid start hub {line}")
                self.hubs.append(self.start)

            elif match := goal_regex.search(line):
                if self.finish:
                    raise ParsingError(f"duplicated goal hub {line}")
                try:
                    self.finish = Hub(match)
                except Exception:
                    raise ParsingError(f"invalid finish hub {line}")
                self.hubs.append(self.finish)

            elif match := drone_num_regex.search(line):
                if self.drone_num != -1:
                    raise ParsingError(f"duplicated drone number {line}")
                try:
                    self.drone_num = int(match.groupdict().get("num", 0))
                except ValueError:
                    raise ParsingError(f"invalid drone number {line}")
                if self.drone_num <= 0:
                    raise ParsingError(f"invalid drone number {line}")
            elif match := hub_regex.search(line):
                try:
                    self.hubs.append(Hub(match))
                except Exception:
                    raise ParsingError(f"invalid hub {line}")
            elif match := connections_regex.search(line):
                try:
                    self.connections.append(
                        {
                            "node_a": match.groupdict().get("node_a"),
                            "node_b": match.groupdict().get("node_b"),
                            "cap": int(match.groupdict().get("cap", 1)),
                        }
                    )
                except Exception:
                    raise ParsingError(f"invalid connection {line}")

            else:
                break
        if idx < len(lines):
            raise ParsingError(f"invalid map additional lines {lines[idx::]}")
