from re import Match, compile
from typing import List, Any
import webcolors


class ParsingError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ParsedHub:
    def __init__(self, match: Match[str], hub_type: str) -> None:
        raw_x = match.groupdict().get("x")
        raw_y = match.groupdict().get("y")
        valid_keys = ["zone", "color", "max_drones"]
        raw_meta = match.groupdict().get("meta_data")
        if raw_meta:
            if any(['=' not in w and w not in valid_keys
                    for w in raw_meta.split()]):
                raise ValueError("invalid meta data")
        meta = (dict(word.split("=") for word in raw_meta.split())
                if raw_meta else dict())
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
        if self.color.lower() != "rainbow" and self.color != "None":
            if not webcolors.name_to_hex(self.color.lower()):
                raise ValueError("invalid color")
        self.cap = None
        if raw_max_drones:
            if not raw_max_drones.isdigit():
                raise ValueError("invalid number of drones")
        self.cap = (
            int(raw_max_drones)
            if raw_max_drones
            else None if hub_type in ["start", "end"] else 1
        )
        if self.cap is not None and self.cap <= 0:
            raise ValueError("invalid drone num")


class GraphData:

    def __init__(self, lines: List[str]) -> None:
        hub_regex = compile(
            r"^hub:\s+(?P<name>\S+)\s(?P<x>-?\d+)\s(?P<y>-?\d+)"
            r"(?:\s+\[(?P<meta_data>.*?)\]\s?)?"
        )
        start_regex = compile(
            r"^start_hub:\s+(?P<name>\S+)\s+(?P<x>-?\d+)\s+(?P<y>-?\d+)\s?"
            r"(?:\s\[(?P<meta_data>.*?)\])?\s*$"
        )
        goal_regex = compile(
            r"^end_hub:\s+(?P<name>\S+)\s+(?P<x>-?\d+)\s+(?P<y>-?\d+)\s?"
            r"(?:\s\[(?P<meta_data>.*?)\])?\s*$"
        )
        drone_num_regex = compile(r"^nb_drones:\s+(?P<num>\S+)\s*$")
        connections_regex = compile(
            r"connection:\s+(?P<node_a>\S+)-(?P<node_b>\S+)"
            r"(?:\s+\[max_link_capacity=(?P<cap>-?\S+)\])?\s*$"
        )

        idx = 0
        self.start = None
        self.finish = None
        self.drone_num: int = -1
        self.hubs: List[ParsedHub] = []
        self.connections: List[dict[str, Any]] = []
        if match := drone_num_regex.search(lines[0]):
            raw_num = str(match.groupdict().get("num"))
            if not raw_num.isdigit():
                raise ParsingError(f"invalid number of drones {lines[0]}")
            if self.drone_num != -1:
                raise ParsingError(f"duplicated drone number {lines[0]}")
            try:
                self.drone_num = int(str(raw_num))
            except ValueError:
                raise ParsingError(f"invalid drone number {lines[0]}")
            if self.drone_num <= 0:
                raise ParsingError(f"invalid drone number {lines[0]}")
        else:
            raise ParsingError(
                f"invalid map drone count should be first line {lines[0]}"
            )
        lines = lines[1::]
        for line in lines:
            idx += 1
            if match := start_regex.search(line):
                if self.start:
                    raise ParsingError(f"duplicated start hub {line}")
                try:
                    self.start = ParsedHub(match, "start")
                except Exception as e:
                    raise ParsingError(f"{e} {line}")
                if self.start.zone == "blocked":
                    raise ParsingError(f"start zone cannot be blocked {line}")
                if "-" in self.start.name:
                    raise ParsingError(f"invalid hub name {line}")
                if self.start.name in [hub.name for hub in self.hubs]:
                    raise ParsingError(f"duplicated zones are not allowed \
{line}")
                self.hubs.append(self.start)

            elif match := goal_regex.search(line):
                if self.finish:
                    raise ParsingError(f"duplicated goal hub {line}")
                try:
                    self.finish = ParsedHub(match, "end")
                except Exception:
                    raise ParsingError(f"invalid finish hub {line}")
                if self.finish.zone == "blocked":
                    raise ParsingError(f"finish zone cannot be blocked {line}")
                if "-" in self.finish.name:
                    raise ParsingError(f"invalid hub name {line}")
                if self.finish.name in [hub.name for hub in self.hubs]:
                    raise ParsingError(f"duplicated zones are not allowed \
{line}")
                self.hubs.append(self.finish)

            elif match := hub_regex.search(line):
                try:
                    hub = ParsedHub(match, "hub")
                    if hub.name in [hub.name for hub in self.hubs]:
                        raise ParsingError(f"duplicated zones are not allowed \
{line}")

                    self.hubs.append(hub)
                except Exception as e:
                    raise ParsingError(f"{e} {line}")
                if "-" in self.hubs[-1].name:
                    raise ParsingError(f"invalid hub name {line}")
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
                    if raw_node_a not in [
                        hub.name for hub in self.hubs
                    ] or raw_node_b not in [hub.name for hub in self.hubs]:
                        raise ValueError
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

    def validate_graph(self) -> None:
        if not self.start:
            raise ParsingError("no start detected invalid map")
        if not self.finish:
            raise ParsingError("no finish detected invalid map")
        for hub_a in self.hubs:
            for hub_b in self.hubs:
                if hub_a.name != hub_b.name and (hub_a.x, hub_a.y) == (
                    hub_b.x,
                    hub_b.y,
                ):
                    raise ParsingError(f"{hub_a.name} and \
{hub_b.name} are overlapping")
        self.start.cap = (
                self.drone_num if self.start.cap is None else self.start.cap
                )
        self.finish.cap = (
                self.drone_num if self.finish.cap is None else self.finish.cap
                           )
        if self.start.cap < self.drone_num:
            raise ParsingError(
                "start max drones cannot be less than the number of drones"
            )
        if self.finish.cap < self.drone_num:
            raise ParsingError(
                "finish max drones cannot be less than the number of drones"
            )
