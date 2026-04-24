from __future__ import annotations

import heapq
import time
from itertools import count
from typing import Dict, List, Tuple

from map_utils import Coord, Grid, SearchResult, get_neighbors, manhattan, reconstruct_path


def a_star(grid: Grid, start: Coord, goal: Coord) -> SearchResult:
    start_time = time.perf_counter()

    open_heap: List[Tuple[int, int, int, Coord]] = []
    serial = count()
    heapq.heappush(open_heap, (manhattan(start, goal), 0, next(serial), start))

    came_from: Dict[Coord, Coord] = {}
    g_score: Dict[Coord, int] = {start: 0}
    closed = set()
    visited_order: List[Coord] = []

    while open_heap:
        _, current_g, _, current = heapq.heappop(open_heap)
        if current in closed:
            continue

        closed.add(current)
        visited_order.append(current)

        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return SearchResult(
                algorithm="A*",
                found=True,
                path=path,
                visited_order=visited_order,
                expanded_nodes=len(visited_order),
                path_cost=len(path) - 1,
                runtime_ms=elapsed_ms,
            )

        for neighbor in get_neighbors(grid, current):
            tentative_g = current_g + 1
            if tentative_g < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                f_score = tentative_g + manhattan(neighbor, goal)
                heapq.heappush(open_heap, (f_score, tentative_g, next(serial), neighbor))

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return SearchResult(
        algorithm="A*",
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
    result = a_star(grid, start, goal)
    print(result)
    print(overlay_map_text(grid, start, goal, result.path))
