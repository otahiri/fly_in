"""Rendering helpers for terminal output of drone movements."""

from rich import print
from rich.console import Console
from graph_creation import Drone, Graph, Hub
from webcolors import name_to_hex


class Renderer:
    """Print drones and hubs using optional color metadata."""

    @staticmethod
    def print_line(zone: Hub) -> None:
        """Render one zone label with the configured color behavior."""
        hex_color = name_to_hex
        console = Console()
        rainbow = [
                "red", "orange", "yellow", "green", "blue", "indigo", "violet"
                   ]
        if zone.color == "rainbow":
            for i, c in enumerate(zone.name):
                idx = i % len(rainbow)
                console.print(
                    f"{c}",
                    style=hex_color(rainbow[idx]),
                    end="",
                )
        elif zone.color.lower() == "none":
            console.print(f"{zone.name}", end="")
        else:
            console.print(f"{zone.name}", style=zone.color, end="")
        console.print(" ", end="")

    @staticmethod
    def print_drone_log(drone: Drone) -> None:
        """Print one drone movement entry for the current turn."""
        print(f"D{drone.id}-", end="")
        if drone.in_transit:
            _, zone_a, zone_b = drone.connection
            Renderer.print_line(zone_a)
            Renderer.print_line(zone_b)
        else:
            Renderer.print_line(drone.zone)

    @staticmethod
    def print_moves(graph: Graph) -> None:
        """Print all drone moves that happened during the turn."""
        for drone in graph.drones:
            if drone.moved:
                Renderer.print_drone_log(drone)

    @staticmethod
    def print_hub_occupancy(graph: Graph) -> None:
        """Print the occupancy of hubs that have at least one drone"""
        if any(hub.size for hub in graph.hubs):
            print("| hubs: ", end="")
        for hub in graph.hubs:
            if hub.size:
                Renderer.print_line(hub)
                print(f": {hub.size}/{hub.cap}", end=" ")

    @staticmethod
    def print_con_occupancy(graph: Graph) -> None:
        """
        Print the occupancy of the connections that have at least one drone
        """
        (
            print("| connection: ", end="")
            if any([drone.in_transit for drone in graph.drones])
            else None
        )
        for drone in graph.drones:
            if drone.in_transit:
                occupancy, zone_a, zone_b = drone.connection
                size, cap = occupancy
                Renderer.print_line(zone_a)
                print("- ", end="")
                Renderer.print_line(zone_b)
                print(f"{size}/\
{cap}", end=" ")
