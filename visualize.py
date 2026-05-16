from graph_creation import Drone, Graph
from termcolor import colored


class Renderer:
    @staticmethod
    def construct_log(drone: Drone) -> str:
        if drone.in_transit:
            zone_a, zone_b = drone.connection
            zone_a_name = colored(zone_a.name, zone_a.color) if zone_a.color != "None" else zone_a.name
            zone_b_name = colored(zone_b.name, zone_b.color) if zone_b.color != "None" else zone_b.name
            log = zone_a_name + zone_b_name
        else:
            log = colored(drone.zone.name, drone.zone.color) if drone.zone.color != "None" else drone.zone.name
        return log

    @staticmethod
    def print_moves(graph: Graph):
        print(" ".join([f"D{drone.id} " + Renderer.construct_log(drone) for drone in graph.drones if drone.moved]))
