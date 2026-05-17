"""Parsing and validation for fly-in map files."""

from re import Match, compile
from typing import List, Any
import webcolors


class ParsingError(Exception):
    """Raised when the map input does not match expected constraints."""

    def __init__(self, *args: object) -> None:
        """Initialize a parsing error with the provided message parts."""
        super().__init__(*args)


class ParsedHub:
    """Represent a validated hub entry parsed from one map line."""

    def __init__(self, match: Match[str], hub_type: str) -> None:
        """Parse and validate a hub definition from a regex match."""
        raw_x = match.groupdict().get("x")
        raw_y = match.groupdict().get("y")
        valid_keys = ["zone", "color", "max_drones"]
        raw_meta = match.groupdict().get("meta_data")
        if raw_meta:
            keys = [key.split('=')[0] for key in raw_meta.split()]
            if len(keys) != len(set(keys)):
                raise ValueError("duplicated meta_data")
            if any(["=" not in w and w not in valid_keys
                    for w in raw_meta.split()]):
                raise ValueError("invalid meta data")
        meta = (
            dict(word.split("=") for word in raw_meta.split())
            if raw_meta else dict()
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
        self.color: str = meta.get("color", "None").lower()
        if self.color != "rainbow" and self.color != "none":
            try:
                self.color = webcolors.name_to_hex(self.color.lower())
            except Exception:
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
    """Store all parsed graph components from map input lines."""

    def __init__(self, lines: List[str]) -> None:
        current_line = ""
        """Parse map lines into hubs, links, and global graph settings."""
        hub_regex = compile(
            r"hub:\s+(?P<name>\S+)\s(?P<x>-?\d+)\s(?P<y>-?\d+)"
            r"(?:\s+\[(?P<meta_data>.*?)\]\s?)?"
        )
        start_regex = compile(
            r"start_hub:\s+(?P<name>\S+)\s+(?P<x>-?\d+)\s+(?P<y>-?\d+)?"
            r"(?:\s+\[(?P<meta_data>.*?)\])?$"
        )
        goal_regex = compile(
            r"end_hub:\s+(?P<name>\S+)\s+(?P<x>-?\d+)\s+(?P<y>-?\d+)?"
            r"(?:\s+\[(?P<meta_data>.*?)\])?\s*$"
        )
        drone_num_regex = compile(r"^nb_drones:\s+(?P<num>\S+)$")
        connections_regex = compile(
            r"connection:\s+(?P<node_a>\S+)-(?P<node_b>\S+)"
            r"(?:\s+\[(max_link_capacity=(?P<cap>-?\S+))?\])?$"
        )

        idx = 0
        self.start = None
        self.finish = None
        self.drone_num: int = -1
        self.hubs: List[ParsedHub] = []
        self.connections: List[dict[str, Any]] = []
        if match := drone_num_regex.match(lines[0]):
            raw_num = str(match.groupdict().get("num"))
            if not raw_num.isdigit():
                raise ParsingError(f"invalid number of drones line: \
{lines[0]}")
            if self.drone_num != -1:
                raise ParsingError(f"duplicated drone number line: \
{lines[0]}")
            try:
                self.drone_num = int(str(raw_num))
            except ValueError:
                raise ParsingError(f"invalid drone number line: {lines[0]}")
            if self.drone_num <= 0:
                raise ParsingError(f"invalid drone number line: {lines[0]}")
        else:
            raise ParsingError(
                f"invalid map drone count should be first line line: \
{lines[0]}"
            )
        lines = lines[1::]
        for line in lines:
            current_line = line
            idx += 1
            if match := start_regex.match(line):
                if self.start:
                    raise ParsingError(f"duplicated start hub line: {line}")
                try:
                    self.start = ParsedHub(match, "start")
                except Exception as e:
                    raise ParsingError(f"{e} line: {line}")
                if self.start.zone == "blocked":
                    raise ParsingError(f"start zone cannot be blocked line: \
{line}")
                if "-" in self.start.name:
                    raise ParsingError(f"invalid hub name line: {line}")
                if self.start.name in [hub.name for hub in self.hubs]:
                    raise ParsingError(f"duplicated zones are not allowed \
line: {line}")
                self.hubs.append(self.start)

            elif match := goal_regex.match(line):
                if self.finish:
                    raise ParsingError(f"duplicated goal hub line: {line}")
                try:
                    self.finish = ParsedHub(match, "end")
                except Exception:
                    raise ParsingError(f"invalid finish hub line: {line}")
                if self.finish.zone == "blocked":
                    raise ParsingError(f"finish zone cannot be blocked line: \
{line}")
                if "-" in self.finish.name:
                    raise ParsingError(f"invalid hub name line: {line}")
                if self.finish.name in [hub.name for hub in self.hubs]:
                    raise ParsingError(f"duplicated zones are not allowed \
line: {line}")
                self.hubs.append(self.finish)

            elif match := hub_regex.match(line):
                try:
                    hub = ParsedHub(match, "hub")
                    if hub.name in [hub.name for hub in self.hubs]:
                        raise ParsingError(f"duplicated zones are not allowed \
line :{line}")

                    self.hubs.append(hub)
                except Exception as e:
                    raise ParsingError(f"{e} line: {line}")
                if "-" in self.hubs[-1].name:
                    raise ParsingError(f"invalid hub name {line}")
            elif match := connections_regex.match(line):
                raw_cap = match.groupdict().get("cap")
                raw_node_a = match.groupdict().get("node_a")
                raw_node_b = match.groupdict().get("node_b")
                if any(
                    {con["node_a"], con["node_b"]} == {raw_node_b, raw_node_a}
                    for con in self.connections
                ):
                    raise ParsingError(f"duplicated connections line: {line}")
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
                    raise ParsingError(f"invalid connection line: {line}")

            else:
                break
        if idx < len(lines):
            raise ParsingError(f"invalid map line: {current_line}")
        self.validate_graph()

    def validate_graph(self) -> None:
        """Validate required graph rules after parsing all lines."""
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
