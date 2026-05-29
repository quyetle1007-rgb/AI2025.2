import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Optional
import metro_ui
# ─────────────────────────────────────────────
#  PANEL ADMIN: QUẢN LÝ SỰ CỐ HỆ THỐNG (LAYOUT NÂNG CẤP)
# ─────────────────────────────────────────────
class AdminScreen(tk.Frame):
    def __init__(self, parent, state):
        super().__init__(parent, bg=metro_ui.CLR_BG)
        self.state = state
        self._selected_scenario_name: Optional[str] = None
        self._build_ui()

    def _build_ui(self):
        # Thiết lập tỷ lệ hiển thị 2 panel: Trái (1) - Phải (3)
        self.columnconfigure(0, weight=1, minsize=380)
        self.columnconfigure(1, weight=3, minsize=600)
        self.rowconfigure(0, weight=1)

        # ─────────────────────────────────────────────
        #  PANEL TRÁI: QUẢN LÝ & TÌM KIẾM SCENARIOS
        # ─────────────────────────────────────────────
        left_panel = tk.Frame(self, bg=metro_ui.CLR_PANEL, bd=0)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 2))

        tk.Label(left_panel, text="DANH SÁCH SỰ CỐ SYSTEM", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_ACCENT,
                 font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(15, 5))

        # --- THANH TÌM KIẾM SCENARIO ---
        search_frame = tk.Frame(left_panel, bg=metro_ui.CLR_PANEL)
        search_frame.pack(fill="x", padx=15, pady=(0, 10))
        tk.Label(search_frame, text="🔍 Tìm:", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_SUBTEXT, font=("Arial", 10, "bold")).pack(
            side="left", padx=(0, 5))

        self.scen_search_var = tk.StringVar()
        self.scen_search_var.trace_add("write", lambda *args: self._refresh_scenario_list())
        self.scen_search_entry = tk.Entry(search_frame, textvariable=self.scen_search_var, bg=metro_ui.CLR_ACCENT2, fg=metro_ui.CLR_TEXT,
                                          relief="flat", font=("Arial", 10))
        self.scen_search_entry.pack(side="left", fill="x", expand=True, ipady=5, ipadx=5)

        # --- LISTBOX HIỂN THỊ SCENARIOS ---
        self.scen_listbox = tk.Listbox(left_panel, bg=metro_ui.CLR_CARD, fg=metro_ui.CLR_TEXT, selectbackground=metro_ui.CLR_ACCENT, relief="flat",
                                       bd=0, font=("Arial", 11))
        self.scen_listbox.pack(fill="both", expand=True, padx=15, pady=5)
        self.scen_listbox.bind("<<ListboxSelect>>", self._on_scenario_select)

        # --- THANH DIỀU KHIỂN CRUD SCENARIO ---
        btn_frame = tk.Frame(left_panel, bg=metro_ui.CLR_PANEL)
        btn_frame.pack(fill="x", padx=15, pady=15)

        tk.Button(btn_frame, text="Thêm", bg=metro_ui.CLR_ACCENT, fg="white", relief="flat", font=("Arial", 9, "bold"), width=8,
                  command=self._add_scenario, cursor="hand2").pack(side="left", padx=2, ipady=4)
        tk.Button(btn_frame, text="Xóa", bg=metro_ui.CLR_DANGER, fg="white", relief="flat", font=("Arial", 9, "bold"), width=8,
                  command=self._delete_scenario, cursor="hand2").pack(side="left", padx=2, ipady=4)
        tk.Button(btn_frame, text="Bật", bg=metro_ui.CLR_SUCCESS, fg="white", relief="flat", font=("Arial", 9, "bold"), width=8,
                  command=lambda: self._toggle_scenario(True), cursor="hand2").pack(side="left", padx=2, ipady=4)
        tk.Button(btn_frame, text="Tắt", bg=metro_ui.CLR_SUBTEXT, fg="white", relief="flat", font=("Arial", 9, "bold"), width=8,
                  command=lambda: self._toggle_scenario(False), cursor="hand2").pack(side="left", padx=2, ipady=4)

        # ─────────────────────────────────────────────
        #  PANEL PHẢI: CHI TIẾT VÀ QUẢN LÝ HÀNH ĐỘNG
        # ─────────────────────────────────────────────
        self.right_panel = tk.Frame(self, bg=metro_ui.CLR_BG)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)

        self.no_select_label = tk.Label(self.right_panel,
                                        text="Vui lòng chọn hoặc thêm một Sự cố (Scenario) từ danh sách bên trái.",
                                        bg=metro_ui.CLR_BG, fg=metro_ui.CLR_SUBTEXT, font=("Arial", 11, "italic"))
        self.no_select_label.pack(expand=True)

        self.details_frame = tk.Frame(self.right_panel, bg=metro_ui.CLR_BG)

        self.scen_title = tk.Label(self.details_frame, text="Chi tiết Sự cố:", bg=metro_ui.CLR_BG, fg=metro_ui.CLR_TEXT,
                                   font=("Arial", 14, "bold"))
        self.scen_title.pack(anchor="w", pady=(0, 10))

        tables_frame = tk.Frame(self.details_frame, bg=metro_ui.CLR_BG)
        tables_frame.pack(fill="both", expand=True)
        tables_frame.columnconfigure(0, weight=1)
        tables_frame.columnconfigure(1, weight=1)
        tables_frame.columnconfigure(2, weight=1)
        tables_frame.rowconfigure(0, weight=1)

        # --- Bảng 1: Ga Đóng Cửa ---
        f_station = tk.LabelFrame(tables_frame, text="1. Ga Đóng Cửa", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_ACCENT,
                                  font=("Arial", 10, "bold"), padx=10, pady=10)
        f_station.grid(row=0, column=0, sticky="nsew", padx=5)
        self.box_stations = tk.Listbox(f_station, bg=metro_ui.CLR_CARD, fg=metro_ui.CLR_TEXT, bd=0, relief="flat",
                                       selectbackground=metro_ui.CLR_ACCENT)
        self.box_stations.pack(fill="both", expand=True, pady=5)
        tk.Button(f_station, text="+ Thêm Ga Đóng", bg=metro_ui.CLR_ACCENT2, fg=metro_ui.CLR_TEXT, relief="flat",
                  command=self._add_closed_station, cursor="hand2").pack(fill="x", side="bottom", pady=2, ipady=3)
        tk.Button(f_station, text="- Xóa Chọn", bg=metro_ui.CLR_ACCENT2, fg=metro_ui.CLR_DANGER, relief="flat",
                  command=self._delete_closed_station, cursor="hand2").pack(fill="x", side="bottom", ipady=3)

        # --- Bảng 2: Chặng Bị Đóng ---
        f_edge = tk.LabelFrame(tables_frame, text="2. Chặng Đứt Gãy", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_ACCENT,
                               font=("Arial", 10, "bold"), padx=10, pady=10)
        f_edge.grid(row=0, column=1, sticky="nsew", padx=5)
        self.box_edges = tk.Listbox(f_edge, bg=metro_ui.CLR_CARD, fg=metro_ui.CLR_TEXT, bd=0, relief="flat", selectbackground=metro_ui.CLR_ACCENT)
        self.box_edges.pack(fill="both", expand=True, pady=5)
        tk.Button(f_edge, text="+ Thêm Chặng", bg=metro_ui.CLR_ACCENT2, fg=metro_ui.CLR_TEXT, relief="flat",
                  command=self._add_closed_edge, cursor="hand2").pack(fill="x", side="bottom", pady=2, ipady=3)
        tk.Button(f_edge, text="- Xóa Chọn", bg=metro_ui.CLR_ACCENT2, fg=metro_ui.CLR_DANGER, relief="flat",
                  command=self._delete_closed_edge, cursor="hand2").pack(fill="x", side="bottom", ipady=3)

        # --- Bảng 3: Chặng Bị Trì Hoãn ---
        f_delay = tk.LabelFrame(tables_frame, text="3. Chặng Trì Hoãn (Delay)", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_ACCENT,
                                font=("Arial", 10, "bold"), padx=10, pady=10)
        f_delay.grid(row=0, column=2, sticky="nsew", padx=5)
        self.box_delays = tk.Listbox(f_delay, bg=metro_ui.CLR_CARD, fg=metro_ui.CLR_TEXT, bd=0, relief="flat",
                                     selectbackground=metro_ui.CLR_ACCENT)
        self.box_delays.pack(fill="both", expand=True, pady=5)
        tk.Button(f_delay, text="+ Thêm Delay", bg=metro_ui.CLR_ACCENT2, fg=metro_ui.CLR_TEXT, relief="flat", command=self._add_delay,
                  cursor="hand2").pack(fill="x", side="bottom", pady=2, ipady=3)
        tk.Button(f_delay, text="- Xóa Chọn", bg=metro_ui.CLR_ACCENT2, fg=metro_ui.CLR_DANGER, relief="flat", command=self._delete_delay,
                  cursor="hand2").pack(fill="x", side="bottom", ipady=3)

        self._refresh_scenario_list()

    def _refresh_scenario_list(self):
        self.scen_listbox.delete(0, tk.END)
        search_query = self.scen_search_var.get().strip().lower()

        for sc in self.state.manager.list_scenarios():
            # Thực hiện bộ lọc tìm kiếm theo ký tự nhập vào
            if search_query and search_query not in sc.name.lower():
                continue
            status = "[ON]" if sc.active else "[OFF]"
            self.scen_listbox.insert(tk.END, f" {status} {sc.name}")
        self._load_scenario_details()

    def _on_scenario_select(self, _=None):
        idx = self.scen_listbox.curselection()
        if idx:
            full_str = self.scen_listbox.get(idx[0])
            self._selected_scenario_name = full_str.split(" ", 2)[-1]
            self.no_select_label.pack_forget()
            self.details_frame.pack(fill="both", expand=True)
            self._load_scenario_details()

    def _load_scenario_details(self):
        self.box_stations.delete(0, tk.END)
        self.box_edges.delete(0, tk.END)
        self.box_delays.delete(0, tk.END)

        if not self._selected_scenario_name:
            self.details_frame.pack_forget()
            self.no_select_label.pack(expand=True)
            return

        sc = self.state.manager.get_scenario(self._selected_scenario_name)
        if not sc: return

        status_text = "Đang hoạt động" if sc.active else "Đang tắt"
        self.scen_title.config(text=f"Sự cố: {sc.name} ({status_text})")

        for s_id in sc.closed_stations:
            name = self.state.mg.stations[s_id].name if s_id in self.state.mg.stations else s_id
            self.box_stations.insert(tk.END, f"{name} ({s_id})")

        for (u, v, line) in sc.closed_edges:
            un = self.state.mg.stations[u].name if u in self.state.mg.stations else u
            vn = self.state.mg.stations[v].name if v in self.state.mg.stations else v
            self.box_edges.insert(tk.END, f"{un} ⇄ {vn} [L: {line}]")

        for (u, v, line), value in sc.delays.items():
            un = self.state.mg.stations[u].name if u in self.state.mg.stations else u
            vn = self.state.mg.stations[v].name if v in self.state.mg.stations else v
            self.box_delays.insert(tk.END, f"{un} ⇄ {vn} (+{value}m) [L: {line}]")

    def _add_scenario(self):
        name = simpledialog.askstring("Thêm Sự Cố", "Nhập tên sự cố hệ thống mới:")
        if name:
            try:
                self.state.manager.create_scenario(name, "Mô tả sự cố hệ thống")
                self._selected_scenario_name = name
                self._refresh_scenario_list()
                self.state.notify_scenario_change()
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e))

    def _delete_scenario(self):
        if not self._selected_scenario_name: return
        if messagebox.askyesno("Xác nhận",
                               f"Bạn có chắc chắn muốn xóa hoàn toàn sự cố '{self._selected_scenario_name}'?"):
            if hasattr(self.state.manager, 'delete_scenario'):
                self.state.manager.delete_scenario(self._selected_scenario_name)
            else:
                self.state.manager.scenarios.pop(self._selected_scenario_name, None)
                self.state.manager.save()
            self._selected_scenario_name = None
            self._refresh_scenario_list()
            self.state.notify_scenario_change()

    def _toggle_scenario(self, status: bool):
        if not self._selected_scenario_name: return
        sc = self.state.manager.get_scenario(self._selected_scenario_name)
        if sc:
            sc.active = status
            self.state.manager.save()
            self._refresh_scenario_list()
            self.state.notify_scenario_change()

    # ─────────────────────────────────────────────
    #  CÁC THỦ TỤC THÊM HÀNH ĐỘNG CÓ AUTOCOMPLETE
    # ─────────────────────────────────────────────
    def _get_station_suggestions(self):
        return [(sid, s.name) for sid, s in sorted(self.state.mg.stations.items(), key=lambda x: x[1].name)]

    def _add_closed_station(self):
        if not self._selected_scenario_name: return
        sc = self.state.manager.get_scenario(self._selected_scenario_name)

        # Tạo cửa sổ Pop-up độc lập để nhập liệu nâng cao
        dialog = tk.Toplevel(self)
        dialog.title("Đóng Cửa Ga")
        metro_ui.center_window(dialog, 420, 220)
        dialog.configure(bg=metro_ui.CLR_PANEL)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="CHỌN GA CẦN ĐÓNG CỬA", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_ACCENT, font=("Arial", 11, "bold")).pack(
            pady=(20, 10))

        # Tái sử dụng widget Autocomplete gợi ý thông minh
        entry_station = metro_ui.AutocompleteEntry(dialog, self._get_station_suggestions(),
                                                   placeholder="Gõ tên hoặc ID ga để tìm kiếm...")
        entry_station.pack(fill="x", padx=35, pady=10)

        def confirm():
            sid, _ = entry_station.get_selected()
            # Fallback nếu người dùng gõ tay chính xác ID mà không click chuột chọn
            if not sid:
                typed = entry_station.var.get().strip()
                if typed in self.state.mg.stations: sid = typed

            if sid and sid in self.state.mg.stations:
                if sid not in sc.closed_stations:
                    sc.closed_stations.append(sid)
                    self.state.manager.save()
                    self._load_scenario_details()
                    self.state.notify_scenario_change()
                dialog.destroy()
            else:
                messagebox.showerror("Lỗi", "Vui lòng chọn một nhà ga hợp lệ từ danh sách gợi ý!", parent=dialog)

        btn_frame = tk.Frame(dialog, bg=metro_ui.CLR_PANEL)
        btn_frame.pack(fill="x", side="bottom", pady=20, padx=35)
        tk.Button(btn_frame, text="Xác nhận", bg=metro_ui.CLR_ACCENT, fg="white", relief="flat", font=("Arial", 10, "bold"),
                  command=confirm, width=12, cursor="hand2").pack(side="right", padx=5)
        tk.Button(btn_frame, text="Hủy", bg=metro_ui.CLR_ACCENT2, fg=metro_ui.CLR_TEXT, relief="flat", font=("Arial", 10),
                  command=dialog.destroy, width=12, cursor="hand2").pack(side="right")

    def _delete_closed_station(self):
        idx = self.box_stations.curselection()
        if not idx or not self._selected_scenario_name: return
        sc = self.state.manager.get_scenario(self._selected_scenario_name)
        val = self.box_stations.get(idx[0])
        sid = val.split('(')[-1].replace(')', '')
        if sid in sc.closed_stations:
            sc.closed_stations.remove(sid)
            self.state.manager.save()
            self._load_scenario_details()
            self.state.notify_scenario_change()

    def _add_closed_edge(self):
        if not self._selected_scenario_name: return
        sc = self.state.manager.get_scenario(self._selected_scenario_name)
        mg = self.state.mg

        dialog = tk.Toplevel(self)
        dialog.title("Đóng Chặng Đường")
        metro_ui.center_window(dialog, 450, 420)
        dialog.configure(bg=metro_ui.CLR_PANEL)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="THÊM CHẶNG ĐỨT GÃY", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_ACCENT, font=("Arial", 11, "bold")).pack(
            pady=(15, 10))

        suggestions = self._get_station_suggestions()

        tk.Label(dialog, text="Ga bắt đầu (Station U):", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_SUBTEXT, font=("Arial", 9, "bold")).pack(
            anchor="w", padx=35)
        entry_u = metro_ui.AutocompleteEntry(dialog, suggestions, placeholder="Tìm ga bắt đầu...")
        entry_u.pack(fill="x", padx=35, pady=(2, 10))

        tk.Label(dialog, text="Ga kết thúc (Station V):", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_SUBTEXT, font=("Arial", 9, "bold")).pack(
            anchor="w", padx=35)
        entry_v = metro_ui.AutocompleteEntry(dialog, suggestions, placeholder="Tìm ga kết thúc...")
        entry_v.pack(fill="x", padx=35, pady=(2, 10))

        tk.Label(dialog, text="Tuyến đường:", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_SUBTEXT,
                 font=("Arial", 9, "bold")).pack(anchor="w", padx=35)

        line_frame = tk.Frame(dialog, bg=metro_ui.CLR_PANEL)
        line_frame.pack(fill="x", padx=35, pady=(2, 5))

        from tkinter import ttk
        line_combo = ttk.Combobox(line_frame, state="readonly", font=("Arial", 10), values=["← Chọn 2 ga rồi nhấn Tải tuyến"])
        line_combo.pack(side="left", fill="x", expand=True, ipady=3)
        line_combo.current(0)

        # Label trạng thái kiểm tra
        status_label = tk.Label(dialog, text="", bg=metro_ui.CLR_PANEL, font=("Arial", 9, "italic"))
        status_label.pack(anchor="w", padx=35)

        def load_lines():
            """Kiểm tra 2 ga liền kề và tải tuyến hợp lệ vào Combobox."""
            u_id, _ = entry_u.get_selected()
            v_id, _ = entry_v.get_selected()
            if not u_id and entry_u.var.get().strip() in mg.stations:
                u_id = entry_u.var.get().strip()
            if not v_id and entry_v.var.get().strip() in mg.stations:
                v_id = entry_v.var.get().strip()

            if not u_id or u_id not in mg.stations:
                status_label.config(text="⚠ Chưa chọn ga bắt đầu hợp lệ.", fg="#cc0000")
                return
            if not v_id or v_id not in mg.stations:
                status_label.config(text="⚠ Chưa chọn ga kết thúc hợp lệ.", fg="#cc0000")
                return

            # Tìm tất cả tuyến nối trực tiếp u → v
            valid_lines = sorted({e.line_name for e in mg.adj_list.get(u_id, []) if e.v == v_id})

            if not valid_lines:
                u_name = mg.stations[u_id].name
                v_name = mg.stations[v_id].name
                status_label.config(text=f"✕ {u_name} và {v_name} không liền kề!", fg="#cc0000")
                line_combo.config(values=["Không có tuyến hợp lệ"])
                line_combo.current(0)
                return

            # Tải tuyến hợp lệ + option tất cả
            options = [f"* (Tất cả tuyến)"] + [f"Tuyến {l}" for l in valid_lines]
            line_combo.config(values=options)
            line_combo.current(0)
            status_label.config(text=f"✔ Tìm thấy {len(valid_lines)} tuyến hợp lệ.", fg=metro_ui.CLR_SUCCESS)

        tk.Button(line_frame, text="Tải tuyến ↻", bg=metro_ui.CLR_ACCENT, fg="white", relief="flat",
                  font=("Arial", 9, "bold"), command=load_lines, cursor="hand2").pack(side="left", padx=(5, 0), ipady=3)

        def confirm():
            u_id, _ = entry_u.get_selected()
            v_id, _ = entry_v.get_selected()
            if not u_id and entry_u.var.get().strip() in mg.stations:
                u_id = entry_u.var.get().strip()
            if not v_id and entry_v.var.get().strip() in mg.stations:
                v_id = entry_v.var.get().strip()

            if not u_id or u_id not in mg.stations or not v_id or v_id not in mg.stations:
                messagebox.showerror("Lỗi", "Vui lòng chọn 2 ga hợp lệ từ gợi ý!", parent=dialog)
                return

            # Kiểm tra liền kề
            valid_lines = {e.line_name for e in mg.adj_list.get(u_id, []) if e.v == v_id}
            if not valid_lines:
                u_name = mg.stations[u_id].name
                v_name = mg.stations[v_id].name
                messagebox.showerror("Lỗi",
                    f"Ga '{u_name}' và '{v_name}' không nối trực tiếp!\n"
                    f"Chỉ được chọn 2 ga liền kề nhau trên cùng 1 chặng.",
                    parent=dialog)
                return

            # Parse tuyến từ Combobox
            selected = line_combo.get()
            if selected.startswith("*"):
                line = "*"
            elif selected.startswith("Tuyến "):
                line = selected.replace("Tuyến ", "")
            else:
                messagebox.showerror("Lỗi", "Vui lòng nhấn 'Tải tuyến ↻' để chọn tuyến hợp lệ.", parent=dialog)
                return

            # Kiểm tra tuyến cụ thể
            if line != "*" and line not in valid_lines:
                messagebox.showerror("Lỗi", f"Tuyến {line} không tồn tại giữa 2 ga đã chọn!", parent=dialog)
                return

            sc.closed_edges.append((u_id, v_id, line))
            self.state.manager.save()
            self._load_scenario_details()
            self.state.notify_scenario_change()
            dialog.destroy()

        btn_frame = tk.Frame(dialog, bg=metro_ui.CLR_PANEL)
        btn_frame.pack(fill="x", side="bottom", pady=15, padx=35)
        tk.Button(btn_frame, text="Xác nhận", bg=metro_ui.CLR_ACCENT, fg="white", relief="flat", font=("Arial", 10, "bold"),
                  command=confirm, width=12, cursor="hand2").pack(side="right", padx=5)
        tk.Button(btn_frame, text="Hủy", bg=metro_ui.CLR_ACCENT2, fg=metro_ui.CLR_TEXT, relief="flat", font=("Arial", 10),
                  command=dialog.destroy, width=12, cursor="hand2").pack(side="right")

    def _delete_closed_edge(self):
        idx = self.box_edges.curselection()
        if not idx or not self._selected_scenario_name: return
        sc = self.state.manager.get_scenario(self._selected_scenario_name)
        if idx[0] < len(sc.closed_edges):
            sc.closed_edges.pop(idx[0])
            self.state.manager.save()
            self._load_scenario_details()
            self.state.notify_scenario_change()

    def _add_delay(self):
        if not self._selected_scenario_name: return
        sc = self.state.manager.get_scenario(self._selected_scenario_name)

        dialog = tk.Toplevel(self)
        dialog.title("Khai Báo Trì Hoãn (Delay)")
        metro_ui.center_window(dialog, 450, 450)
        dialog.configure(bg=metro_ui.CLR_PANEL)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="THÊM CHẶNG TRÌ HOÃN (DELAY)", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_ACCENT,
                 font=("Arial", 11, "bold")).pack(pady=(15, 10))

        suggestions = self._get_station_suggestions()

        tk.Label(dialog, text="Ga bắt đầu (Station U):", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_SUBTEXT, font=("Arial", 9, "bold")).pack(
            anchor="w", padx=35)
        entry_u = metro_ui.AutocompleteEntry(dialog, suggestions, placeholder="Tìm ga bắt đầu...")
        entry_u.pack(fill="x", padx=35, pady=(2, 10))

        tk.Label(dialog, text="Ga kết thúc (Station V):", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_SUBTEXT, font=("Arial", 9, "bold")).pack(
            anchor="w", padx=35)
        entry_v = metro_ui.AutocompleteEntry(dialog, suggestions, placeholder="Tìm ga kết thúc...")
        entry_v.pack(fill="x", padx=35, pady=(2, 10))

        tk.Label(dialog, text="Tuyến đường (Nhập tên tuyến hoặc *):", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_SUBTEXT,
                 font=("Arial", 9, "bold")).pack(anchor="w", padx=35)
        line_var = tk.StringVar(value="*")
        entry_line = tk.Entry(dialog, textvariable=line_var, bg=metro_ui.CLR_ACCENT2, fg=metro_ui.CLR_TEXT, relief="flat",
                              font=("Segoe UI", 11))
        entry_line.pack(fill="x", padx=35, pady=(2, 10), ipady=5)

        tk.Label(dialog, text="Thời gian hoãn thêm (Đơn vị: phút):", bg=metro_ui.CLR_PANEL, fg=metro_ui.CLR_SUBTEXT,
                 font=("Arial", 9, "bold")).pack(anchor="w", padx=35)
        mins_var = tk.StringVar()
        entry_mins = tk.Entry(dialog, textvariable=mins_var, bg=metro_ui.CLR_ACCENT2, fg=metro_ui.CLR_TEXT, relief="flat",
                              font=("Segoe UI", 11))
        entry_mins.pack(fill="x", padx=35, pady=(2, 15), ipady=5)

        def confirm():
            u_id, _ = entry_u.get_selected()
            v_id, _ = entry_v.get_selected()
            line = line_var.get().strip()
            try:
                mins = float(mins_var.get().strip())
            except ValueError:
                messagebox.showerror("Lỗi", "Thời gian hoãn phải là một số thực hợp lệ!", parent=dialog)
                return

            if not u_id and entry_u.var.get().strip() in self.state.mg.stations: u_id = entry_u.var.get().strip()
            if not v_id and entry_v.var.get().strip() in self.state.mg.stations: v_id = entry_v.var.get().strip()

            if u_id in self.state.mg.stations and v_id in self.state.mg.stations and line and mins >= 0:
                sc.delays[(u_id, v_id, line)] = mins
                self.state.manager.save()
                self._load_scenario_details()
                self.state.notify_scenario_change()
                dialog.destroy()
            else:
                messagebox.showerror("Lỗi", "Thông tin nhập vào sai hoặc thời gian âm. Hãy thử lại!", parent=dialog)

        btn_frame = tk.Frame(dialog, bg=metro_ui.CLR_PANEL)
        btn_frame.pack(fill="x", side="bottom", pady=15, padx=35)
        tk.Button(btn_frame, text="Xác nhận", bg=metro_ui.CLR_ACCENT, fg="white", relief="flat", font=("Arial", 10, "bold"),
                  command=confirm, width=12, cursor="hand2").pack(side="right", padx=5)
        tk.Button(btn_frame, text="Hủy", bg=metro_ui.CLR_ACCENT2, fg=metro_ui.CLR_TEXT, relief="flat", font=("Arial", 10),
                  command=dialog.destroy, width=12, cursor="hand2").pack(side="right")

    def _delete_delay(self):
        idx = self.box_delays.curselection()
        if not idx or not self._selected_scenario_name: return
        sc = self.state.manager.get_scenario(self._selected_scenario_name)
        keys = list(sc.delays.keys())
        if idx[0] < len(keys):
            sc.delays.pop(keys[idx[0]])
            self.state.manager.save()
            self._load_scenario_details()
            self.state.notify_scenario_change()

