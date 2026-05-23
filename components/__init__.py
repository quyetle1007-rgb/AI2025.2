# # ─────────────────────────────────────────────
# #  PANEL ADMIN: QUẢN LÝ SỰ CỐ HỆ THỐNG (LAYOUT NÂNG CẤP)
# # ─────────────────────────────────────────────
# class AdminScreen(tk.Frame):
#     def __init__(self, parent, state: AppState):
#         super().__init__(parent, bg=CLR_BG)
#         self.state = state
#         self._selected_scenario_name: Optional[str] = None
#         self._build_ui()
#
#     def _build_ui(self):
#         # Thiết lập tỷ lệ hiển thị 2 panel: Trái (1) - Phải (3)
#         self.columnconfigure(0, weight=1, minsize=380)
#         self.columnconfigure(1, weight=3, minsize=600)
#         self.rowconfigure(0, weight=1)
#
#         # ─────────────────────────────────────────────
#         #  PANEL TRÁI: QUẢN LÝ & TÌM KIẾM SCENARIOS
#         # ─────────────────────────────────────────────
#         left_panel = tk.Frame(self, bg=CLR_PANEL, bd=0)
#         left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
#
#         tk.Label(left_panel, text="DANH SÁCH SỰ CỐ SYSTEM", bg=CLR_PANEL, fg=CLR_ACCENT,
#                  font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
#
#         # --- THANH TÌM KIẾM SCENARIO ---
#         search_frame = tk.Frame(left_panel, bg=CLR_PANEL)
#         search_frame.pack(fill="x", padx=15, pady=(0, 10))
#         tk.Label(search_frame, text="🔍 Tìm:", bg=CLR_PANEL, fg=CLR_SUBTEXT, font=("Arial", 10, "bold")).pack(
#             side="left", padx=(0, 5))
#
#         self.scen_search_var = tk.StringVar()
#         self.scen_search_var.trace_add("write", lambda *args: self._refresh_scenario_list())
#         self.scen_search_entry = tk.Entry(search_frame, textvariable=self.scen_search_var, bg=CLR_ACCENT2, fg=CLR_TEXT,
#                                           relief="flat", font=("Arial", 10))
#         self.scen_search_entry.pack(side="left", fill="x", expand=True, ipady=5, ipadx=5)
#
#         # --- LISTBOX HIỂN THỊ SCENARIOS ---
#         self.scen_listbox = tk.Listbox(left_panel, bg=CLR_CARD, fg=CLR_TEXT, selectbackground=CLR_ACCENT, relief="flat",
#                                        bd=0, font=("Arial", 11))
#         self.scen_listbox.pack(fill="both", expand=True, padx=15, pady=5)
#         self.scen_listbox.bind("<<ListboxSelect>>", self._on_scenario_select)
#
#         # --- THANH DIỀU KHIỂN CRUD SCENARIO ---
#         btn_frame = tk.Frame(left_panel, bg=CLR_PANEL)
#         btn_frame.pack(fill="x", padx=15, pady=15)
#
#         tk.Button(btn_frame, text="Thêm", bg=CLR_ACCENT, fg="white", relief="flat", font=("Arial", 9, "bold"), width=8,
#                   command=self._add_scenario, cursor="hand2").pack(side="left", padx=2, ipady=4)
#         tk.Button(btn_frame, text="Xóa", bg=CLR_DANGER, fg="white", relief="flat", font=("Arial", 9, "bold"), width=8,
#                   command=self._delete_scenario, cursor="hand2").pack(side="left", padx=2, ipady=4)
#         tk.Button(btn_frame, text="Bật", bg=CLR_SUCCESS, fg="white", relief="flat", font=("Arial", 9, "bold"), width=8,
#                   command=lambda: self._toggle_scenario(True), cursor="hand2").pack(side="left", padx=2, ipady=4)
#         tk.Button(btn_frame, text="Tắt", bg=CLR_SUBTEXT, fg="white", relief="flat", font=("Arial", 9, "bold"), width=8,
#                   command=lambda: self._toggle_scenario(False), cursor="hand2").pack(side="left", padx=2, ipady=4)
#
#         # ─────────────────────────────────────────────
#         #  PANEL PHẢI: CHI TIẾT VÀ QUẢN LÝ HÀNH ĐỘNG
#         # ─────────────────────────────────────────────
#         self.right_panel = tk.Frame(self, bg=CLR_BG)
#         self.right_panel.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
#
#         self.no_select_label = tk.Label(self.right_panel,
#                                         text="Vui lòng chọn hoặc thêm một Sự cố (Scenario) từ danh sách bên trái.",
#                                         bg=CLR_BG, fg=CLR_SUBTEXT, font=("Arial", 11, "italic"))
#         self.no_select_label.pack(expand=True)
#
#         self.details_frame = tk.Frame(self.right_panel, bg=CLR_BG)
#
#         self.scen_title = tk.Label(self.details_frame, text="Chi tiết Sự cố:", bg=CLR_BG, fg=CLR_TEXT,
#                                    font=("Arial", 14, "bold"))
#         self.scen_title.pack(anchor="w", pady=(0, 10))
#
#         tables_frame = tk.Frame(self.details_frame, bg=CLR_BG)
#         tables_frame.pack(fill="both", expand=True)
#         tables_frame.columnconfigure(0, weight=1)
#         tables_frame.columnconfigure(1, weight=1)
#         tables_frame.columnconfigure(2, weight=1)
#         tables_frame.rowconfigure(0, weight=1)
#
#         # --- Bảng 1: Ga Đóng Cửa ---
#         f_station = tk.LabelFrame(tables_frame, text="1. Ga Đóng Cửa", bg=CLR_PANEL, fg=CLR_ACCENT,
#                                   font=("Arial", 10, "bold"), padx=10, pady=10)
#         f_station.grid(row=0, column=0, sticky="nsew", padx=5)
#         self.box_stations = tk.Listbox(f_station, bg=CLR_CARD, fg=CLR_TEXT, bd=0, relief="flat",
#                                        selectbackground=CLR_ACCENT)
#         self.box_stations.pack(fill="both", expand=True, pady=5)
#         tk.Button(f_station, text="+ Thêm Ga Đóng", bg=CLR_ACCENT2, fg=CLR_TEXT, relief="flat",
#                   command=self._add_closed_station, cursor="hand2").pack(fill="x", side="bottom", pady=2, ipady=3)
#         tk.Button(f_station, text="- Xóa Chọn", bg=CLR_ACCENT2, fg=CLR_DANGER, relief="flat",
#                   command=self._delete_closed_station, cursor="hand2").pack(fill="x", side="bottom", ipady=3)
#
#         # --- Bảng 2: Chặng Bị Đóng ---
#         f_edge = tk.LabelFrame(tables_frame, text="2. Chặng Đứt Gãy", bg=CLR_PANEL, fg=CLR_ACCENT,
#                                font=("Arial", 10, "bold"), padx=10, pady=10)
#         f_edge.grid(row=0, column=1, sticky="nsew", padx=5)
#         self.box_edges = tk.Listbox(f_edge, bg=CLR_CARD, fg=CLR_TEXT, bd=0, relief="flat", selectbackground=CLR_ACCENT)
#         self.box_edges.pack(fill="both", expand=True, pady=5)
#         tk.Button(f_edge, text="+ Thêm Chặng", bg=CLR_ACCENT2, fg=CLR_TEXT, relief="flat",
#                   command=self._add_closed_edge, cursor="hand2").pack(fill="x", side="bottom", pady=2, ipady=3)
#         tk.Button(f_edge, text="- Xóa Chọn", bg=CLR_ACCENT2, fg=CLR_DANGER, relief="flat",
#                   command=self._delete_closed_edge, cursor="hand2").pack(fill="x", side="bottom", ipady=3)
#
#         # --- Bảng 3: Chặng Bị Trì Hoãn ---
#         f_delay = tk.LabelFrame(tables_frame, text="3. Chặng Trì Hoãn (Delay)", bg=CLR_PANEL, fg=CLR_ACCENT,
#                                 font=("Arial", 10, "bold"), padx=10, pady=10)
#         f_delay.grid(row=0, column=2, sticky="nsew", padx=5)
#         self.box_delays = tk.Listbox(f_delay, bg=CLR_CARD, fg=CLR_TEXT, bd=0, relief="flat",
#                                      selectbackground=CLR_ACCENT)
#         self.box_delays.pack(fill="both", expand=True, pady=5)
#         tk.Button(f_delay, text="+ Thêm Delay", bg=CLR_ACCENT2, fg=CLR_TEXT, relief="flat", command=self._add_delay,
#                   cursor="hand2").pack(fill="x", side="bottom", pady=2, ipady=3)
#         tk.Button(f_delay, text="- Xóa Chọn", bg=CLR_ACCENT2, fg=CLR_DANGER, relief="flat", command=self._delete_delay,
#                   cursor="hand2").pack(fill="x", side="bottom", ipady=3)
#
#         self._refresh_scenario_list()
#
#     def _refresh_scenario_list(self):
#         self.scen_listbox.delete(0, tk.END)
#         search_query = self.scen_search_var.get().strip().lower()
#
#         for sc in self.state.manager.list_scenarios():
#             # Thực hiện bộ lọc tìm kiếm theo ký tự nhập vào
#             if search_query and search_query not in sc.name.lower():
#                 continue
#             status = "[ON]" if sc.active else "[OFF]"
#             self.scen_listbox.insert(tk.END, f" {status} {sc.name}")
#         self._load_scenario_details()
#
#     def _on_scenario_select(self, _=None):
#         idx = self.scen_listbox.curselection()
#         if idx:
#             full_str = self.scen_listbox.get(idx[0])
#             self._selected_scenario_name = full_str.split(" ", 2)[-1]
#             self.no_select_label.pack_forget()
#             self.details_frame.pack(fill="both", expand=True)
#             self._load_scenario_details()
#
#     def _load_scenario_details(self):
#         self.box_stations.delete(0, tk.END)
#         self.box_edges.delete(0, tk.END)
#         self.box_delays.delete(0, tk.END)
#
#         if not self._selected_scenario_name:
#             self.details_frame.pack_forget()
#             self.no_select_label.pack(expand=True)
#             return
#
#         sc = self.state.manager.get_scenario(self._selected_scenario_name)
#         if not sc: return
#
#         status_text = "Đang hoạt động" if sc.active else "Đang tắt"
#         self.scen_title.config(text=f"Sự cố: {sc.name} ({status_text})")
#
#         for s_id in sc.closed_stations:
#             name = self.state.mg.stations[s_id].name if s_id in self.state.mg.stations else s_id
#             self.box_stations.insert(tk.END, f"{name} ({s_id})")
#
#         for (u, v, line) in sc.closed_edges:
#             un = self.state.mg.stations[u].name if u in self.state.mg.stations else u
#             vn = self.state.mg.stations[v].name if v in self.state.mg.stations else v
#             self.box_edges.insert(tk.END, f"{un} ⇄ {vn} [L: {line}]")
#
#         for (u, v, line), value in sc.delays.items():
#             un = self.state.mg.stations[u].name if u in self.state.mg.stations else u
#             vn = self.state.mg.stations[v].name if v in self.state.mg.stations else v
#             self.box_delays.insert(tk.END, f"{un} ⇄ {vn} (+{value}m) [L: {line}]")
#
#     def _add_scenario(self):
#         name = simpledialog.askstring("Thêm Sự Cố", "Nhập tên sự cố hệ thống mới:")
#         if name:
#             try:
#                 self.state.manager.create_scenario(name, "Mô tả sự cố hệ thống")
#                 self._selected_scenario_name = name
#                 self._refresh_scenario_list()
#                 self.state.notify_scenario_change()
#             except ValueError as e:
#                 messagebox.showerror("Lỗi", str(e))
#
#     def _delete_scenario(self):
#         if not self._selected_scenario_name: return
#         if messagebox.askyesno("Xác nhận",
#                                f"Bạn có chắc chắn muốn xóa hoàn toàn sự cố '{self._selected_scenario_name}'?"):
#             if hasattr(self.state.manager, 'delete_scenario'):
#                 self.state.manager.delete_scenario(self._selected_scenario_name)
#             else:
#                 self.state.manager.scenarios.pop(self._selected_scenario_name, None)
#                 self.state.manager.save()
#             self._selected_scenario_name = None
#             self._refresh_scenario_list()
#             self.state.notify_scenario_change()
#
#     def _toggle_scenario(self, status: bool):
#         if not self._selected_scenario_name: return
#         sc = self.state.manager.get_scenario(self._selected_scenario_name)
#         if sc:
#             sc.active = status
#             self.state.manager.save()
#             self._refresh_scenario_list()
#             self.state.notify_scenario_change()
#
#     # ─────────────────────────────────────────────
#     #  CÁC THỦ TỤC THÊM HÀNH ĐỘNG CÓ AUTOCOMPLETE
#     # ─────────────────────────────────────────────
#     def _get_station_suggestions(self):
#         return [(sid, s.name) for sid, s in sorted(self.state.mg.stations.items(), key=lambda x: x[1].name)]
#
#     def _add_closed_station(self):
#         if not self._selected_scenario_name: return
#         sc = self.state.manager.get_scenario(self._selected_scenario_name)
#
#         # Tạo cửa sổ Pop-up độc lập để nhập liệu nâng cao
#         dialog = tk.Toplevel(self)
#         dialog.title("Đóng Cửa Ga")
#         center_window(dialog, 420, 220)
#         dialog.configure(bg=CLR_PANEL)
#         dialog.transient(self)
#         dialog.grab_set()
#
#         tk.Label(dialog, text="CHỌN GA CẦN ĐÓNG CỬA", bg=CLR_PANEL, fg=CLR_ACCENT, font=("Arial", 11, "bold")).pack(
#             pady=(20, 10))
#
#         # Tái sử dụng widget Autocomplete gợi ý thông minh
#         entry_station = AutocompleteEntry(dialog, self._get_station_suggestions(),
#                                           placeholder="Gõ tên hoặc ID ga để tìm kiếm...")
#         entry_station.pack(fill="x", padx=35, pady=10)
#
#         def confirm():
#             sid, _ = entry_station.get_selected()
#             # Fallback nếu người dùng gõ tay chính xác ID mà không click chuột chọn
#             if not sid:
#                 typed = entry_station.var.get().strip()
#                 if typed in self.state.mg.stations: sid = typed
#
#             if sid and sid in self.state.mg.stations:
#                 if sid not in sc.closed_stations:
#                     sc.closed_stations.append(sid)
#                     self.state.manager.save()
#                     self._load_scenario_details()
#                     self.state.notify_scenario_change()
#                 dialog.destroy()
#             else:
#                 messagebox.showerror("Lỗi", "Vui lòng chọn một nhà ga hợp lệ từ danh sách gợi ý!", parent=dialog)
#
#         btn_frame = tk.Frame(dialog, bg=CLR_PANEL)
#         btn_frame.pack(fill="x", side="bottom", pady=20, padx=35)
#         tk.Button(btn_frame, text="Xác nhận", bg=CLR_ACCENT, fg="white", relief="flat", font=("Arial", 10, "bold"),
#                   command=confirm, width=12, cursor="hand2").pack(side="right", padx=5)
#         tk.Button(btn_frame, text="Hủy", bg=CLR_ACCENT2, fg=CLR_TEXT, relief="flat", font=("Arial", 10),
#                   command=dialog.destroy, width=12, cursor="hand2").pack(side="right")
#
#     def _delete_closed_station(self):
#         idx = self.box_stations.curselection()
#         if not idx or not self._selected_scenario_name: return
#         sc = self.state.manager.get_scenario(self._selected_scenario_name)
#         val = self.box_stations.get(idx[0])
#         sid = val.split('(')[-1].replace(')', '')
#         if sid in sc.closed_stations:
#             sc.closed_stations.remove(sid)
#             self.state.manager.save()
#             self._load_scenario_details()
#             self.state.notify_scenario_change()
#
#     def _add_closed_edge(self):
#         if not self._selected_scenario_name: return
#         sc = self.state.manager.get_scenario(self._selected_scenario_name)
#
#         dialog = tk.Toplevel(self)
#         dialog.title("Đóng Chặng Đường")
#         center_window(dialog, 450, 380)
#         dialog.configure(bg=CLR_PANEL)
#         dialog.transient(self)
#         dialog.grab_set()
#
#         tk.Label(dialog, text="THÊM CHẶNG ĐỨT GÃY", bg=CLR_PANEL, fg=CLR_ACCENT, font=("Arial", 11, "bold")).pack(
#             pady=(15, 10))
#
#         suggestions = self._get_station_suggestions()
#
#         tk.Label(dialog, text="Ga bắt đầu (Station U):", bg=CLR_PANEL, fg=CLR_SUBTEXT, font=("Arial", 9, "bold")).pack(
#             anchor="w", padx=35)
#         entry_u = AutocompleteEntry(dialog, suggestions, placeholder="Tìm ga bắt đầu...")
#         entry_u.pack(fill="x", padx=35, pady=(2, 10))
#
#         tk.Label(dialog, text="Ga kết thúc (Station V):", bg=CLR_PANEL, fg=CLR_SUBTEXT, font=("Arial", 9, "bold")).pack(
#             anchor="w", padx=35)
#         entry_v = AutocompleteEntry(dialog, suggestions, placeholder="Tìm ga kết thúc...")
#         entry_v.pack(fill="x", padx=35, pady=(2, 10))
#
#         tk.Label(dialog, text="Tuyến đường (Nhập tên tuyến hoặc * cho tất cả):", bg=CLR_PANEL, fg=CLR_SUBTEXT,
#                  font=("Arial", 9, "bold")).pack(anchor="w", padx=35)
#         line_var = tk.StringVar(value="*")
#         entry_line = tk.Entry(dialog, textvariable=line_var, bg=CLR_ACCENT2, fg=CLR_TEXT, relief="flat",
#                               font=("Segoe UI", 11))
#         entry_line.pack(fill="x", padx=35, pady=(2, 15), ipady=5)
#
#         def confirm():
#             u_id, _ = entry_u.get_selected()
#             v_id, _ = entry_v.get_selected()
#             line = line_var.get().strip()
#
#             if not u_id and entry_u.var.get().strip() in self.state.mg.stations: u_id = entry_u.var.get().strip()
#             if not v_id and entry_v.var.get().strip() in self.state.mg.stations: v_id = entry_v.var.get().strip()
#
#             if u_id in self.state.mg.stations and v_id in self.state.mg.stations and line:
#                 sc.closed_edges.append((u_id, v_id, line))
#                 self.state.manager.save()
#                 self._load_scenario_details()
#                 self.state.notify_scenario_change()
#                 dialog.destroy()
#             else:
#                 messagebox.showerror("Lỗi", "Thông tin ga không khớp hệ thống. Vui lòng sử dụng gợi ý!", parent=dialog)
#
#         btn_frame = tk.Frame(dialog, bg=CLR_PANEL)
#         btn_frame.pack(fill="x", side="bottom", pady=15, padx=35)
#         tk.Button(btn_frame, text="Xác nhận", bg=CLR_ACCENT, fg="white", relief="flat", font=("Arial", 10, "bold"),
#                   command=confirm, width=12, cursor="hand2").pack(side="right", padx=5)
#         tk.Button(btn_frame, text="Hủy", bg=CLR_ACCENT2, fg=CLR_TEXT, relief="flat", font=("Arial", 10),
#                   command=dialog.destroy, width=12, cursor="hand2").pack(side="right")
#
#     def _delete_closed_edge(self):
#         idx = self.box_edges.curselection()
#         if not idx or not self._selected_scenario_name: return
#         sc = self.state.manager.get_scenario(self._selected_scenario_name)
#         if idx[0] < len(sc.closed_edges):
#             sc.closed_edges.pop(idx[0])
#             self.state.manager.save()
#             self._load_scenario_details()
#             self.state.notify_scenario_change()
#
#     def _add_delay(self):
#         if not self._selected_scenario_name: return
#         sc = self.state.manager.get_scenario(self._selected_scenario_name)
#
#         dialog = tk.Toplevel(self)
#         dialog.title("Khai Báo Trì Hoãn (Delay)")
#         center_window(dialog, 450, 450)
#         dialog.configure(bg=CLR_PANEL)
#         dialog.transient(self)
#         dialog.grab_set()
#
#         tk.Label(dialog, text="THÊM CHẶNG TRÌ HOÃN (DELAY)", bg=CLR_PANEL, fg=CLR_ACCENT,
#                  font=("Arial", 11, "bold")).pack(pady=(15, 10))
#
#         suggestions = self._get_station_suggestions()
#
#         tk.Label(dialog, text="Ga bắt đầu (Station U):", bg=CLR_PANEL, fg=CLR_SUBTEXT, font=("Arial", 9, "bold")).pack(
#             anchor="w", padx=35)
#         entry_u = AutocompleteEntry(dialog, suggestions, placeholder="Tìm ga bắt đầu...")
#         entry_u.pack(fill="x", padx=35, pady=(2, 10))
#
#         tk.Label(dialog, text="Ga kết thúc (Station V):", bg=CLR_PANEL, fg=CLR_SUBTEXT, font=("Arial", 9, "bold")).pack(
#             anchor="w", padx=35)
#         entry_v = AutocompleteEntry(dialog, suggestions, placeholder="Tìm ga kết thúc...")
#         entry_v.pack(fill="x", padx=35, pady=(2, 10))
#
#         tk.Label(dialog, text="Tuyến đường (Nhập tên tuyến hoặc *):", bg=CLR_PANEL, fg=CLR_SUBTEXT,
#                  font=("Arial", 9, "bold")).pack(anchor="w", padx=35)
#         line_var = tk.StringVar(value="*")
#         entry_line = tk.Entry(dialog, textvariable=line_var, bg=CLR_ACCENT2, fg=CLR_TEXT, relief="flat",
#                               font=("Segoe UI", 11))
#         entry_line.pack(fill="x", padx=35, pady=(2, 10), ipady=5)
#
#         tk.Label(dialog, text="Thời gian hoãn thêm (Đơn vị: phút):", bg=CLR_PANEL, fg=CLR_SUBTEXT,
#                  font=("Arial", 9, "bold")).pack(anchor="w", padx=35)
#         mins_var = tk.StringVar()
#         entry_mins = tk.Entry(dialog, textvariable=mins_var, bg=CLR_ACCENT2, fg=CLR_TEXT, relief="flat",
#                               font=("Segoe UI", 11))
#         entry_mins.pack(fill="x", padx=35, pady=(2, 15), ipady=5)
#
#         def confirm():
#             u_id, _ = entry_u.get_selected()
#             v_id, _ = entry_v.get_selected()
#             line = line_var.get().strip()
#             try:
#                 mins = float(mins_var.get().strip())
#             except ValueError:
#                 messagebox.showerror("Lỗi", "Thời gian hoãn phải là một số thực hợp lệ!", parent=dialog)
#                 return
#
#             if not u_id and entry_u.var.get().strip() in self.state.mg.stations: u_id = entry_u.var.get().strip()
#             if not v_id and entry_v.var.get().strip() in self.state.mg.stations: v_id = entry_v.var.get().strip()
#
#             if u_id in self.state.mg.stations and v_id in self.state.mg.stations and line and mins >= 0:
#                 sc.delays[(u_id, v_id, line)] = mins
#                 self.state.manager.save()
#                 self._load_scenario_details()
#                 self.state.notify_scenario_change()
#                 dialog.destroy()
#             else:
#                 messagebox.showerror("Lỗi", "Thông tin nhập vào sai hoặc thời gian âm. Hãy thử lại!", parent=dialog)
#
#         btn_frame = tk.Frame(dialog, bg=CLR_PANEL)
#         btn_frame.pack(fill="x", side="bottom", pady=15, padx=35)
#         tk.Button(btn_frame, text="Xác nhận", bg=CLR_ACCENT, fg="white", relief="flat", font=("Arial", 10, "bold"),
#                   command=confirm, width=12, cursor="hand2").pack(side="right", padx=5)
#         tk.Button(btn_frame, text="Hủy", bg=CLR_ACCENT2, fg=CLR_TEXT, relief="flat", font=("Arial", 10),
#                   command=dialog.destroy, width=12, cursor="hand2").pack(side="right")
#
#     def _delete_delay(self):
#         idx = self.box_delays.curselection()
#         if not idx or not self._selected_scenario_name: return
#         sc = self.state.manager.get_scenario(self._selected_scenario_name)
#         keys = list(sc.delays.keys())
#         if idx[0] < len(keys):
#             sc.delays.pop(keys[idx[0]])
#             self.state.manager.save()
#             self._load_scenario_details()
#             self.state.notify_scenario_change()
