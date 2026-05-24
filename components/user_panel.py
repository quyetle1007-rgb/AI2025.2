import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time

import metro_ui  # Import file chính để lấy màu sắc cấu hình và thuật toán
from algorithms.astar import find_path_astar
from algorithms.bfs import find_path_bfs
from algorithms.ucs import find_path_ucs
from components.map_view import MetroMapVisualizer, load_line_info_from_json


class UserScreen(tk.Frame):
    def __init__(self, parent, state):
        super().__init__(parent, bg=metro_ui.CLR_BG)
        self.state = state
        state.register_scenario_change(self._refresh_warning)
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(1, weight=1); self.rowconfigure(0, weight=1)

        left = tk.Frame(self, bg=metro_ui.CLR_PANEL, width=360)
        left.grid(row=0, column=0, sticky="nsew")
        left.pack_propagate(False)

        tk.Label(left, text="METRO NAVIGATOR", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_ACCENT, font=("Arial", 16, "bold")).pack(pady=(25, 2), padx=25, anchor="w")
        tk.Label(left, text="Brussels Smart Transit System", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_SUBTEXT, font=("Arial", 9)).pack(padx=25, anchor="w")

        self.warn_frame = tk.Frame(left, bg="#fff3cd")
        self.warn_label = tk.Label(self.warn_frame, text="", bg="#fff3cd", fg="#856404", font=("Arial", 9), wraplength=300)
        self.warn_label.pack(padx=10, pady=8)

        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=15, padx=25)

        # PHẦN TÙY CHỌN TUYẾN ĐƯỜNG ĐỂ XEM LẦN ĐẦU
        tk.Label(left, text="LỌC XEM TUYẾN ĐƯỜNG", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_SUBTEXT, font=("Arial", 8, "bold")).pack(padx=25, anchor="w")
        self.line_combo = ttk.Combobox(left, values=["Tất cả các tuyến", "Tuyến 1", "Tuyến 2", "Tuyến 5", "Tuyến 6"], state="readonly", font=("Arial", 10))
        self.line_combo.current(0)
        self.line_combo.pack(fill="x", padx=25, pady=(5, 15))
        self.line_combo.bind("<<ComboboxSelected>>", self._on_line_filter_change)

        suggestions = [(sid, s.name) for sid, s in sorted(self.state.mg.stations.items(), key=lambda x: x[1].name)]

        tk.Label(left, text="GA XUẤT PHÁT", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_SUBTEXT, font=("Arial", 8, "bold")).pack(padx=25, anchor="w")
        self.entry_start = metro_ui.AutocompleteEntry(left, suggestions)
        self.entry_start.pack(fill="x", padx=25, pady=(5, 15))

        tk.Label(left, text="GA ĐẾN", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_SUBTEXT, font=("Arial", 8, "bold")).pack(padx=25, anchor="w")
        self.entry_end = metro_ui.AutocompleteEntry(left, suggestions)
        self.entry_end.pack(fill="x", padx=25, pady=(5, 15))

        tk.Label(left, text="THUẬT TOÁN TÌM KIẾM", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_SUBTEXT, font=("Arial", 8, "bold")).pack(padx=25, anchor="w")
        self.algo_combo = ttk.Combobox(left, values=["A*", "BFS", "UCS"], state="readonly", font=("Arial", 10))
        self.algo_combo.current(0)
        self.algo_combo.pack(fill="x", padx=25, pady=(5, 20))

        btn_f = tk.Frame(left, bg=metro_ui.CLR_PANEL)
        btn_f.pack(fill="x", padx=25)
        self.btn_find = tk.Button(btn_f, text="TÌM ĐƯỜNG NGAY", bg=metro_ui.CLR_ACCENT, fg="white", font=("Arial", 11, "bold"), relief="flat", command=self._find_route, cursor="hand2")
        self.btn_find.pack(side="left", fill="x", expand=True, ipady=10)
        tk.Button(btn_f, text="✕", bg=metro_ui.CLR_ACCENT2, fg=metro_ui.CLR_TEXT, relief="flat", width=4, command=self._clear_all).pack(side="left", padx=(5, 0), ipady=10)

        self.stats_label = tk.Label(left, text="", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_SUCCESS, font=("Arial", 9, "italic"))
        self.stats_label.pack(pady=(15, 0), padx=25, anchor="w")

        self.result_box = tk.Text(left, bg=metro_ui.CLR_CARD, fg=metro_ui.CLR_TEXT, font=("Consolas", 10), relief="flat", padx=15, pady=15, state="disabled")
        self.result_box.pack(fill="both", expand=True, padx=25, pady=20)
        self.result_box.tag_config("title", foreground=metro_ui.CLR_ACCENT, font=("Consolas", 11, "bold"))
        self.result_box.tag_config("transfer", foreground=metro_ui.CLR_WARN)

        # ── BẢN ĐỒ BÊN PHẢI: MetroMapVisualizer (Sơn) ──
        right_frame = tk.Frame(self, bg=metro_ui.CLR_BG)
        right_frame.grid(row=0, column=1, sticky="nsew")

        line_colors, line_station_order = load_line_info_from_json(metro_ui.DATA_FILE)
        self.visualizer = MetroMapVisualizer(
            right_frame, self.state.mg, line_colors, line_station_order
        )
        self.visualizer.draw_network()
        self._refresh_warning()

    def _on_line_filter_change(self, _=None):
        """Khi chọn lọc tuyến, vẽ lại mạng lưới theo tuyến đã chọn."""
        selected = self.line_combo.get()
        filter_line = selected.split(" ")[-1] if "Tuyến" in selected else None
        self.visualizer.draw_network(filter_line=filter_line)

    def _refresh_warning(self):
        active = [sc for sc in self.state.manager.list_scenarios() if sc.active]
        active_names = [sc.name for sc in active]
        if active_names:
            self.warn_label.config(text=f"⚠️ SỰ CỐ HOẠT ĐỘNG: {', '.join(active_names)}")
            self.warn_frame.pack(fill="x", padx=25, pady=(15, 0))
        else:
            self.warn_frame.pack_forget()

        # Đánh dấu ga đóng trên bản đồ (Sơn — visualization)
        closed_ids = []
        for sc in active:
            closed_ids.extend(sc.closed_stations)
        self.visualizer.mark_closed_stations(closed_ids)

    def _find_route(self):
        sid_start, _ = self.entry_start.get_selected()
        sid_end, _ = self.entry_end.get_selected()
        algo = self.algo_combo.get()
        if not sid_start or not sid_end: return

        self.btn_find.config(state="disabled", text="ĐANG TÍNH...")
        def run():
            mg_use = self.state.manager.get_modified_graph(self.state.mg)
            t_start = time.perf_counter()
            if algo == "A*": result = find_path_astar(mg_use, sid_start, sid_end)
            elif algo == "BFS": result = find_path_bfs(mg_use, sid_start, sid_end)
            else: result = find_path_ucs(mg_use, sid_start, sid_end)
            duration_ms = (time.perf_counter() - t_start) * 1000
            self.after(0, lambda: self._display_result(result, duration_ms, algo))
        threading.Thread(target=run, daemon=True).start()

    def _display_result(self, result, duration, algo):
        self.btn_find.config(state="normal", text="TÌM ĐƯỜNG NGAY")
        self.visualizer.clear_highlight()
        if "error" in result:
            messagebox.showerror("Lỗi", result["error"]); return

        self.stats_label.config(text=f"✔ {algo}: {len(result['path'])} ga | {duration:.2f} ms")
        self.result_box.config(state="normal")
        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, f"LỘ TRÌNH TỐI ƯU ({algo})\n", "title")
        self.result_box.insert(tk.END, f"⏱ Tổng thời gian: {result['total_time_min']} phút\n")
        self.result_box.insert(tk.END, f"🔄 Đổi tuyến: {result['transfers']} lần\n\n")

        path, lines_used = result["path"], result.get("path_lines", [])
        prev_line = None
        for i, sid in enumerate(path):
            name = self.state.mg.stations[sid].name
            curr_line = lines_used[i] if i < len(lines_used) else None
            if i > 0 and curr_line and prev_line and curr_line != prev_line:
                self.result_box.insert(tk.END, f"  [Đổi sang Tuyến {curr_line}]\n", "transfer")
            prefix = "🟢" if i == 0 else ("🔴" if i == len(path)-1 else "●")
            self.result_box.insert(tk.END, f"{prefix} {name}\n")
            prev_line = curr_line
        self.result_box.config(state="disabled")

        # Highlight lộ trình trên bản đồ (Sơn — visualization)
        self.visualizer.highlight_route(result["path"], result.get("path_lines", []))

    def _clear_all(self):
        self.entry_start.clear(); self.entry_end.clear()
        self.visualizer.clear_highlight()
        self.line_combo.current(0)
        self.visualizer.draw_network()
        self.stats_label.config(text="")

        self.result_box.config(state="normal")
        self.result_box.delete("1.0", tk.END)
        self.result_box.config(state="disabled")
