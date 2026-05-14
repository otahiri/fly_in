*This project has been created as part of the 42 curriculum by otahiri-.*

# Fly-in

## Description
Fly-in is a drone-routing simulation project.
The goal is to move all drones from a `start_hub` to an `end_hub` in the fewest simulation turns while respecting zone and connection constraints.

This implementation parses a map file, builds a graph of hubs/connections, computes drone moves turn by turn, and prints the simulation output in the required format.

## Instructions

### Prerequisites
- Python `3.10+`
- uv

### Installation
```bash
uv sync
```

### Run
```bash
uv run python3 fly_in.py [insert_map_path]
# or
make run MAP=[insert_map_path]
```

### Debug
```bash
python3 -m pdb fly_in.py [insert_map_path]
# or
make debug MAP=[insert_map_path]
```

### Lint / Type-check
```bash
make lint
```

### Clean cache files
```bash
make clean
```

## Input format (map file)
The parser expects:
- `nb_drones: <positive_integer>`
- exactly one `start_hub: <name> <x> <y> [metadata]`
- exactly one `end_hub: <name> <x> <y> [metadata]`
- zero or more `hub: <name> <x> <y> [metadata]`
- connections as `connection: <hub1>-<hub2> [max_link_capacity=<n>]`

Supported hub metadata:
- `zone=normal|blocked|restricted|priority`
- `color=<named_color|rainbow>`
- `max_drones=<positive_integer>`

## Output format
The simulation prints one line per turn.
Each movement is formatted as:
- `D<ID>-<zone>`
- or `D<ID>-<connection>` when crossing toward a restricted zone

Example:
```text
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```

## Algorithm choices and implementation strategy
This project uses:
1. **Parsing + validation layer** to enforce map structure, metadata validity, unique hubs/connections, and required start/end definitions.
2. **Graph modeling** with hub capacities and bidirectional connections (including link capacity).
3. **Pathfinding strategy based on Dijkstra-style cost evaluation**:
   - avoids blocked zones
   - accounts for occupancy pressure (`size/capacity`)
   - accounts for zone behavior (`restricted`, `priority`)
4. **Turn-based scheduling**:
   - each drone selects a feasible next move
   - capacity constraints are checked before movement
   - movement is applied per turn until all drones reach `end_hub`
5. **Restricted-zone handling**:
   - movement into restricted zones is treated as multi-turn transit
   - drones in transit are represented in output as connection-based movement

## Visual representation
Current visualization is **terminal-based step-by-step simulation output** (one line per turn), which helps track:
- which drones moved on each turn
- routing decisions over time
- congestion/capacity effects during simulation

Additional visual features:
- [insert whether you implemented colored terminal output]
- [insert whether you implemented a graphical viewer]
- [insert screenshot path or demo gif if available]

## Resources

### Classic references
- [insert source: graph theory / shortest-path reference]
- [insert source: Dijkstra algorithm documentation]
- [insert source: Python typing / mypy docs]
- [insert source: parsing/regex reference]
- [insert source: any article/tutorial used]

### AI usage
AI was used for:
- **debugging code**
- **research**

Details:
- Tool(s): [insert AI tool name(s)]
- Tasks: debugging parser/pathfinding issues, researching algorithm and implementation ideas
- Project parts impacted: [insert files or modules, e.g. `parsing.py`, `algo.py`]
- Validation method: [insert how you verified/cross-checked AI output]
