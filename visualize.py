"""Rendering helpers for terminal output of simulation movement logs."""

from rich import print
from rich.console import Console
from graph_creation import Drone, Graph, Hub
from webcolors import name_to_hex


class Renderer:
    """Render drones, hubs, and occupancy details to terminal output."""

    @staticmethod
    def print_line(zone: Hub, connection: bool = False) -> None:
        """Render one hub label using the configured color rules.

        Args:
            zone: Hub whose name and color metadata are rendered.
            connection: ``True`` when label is part of a connection pair.

        Returns:
            None
        """
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
        console.print(" ", end="") if not connection else None

    @staticmethod
    def print_drone_log(drone: Drone) -> None:
        """Render one drone movement token for the current turn.

        Args:
            drone: Drone to render from current movement state.

        Returns:
            None
        """
        print(f"D{drone.id}-", end="")
        if drone.in_transit:
            _, zone_a, zone_b = drone.connection
            Renderer.print_line(zone_a, True)
            print("-", end="")
            Renderer.print_line(zone_b)
        else:
            Renderer.print_line(drone.zone)

    @staticmethod
    def print_moves(graph: Graph) -> None:
        """Print all drone moves that occurred during the current turn.

        Args:
            graph: Graph containing all drones and their movement state.

        Returns:
            None
        """
        for drone in graph.drones:
            if drone.moved:
                Renderer.print_drone_log(drone)

    @staticmethod
    def print_hub_occupancy(graph: Graph) -> None:
        """Print occupancy for hubs that currently contain at least one drone.

        Args:
            graph: Graph containing hub occupancy state.

        Returns:
            None
        """
        if any(hub.size for hub in graph.hubs):
            print("| hubs: ", end="")
        for hub in graph.hubs:
            if hub.size:
                Renderer.print_line(hub)
                print(f": {hub.size}/{hub.cap}", end=" ")

    @staticmethod
    def print_con_occupancy(graph: Graph) -> None:
        """Print occupancy for connections that currently contain drones.

        Args:
            graph: Graph containing drone transit state.

        Returns:
            None
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
                print("-", end="")
                Renderer.print_line(zone_b)
                print(f"{size}/\
{cap}", end=" ")
