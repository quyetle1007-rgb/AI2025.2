from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

Coord = Tuple[int, int]
Grid = List[List[int]]

FREE = 0
BLOCKED = 1


@dataclass
class SearchResult:
    algorithm: str
    found: bool
    path: List[Coord]
    visited_order: List[Coord]
    expanded_nodes: int
    path_cost: int
    runtime_ms: float


class MapFormatError(ValueError):
    pass


def _tokenize_line(line: str) -> List[str]:
    stripped = line.strip()
    if not stripped:
        return []
    if " " in stripped:
        return stripped.split()
    return list(stripped)


def load_map(path: str | Path) -> Tuple[Grid, Coord, Coord]:
    """Load a map from a text file.

    Supported tokens:
    - S: start
    - G: goal
    - 0: free cell
    - 1: obstacle

    Spaces between tokens are optional.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Map file not found: {path}")

    rows: List[List[int]] = []
    start: Optional[Coord] = None
    goal: Optional[Coord] = None
    width: Optional[int] = None

    for r, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        tokens = _tokenize_line(raw_line)
        if not tokens:
            continue

        if width is None:
            width = len(tokens)
        elif len(tokens) != width:
            raise MapFormatError("Map must be rectangular. Found rows with different lengths.")

        row: List[int] = []
        for c, token in enumerate(tokens):
            if token == "0":
                row.append(FREE)
            elif token == "1":
                row.append(BLOCKED)
            elif token.upper() == "S":
                if start is not None:
                    raise MapFormatError("Map must contain exactly one start cell 'S'.")
                start = (r, c)
                row.append(FREE)
            elif token.upper() == "G":
                if goal is not None:
                    raise MapFormatError("Map must contain exactly one goal cell 'G'.")
                goal = (r, c)
                row.append(FREE)
            else:
                raise MapFormatError(f"Invalid token '{token}' in map file: {path}")
        rows.append(row)

    if not rows:
        raise MapFormatError("Map file is empty.")
    if start is None:
        raise MapFormatError("Map must contain one start cell 'S'.")
    if goal is None:
        raise MapFormatError("Map must contain one goal cell 'G'.")

    return rows, start, goal


def is_within_bounds(grid: Grid, cell: Coord) -> bool:
    r, c = cell
    return 0 <= r < len(grid) and 0 <= c < len(grid[0])


def is_walkable(grid: Grid, cell: Coord) -> bool:
    r, c = cell
    return is_within_bounds(grid, cell) and grid[r][c] == FREE


def get_neighbors(grid: Grid, cell: Coord) -> List[Coord]:
    r, c = cell
    candidates = [
        (r - 1, c),
        (r + 1, c),
        (r, c - 1),
        (r, c + 1),
    ]
    return [neighbor for neighbor in candidates if is_walkable(grid, neighbor)]


def manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct_path(came_from: Dict[Coord, Coord], start: Coord, goal: Coord) -> List[Coord]:
    if goal == start:
        return [start]
    if goal not in came_from:
        return []

    node = goal
    path = [node]
    while node != start:
        node = came_from[node]
        path.append(node)
    path.reverse()
    return path


def overlay_map_text(grid: Grid, start: Coord, goal: Coord, path: Optional[Iterable[Coord]] = None) -> str:
    path_set = set(path or [])
    lines: List[str] = []
    for r in range(len(grid)):
        row_tokens: List[str] = []
        for c in range(len(grid[0])):
            cell = (r, c)
            if cell == start:
                row_tokens.append("S")
            elif cell == goal:
                row_tokens.append("G")
            elif cell in path_set:
                row_tokens.append("*")
            elif grid[r][c] == BLOCKED:
                row_tokens.append("1")
            else:
                row_tokens.append("0")
        lines.append(" ".join(row_tokens))
    return "\n".join(lines)
