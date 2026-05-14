import argparse
import math
import sys
from dataclasses import dataclass
from typing import Dict, Iterable

import pygame
import webcolors

from algo import Dijkestra
from graph_creation import Drone, Graph, Hub, State
from parsing import ParsingError


BACKGROUND = (18, 21, 27)
EDGE_COLOR = (90, 102, 120)
TEXT_COLOR = (230, 235, 245)
DRONE_READY_COLOR = (100, 220, 255)
DRONE_WAITING_COLOR = (255, 170, 80)
HUB_FALLBACK_COLOR = (120, 160, 220)
HUB_BORDER_COLOR = (245, 245, 245)


@dataclass
class Layout:
    min_x: int
    max_y: int
    scale: float
    offset_x: float
    offset_y: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Visualize fly_in simulation with pygame"
    )
    parser.add_argument("map_path", help="Path to map file")
    parser.add_argument(
        "--fps",
        type=int,
        default=4,
        help="Simulation steps per second (default: 4)",
    )
    parser.add_argument(
        "--width", type=int, default=3560, help="Window width (default: 1280)"
    )
    parser.add_argument(
        "--height", type=int, default=1600, help="Window height (default: 800)"
    )
    return parser.parse_args()


def load_graph(map_path: str) -> Graph:
    with open(map_path, "r") as map_file:
        lines = [
            line.strip()
            for line in map_file
            if len(line.strip()) and not line.strip().startswith("#")
        ]
    return Graph(lines)


def rainbow_color(phase: float) -> tuple[int, int, int]:
    red = int((math.sin(phase) + 1.0) * 127.5)
    green = int((math.sin(phase + (2.0 * math.pi / 3.0)) + 1.0) * 127.5)
    blue = int((math.sin(phase + (4.0 * math.pi / 3.0)) + 1.0) * 127.5)
    return (red, green, blue)


def hub_color(hub: Hub, phase: float) -> tuple[int, int, int]:
    if hub.color.lower() == "rainbow":
        return rainbow_color(phase)
    if hub.color == "None":
        return HUB_FALLBACK_COLOR
    try:
        color = webcolors.name_to_rgb(hub.color.lower())
        return (color.red, color.green, color.blue)
    except ValueError:
        return HUB_FALLBACK_COLOR


def compute_layout(
    hubs: Iterable[Hub], width: int, height: int, margin: int = 80
) -> Layout:
    x_values = [hub.cod[0] for hub in hubs]
    y_values = [hub.cod[1] for hub in hubs]
    min_x = min(x_values)
    max_x = max(x_values)
    min_y = min(y_values)
    max_y = max(y_values)

    span_x = max(1, max_x - min_x)
    span_y = max(1, max_y - min_y)
    scale = min(
        (width - (2 * margin)) / span_x,
        (height - (2 * margin)) / span_y,
    )

    used_width = span_x * scale
    used_height = span_y * scale
    offset_x = (width - used_width) / 2.0
    offset_y = (height - used_height) / 2.0

    return Layout(
        min_x=min_x,
        max_y=max_y,
        scale=scale,
        offset_x=offset_x,
        offset_y=offset_y,
    )


def hub_pos(hub: Hub, layout: Layout) -> tuple[int, int]:
    x_coord = layout.offset_x + ((hub.cod[0] - layout.min_x) * layout.scale)
    y_coord = layout.offset_y + ((layout.max_y - hub.cod[1]) * layout.scale)
    return int(x_coord), int(y_coord)


def step_simulation(graph: Graph) -> None:
    # This intentionally mirrors fly_in.py's current loop logic exactly.
    for drone in graph.drones:
        Dijkestra.choose_zone(drone, graph)
    for drone in graph.drones:
        if drone.in_transit:
            continue
        Dijkestra.move_drone(drone)


def draw_graph(
    surface: pygame.Surface,
    graph: Graph,
    layout: Layout,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    step_count: int,
    sim_fps: int,
    paused: bool,
    error_text: str | None,
    phase: float,
) -> None:
    surface.fill(BACKGROUND)

    drawn_pairs = set()
    for hub in graph.hubs:
        x1, y1 = hub_pos(hub, layout)
        for connection in hub.connections:
            other = connection.hub
            pair = tuple(sorted((hub.name, other.name)))
            if pair in drawn_pairs:
                continue
            drawn_pairs.add(pair)
            x2, y2 = hub_pos(other, layout)
            pygame.draw.line(surface, EDGE_COLOR, (x1, y1), (x2, y2), 2)

    for hub in graph.hubs:
        position = hub_pos(hub, layout)
        radius = (
            27 if hub.name in {graph.start.name, graph.finish.name} else 24
        )
        fill = hub_color(hub, phase)
        pygame.draw.circle(surface, fill, position, radius)
        pygame.draw.circle(surface, HUB_BORDER_COLOR, position, radius, 2)

        zone_type_label = small_font.render(hub.zone, True, TEXT_COLOR)
        zone_type_rect = zone_type_label.get_rect(
            center=(position[0], position[1] - 41)
        )
        surface.blit(zone_type_label, zone_type_rect)

        name_label = small_font.render("--".join([hub.name[0:2], str(hub.size), str(hub.cap)]), True, TEXT_COLOR)
        name_rect = name_label.get_rect(center=(position[0], position[1] - 25))
        surface.blit(name_label, name_rect)

    grouped_drones: Dict[str, list[Drone]] = {}
    for drone in graph.drones:
        grouped_drones.setdefault(drone.zone.name, []).append(drone)

    for hub_name, drones in grouped_drones.items():
        hub = next(h for h in graph.hubs if h.name == hub_name)
        center_x, center_y = hub_pos(hub, layout)
        count = len(drones)
        orbit_radius = 9 if count == 1 else 13
        for idx, drone in enumerate(drones):
            angle = (2.0 * math.pi * idx) / count if count else 0.0
            drone_x = int(center_x + (math.cos(angle) * orbit_radius))
            drone_y = int(center_y + (math.sin(angle) * orbit_radius))
            color = (
                DRONE_WAITING_COLOR
                if drone.state == State.WAITING
                else DRONE_READY_COLOR
            )
            pygame.draw.circle(surface, color, (drone_x, drone_y), 4)

    finished = sum(1 for drone in graph.drones if drone.zone == graph.finish)
    waiting = sum(1 for drone in graph.drones if drone.state == State.WAITING)
    status = (
        f"step={step_count}  done={finished}/{len(graph.drones)}  "
        f"waiting={waiting}  speed={sim_fps}/s  "
        f"{'paused' if paused else 'running'}"
    )
    info = font.render(status, True, TEXT_COLOR)
    surface.blit(info, (18, 14))

    hint = small_font.render(
        (
            "Space single-step | P pause/resume | Right single-step | "
            "Up/Down speed | R reset | Q/Esc quit"
        ),
        True,
        (190, 200, 220),
    )
    surface.blit(hint, (18, 46))

    if error_text:
        error_surface = font.render(
            f"Error: {error_text}", True, (255, 130, 130)
        )
        surface.blit(error_surface, (18, 74))


def main() -> None:
    args = parse_args()
    if args.fps < 1:
        raise ValueError("--fps must be at least 1")

    pygame.init()
    pygame.display.set_caption("fly_in visualizer")
    screen = pygame.display.set_mode((args.width, args.height))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 22)
    small_font = pygame.font.SysFont("monospace", 15)

    graph = load_graph(args.map_path)
    layout = compute_layout(graph.hubs, args.width, args.height)

    paused = True
    step_count = 0
    phase = 0.0
    error_text: str | None = None
    sim_fps = args.fps
    accumulated_ms = 0.0

    running = True
    while running:
        frame_ms = clock.tick(60)
        phase += frame_ms * 0.006

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
                elif event.key == pygame.K_SPACE:
                    if paused and not error_text:
                        if any(
                            drone.zone != graph.finish for drone in graph.drones
                        ):
                            try:
                                step_simulation(graph)
                                step_count += 1
                            except ValueError as err:
                                error_text = str(err)
                    else:
                        paused = True
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_RIGHT and paused and not error_text:
                    if any(
                        drone.zone != graph.finish for drone in graph.drones
                    ):
                        try:
                            step_simulation(graph)
                            step_count += 1
                        except ValueError as err:
                            error_text = str(err)
                elif event.key == pygame.K_r:
                    graph = load_graph(args.map_path)
                    layout = compute_layout(
                        graph.hubs,
                        args.width,
                        args.height,
                    )
                    paused = True
                    step_count = 0
                    accumulated_ms = 0.0
                    error_text = None
                elif event.key == pygame.K_UP:
                    sim_fps = min(60, sim_fps + 1)
                elif event.key == pygame.K_DOWN:
                    sim_fps = max(1, sim_fps - 1)

        if (
            not paused
            and not error_text
            and any(drone.zone != graph.finish for drone in graph.drones)
        ):
            accumulated_ms += frame_ms
            ms_per_step = 1000.0 / sim_fps
            while accumulated_ms >= ms_per_step:
                accumulated_ms -= ms_per_step
                try:
                    step_simulation(graph)
                    step_count += 1
                except ValueError as err:
                    error_text = str(err)
                    paused = True
                    break

        draw_graph(
            surface=screen,
            graph=graph,
            layout=layout,
            font=font,
            small_font=small_font,
            step_count=step_count,
            sim_fps=sim_fps,
            paused=paused,
            error_text=error_text,
            phase=phase,
        )
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except (
        ParsingError,
        IsADirectoryError,
        PermissionError,
        FileNotFoundError,
        ValueError,
    ) as error:
        print(error)
        sys.exit(1)
