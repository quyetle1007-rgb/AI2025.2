from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict

from flask import Flask, jsonify, request, send_from_directory

from astar import a_star
from bfs import bfs
from map_utils import Grid, SearchResult, load_map
from ucs import ucs

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
MAP_DIR = BASE_DIR / "test_maps"

ALGORITHMS: Dict[str, Callable[[Grid, tuple[int, int], tuple[int, int]], SearchResult]] = {
    "A*": a_star,
    "BFS": bfs,
    "UCS": ucs,
}

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")


def _validate_grid(grid: list[list[int]]) -> None:
    if not grid or not grid[0]:
        raise ValueError("Grid must not be empty.")
    width = len(grid[0])
    for row in grid:
        if len(row) != width:
            raise ValueError("Grid must be rectangular.")
        for cell in row:
            if cell not in (0, 1):
                raise ValueError("Grid values must be 0 or 1.")


def _validate_point(name: str, point: list[int] | tuple[int, int], grid: list[list[int]]) -> tuple[int, int]:
    if not isinstance(point, (list, tuple)) or len(point) != 2:
        raise ValueError(f"{name} must be a pair [row, col].")
    r, c = int(point[0]), int(point[1])
    if not (0 <= r < len(grid) and 0 <= c < len(grid[0])):
        raise ValueError(f"{name} is outside the grid.")
    if grid[r][c] == 1:
        raise ValueError(f"{name} cannot be placed on an obstacle.")
    return (r, c)


def _result_to_json(result: SearchResult) -> dict:
    return {
        "algorithm": result.algorithm,
        "found": result.found,
        "path": [list(p) for p in result.path],
        "visited_order": [list(p) for p in result.visited_order],
        "expanded_nodes": result.expanded_nodes,
        "path_cost": result.path_cost,
        "runtime_ms": result.runtime_ms,
    }


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/api/maps")
def list_maps():
    maps = sorted(p.name for p in MAP_DIR.glob("*.txt"))
    return jsonify({"maps": maps})


@app.get("/api/map/<map_name>")
def get_map(map_name: str):
    grid, start, goal = load_map(MAP_DIR / map_name)
    return jsonify({
        "name": map_name,
        "grid": grid,
        "start": list(start),
        "goal": list(goal),
    })


@app.post("/api/search")
def search():
    data = request.get_json(force=True, silent=False)
    algorithm_name = data.get("algorithm", "A*")
    if algorithm_name not in ALGORITHMS:
        return jsonify({"error": f"Unsupported algorithm: {algorithm_name}"}), 400

    grid = data.get("grid")
    start = data.get("start")
    goal = data.get("goal")

    try:
        _validate_grid(grid)
        start_coord = _validate_point("Start", start, grid)
        goal_coord = _validate_point("Goal", goal, grid)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    result = ALGORITHMS[algorithm_name](grid, start_coord, goal_coord)
    return jsonify(_result_to_json(result))


@app.get("/<path:path>")
def static_proxy(path: str):
    return send_from_directory(FRONTEND_DIR, path)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
