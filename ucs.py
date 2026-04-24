from __future__ import annotations

import heapq
import time
from itertools import count
from typing import Dict, List, Tuple

from map_utils import Coord, Grid, SearchResult, get_neighbors, reconstruct_path


def ucs(grid: Grid, start: Coord, goal: Coord) -> SearchResult:
    start_time = time.perf_counter()

    priority_queue: List[Tuple[int, int, Coord]] = []
    serial = count()
    heapq.heappush(priority_queue, (0, next(serial), start))

    came_from: Dict[Coord, Coord] = {}
    best_cost: Dict[Coord, int] = {start: 0}
    closed = set()
    visited_order: List[Coord] = []

    while priority_queue:
        current_cost, _, current = heapq.heappop(priority_queue)
        if current in closed:
            continue

        closed.add(current)
        visited_order.append(current)

        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return SearchResult(
                algorithm="UCS",
                found=True,
                path=path,
                visited_order=visited_order,
                expanded_nodes=len(visited_order),
                path_cost=len(path) - 1,
                runtime_ms=elapsed_ms,
            )

        for neighbor in get_neighbors(grid, current):
            new_cost = current_cost + 1
            if new_cost < best_cost.get(neighbor, float("inf")):
                best_cost[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(priority_queue, (new_cost, next(serial), neighbor))

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return SearchResult(
        algorithm="UCS",
        found=False,
        path=[],
        visited_order=visited_order,
        expanded_nodes=len(visited_order),
        path_cost=0,
        runtime_ms=elapsed_ms,
    )


if __name__ == "__main__":
    from map_utils import load_map, overlay_map_text

    grid, start, goal = load_map("test_maps/map1.txt")
    result = ucs(grid, start, goal)
    print(result)
    print(overlay_map_text(grid, start, goal, result.path))
