from __future__ import annotations

import argparse
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Callable, Dict, Optional

from astar import a_star
from bfs import bfs
from map_utils import Grid, SearchResult, load_map, overlay_map_text
from ucs import ucs
from visualization import GridVisualizer, animate_result

BASE_DIR = Path(__file__).resolve().parent
MAP_DIR = BASE_DIR / "test_maps"

ALGORITHMS: Dict[str, Callable[[Grid, tuple[int, int], tuple[int, int]], SearchResult]] = {
    "A*": a_star,
    "BFS": bfs,
    "UCS": ucs,
}


class AStarApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("A* Pathfinding Demo")
        self.geometry("1100x700")
        self.minsize(960, 620)

        self.grid_data: Optional[Grid] = None
        self.start = None
        self.goal = None
        self.current_result: Optional[SearchResult] = None

        self.map_var = tk.StringVar(value="map1.txt")
        self.algo_var = tk.StringVar(value="A*")

        self._build_ui()
        self.load_selected_map()

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        controls = ttk.Frame(self, padding=16)
        controls.grid(row=0, column=0, sticky="ns")

        canvas_frame = ttk.Frame(self, padding=16)
        canvas_frame.grid(row=0, column=1, sticky="nsew")
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)

        ttk.Label(controls, text="Project A*", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 12))

        ttk.Label(controls, text="Chọn map:").pack(anchor="w")
        map_choices = sorted(p.name for p in MAP_DIR.glob("*.txt"))
        self.map_combo = ttk.Combobox(controls, textvariable=self.map_var, values=map_choices, state="readonly", width=18)
        self.map_combo.pack(anchor="w", fill="x", pady=(4, 12))

        ttk.Label(controls, text="Chọn thuật toán:").pack(anchor="w")
        self.algo_combo = ttk.Combobox(controls, textvariable=self.algo_var, values=list(ALGORITHMS.keys()), state="readonly", width=18)
        self.algo_combo.pack(anchor="w", fill="x", pady=(4, 12))

        self.load_btn = ttk.Button(controls, text="Load map", command=self.load_selected_map)
        self.load_btn.pack(anchor="w", fill="x", pady=4)

        self.run_btn = ttk.Button(controls, text="Run search", command=self.run_selected_search)
        self.run_btn.pack(anchor="w", fill="x", pady=4)

        self.reset_btn = ttk.Button(controls, text="Reset view", command=self.reset_view)
        self.reset_btn.pack(anchor="w", fill="x", pady=4)

        ttk.Separator(controls, orient="horizontal").pack(fill="x", pady=16)

        self.status_var = tk.StringVar(value="Sẵn sàng.")
        self.expanded_var = tk.StringVar(value="Số nút mở rộng: -")
        self.cost_var = tk.StringVar(value="Chi phí đường đi: -")
        self.time_var = tk.StringVar(value="Thời gian chạy: -")
        self.found_var = tk.StringVar(value="Tìm thấy đường đi: -")

        for var in [self.status_var, self.expanded_var, self.cost_var, self.time_var, self.found_var]:
            ttk.Label(controls, textvariable=var, wraplength=250, justify="left").pack(anchor="w", pady=3)

        ttk.Separator(controls, orient="horizontal").pack(fill="x", pady=16)
        ttk.Label(controls, text="Ghi chú màu:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 8))

        legend = [
            ("#80ed99", "Start"),
            ("#ff6b6b", "Goal"),
            ("#2f2f2f", "Obstacle"),
            ("#bde0fe", "Visited"),
            ("#ffd166", "Final path"),
        ]
        for color, label in legend:
            row = ttk.Frame(controls)
            row.pack(anchor="w", fill="x", pady=2)
            swatch = tk.Canvas(row, width=18, height=18, highlightthickness=0)
            swatch.create_rectangle(0, 0, 18, 18, fill=color, outline="#888888")
            swatch.pack(side="left")
            ttk.Label(row, text=label).pack(side="left", padx=8)

        self.visualizer = GridVisualizer(canvas_frame, cell_size=42)

    def _set_buttons_enabled(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        self.load_btn.config(state=state)
        self.run_btn.config(state=state)
        self.reset_btn.config(state=state)
        self.map_combo.config(state="readonly" if enabled else tk.DISABLED)
        self.algo_combo.config(state="readonly" if enabled else tk.DISABLED)

    def load_selected_map(self) -> None:
        try:
            map_path = MAP_DIR / self.map_var.get()
            self.grid_data, self.start, self.goal = load_map(map_path)
            self.current_result = None
            self.visualizer.draw(self.grid_data, self.start, self.goal)
            self.status_var.set(f"Đã load map: {map_path.name}")
            self.expanded_var.set("Số nút mở rộng: -")
            self.cost_var.set("Chi phí đường đi: -")
            self.time_var.set("Thời gian chạy: -")
            self.found_var.set("Tìm thấy đường đi: -")
        except Exception as exc:
            messagebox.showerror("Load map failed", str(exc))

    def reset_view(self) -> None:
        if self.grid_data is not None and self.start is not None and self.goal is not None:
            self.visualizer.draw(self.grid_data, self.start, self.goal)
            self.status_var.set("Đã reset về trạng thái ban đầu.")

    def run_selected_search(self) -> None:
        if self.grid_data is None or self.start is None or self.goal is None:
            messagebox.showwarning("Missing map", "Vui lòng load map trước khi chạy.")
            return

        algorithm_name = self.algo_var.get()
        algorithm = ALGORITHMS[algorithm_name]

        self._set_buttons_enabled(False)
        self.status_var.set(f"Đang chạy {algorithm_name}...")
        self.visualizer.draw(self.grid_data, self.start, self.goal)

        try:
            result = algorithm(self.grid_data, self.start, self.goal)
            self.current_result = result
            self.expanded_var.set(f"Số nút mở rộng: {result.expanded_nodes}")
            self.cost_var.set(f"Chi phí đường đi: {result.path_cost if result.found else 'Không có'}")
            self.time_var.set(f"Thời gian chạy: {result.runtime_ms:.3f} ms")
            self.found_var.set(f"Tìm thấy đường đi: {'Có' if result.found else 'Không'}")

            def finish_animation() -> None:
                if result.found:
                    self.status_var.set(f"{algorithm_name} hoàn tất. Đã tìm thấy đường đi.")
                else:
                    self.status_var.set(f"{algorithm_name} hoàn tất. Không tìm thấy đường đi.")
                self._set_buttons_enabled(True)

            animate_result(self, self.visualizer, self.grid_data, self.start, self.goal, result, on_done=finish_animation)
        except Exception as exc:
            self._set_buttons_enabled(True)
            messagebox.showerror("Run failed", str(exc))


def run_cli(map_path: str, algorithm_name: str) -> None:
    grid, start, goal = load_map(map_path)
    algorithm = ALGORITHMS[algorithm_name]
    result = algorithm(grid, start, goal)

    print(f"Algorithm      : {result.algorithm}")
    print(f"Found path     : {result.found}")
    print(f"Expanded nodes : {result.expanded_nodes}")
    print(f"Path cost      : {result.path_cost}")
    print(f"Runtime        : {result.runtime_ms:.3f} ms")
    print(f"Path           : {result.path}")
    print("\nMap overlay:")
    print(overlay_map_text(grid, start, goal, result.path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pathfinding project demo with A*, BFS, and UCS.")
    parser.add_argument("--cli", action="store_true", help="Run in command-line mode instead of GUI mode.")
    parser.add_argument("--algo", choices=list(ALGORITHMS.keys()), default="A*", help="Algorithm to run.")
    parser.add_argument("--map", default=str(MAP_DIR / "map1.txt"), help="Path to the map file.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.cli:
        run_cli(args.map, args.algo)
    else:
        app = AStarApp()
        app.mainloop()
