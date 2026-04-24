from __future__ import annotations

import time
from collections import deque
from typing import Deque, Dict, List, Set

from map_utils import Coord, Grid, SearchResult, get_neighbors, reconstruct_path


def bfs(grid: Grid, start: Coord, goal: Coord) -> SearchResult:
    start_time = time.perf_counter()

    queue: Deque[Coord] = deque([start])
    seen: Set[Coord] = {start}
    came_from: Dict[Coord, Coord] = {}
    visited_order: List[Coord] = []

    while queue:
        current = queue.popleft()
        visited_order.append(current)

        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return SearchResult(
                algorithm="BFS",
                found=True,
                path=path,
                visited_order=visited_order,
                expanded_nodes=len(visited_order),
                path_cost=len(path) - 1,
                runtime_ms=elapsed_ms,
            )

        for neighbor in get_neighbors(grid, current):
            if neighbor not in seen:
                seen.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return SearchResult(
        algorithm="BFS",
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
    result = bfs(grid, start, goal)
    print(result)
    print(overlay_map_text(grid, start, goal, result.path))
