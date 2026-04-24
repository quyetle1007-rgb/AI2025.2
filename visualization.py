from __future__ import annotations

import tkinter as tk
from typing import Callable, Iterable, Optional, Set

from map_utils import Coord, Grid, SearchResult


class GridVisualizer:
    def __init__(self, parent: tk.Widget, cell_size: int = 40) -> None:
        self.cell_size = cell_size
        self.canvas = tk.Canvas(parent, bg="white", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack(fill="both", expand=True)

    def resize_for_grid(self, grid: Grid) -> None:
        rows = len(grid)
        cols = len(grid[0])
        width = cols * self.cell_size
        height = rows * self.cell_size
        self.canvas.config(width=width, height=height, scrollregion=(0, 0, width, height))

    def draw(
        self,
        grid: Grid,
        start: Coord,
        goal: Coord,
        visited: Optional[Iterable[Coord]] = None,
        path: Optional[Iterable[Coord]] = None,
    ) -> None:
        visited_set: Set[Coord] = set(visited or [])
        path_set: Set[Coord] = set(path or [])

        self.resize_for_grid(grid)
        self.canvas.delete("all")

        for r in range(len(grid)):
            for c in range(len(grid[0])):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                cell = (r, c)
                fill = "white"
                label = ""
                text_fill = "black"

                if grid[r][c] == 1:
                    fill = "#2f2f2f"
                elif cell in visited_set:
                    fill = "#bde0fe"
                if cell in path_set:
                    fill = "#ffd166"
                if cell == start:
                    fill = "#80ed99"
                    label = "S"
                elif cell == goal:
                    fill = "#ff6b6b"
                    label = "G"
                    text_fill = "white"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#aaaaaa")
                if label:
                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text=label,
                        fill=text_fill,
                        font=("Arial", 12, "bold"),
                    )


def animate_result(
    root: tk.Misc,
    visualizer: GridVisualizer,
    grid: Grid,
    start: Coord,
    goal: Coord,
    result: SearchResult,
    on_done: Optional[Callable[[], None]] = None,
    delay_ms: int = 35,
) -> None:
    visited_so_far = []
    index = 0

    def step() -> None:
        nonlocal index
        if index < len(result.visited_order):
            visited_so_far.append(result.visited_order[index])
            visualizer.draw(grid, start, goal, visited=visited_so_far)
            index += 1
            root.after(delay_ms, step)
        else:
            visualizer.draw(grid, start, goal, visited=visited_so_far, path=result.path)
            if on_done:
                on_done()

    step()
