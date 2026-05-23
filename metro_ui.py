from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from Admin import ScenarioManager
from MetroGraph import MetroGraph

# Import các thuật toán từ package algorithms

# ─────────────────────────────────────────────
#  CẤU HÌNH THEME & MÀU SẮC (LIGHT THEME NEW)
# ─────────────────────────────────────────────
DATA_FILE      = "brussels_metro_dataset (1).json"
ADMIN_PASSWORD = "admin123"
TRANSFER_PENALTY = 4.0

CLR_BG         = "#f4f6f9"  # Nền xám sáng nhẹ tinh tế
CLR_PANEL      = "#ffffff"  # Panel trắng tinh khiết
CLR_ACCENT     = "#007aff"  # Xanh công nghệ hiện đại (iOS Style)
CLR_ACCENT2    = "#e9ecef"  # Nền widget nhập liệu xám nhạt
CLR_TEXT       = "#1c1c1e"  # Chữ đen xám đậm dễ đọc
CLR_SUBTEXT    = "#6c757d"  # Chữ phụ màu xám vừa
CLR_SUCCESS    = "#28a745"  # Xanh lá thành công
CLR_WARN       = "#fd7e14"  # Cam cảnh báo
CLR_DANGER     = "#dc3545"  # Đỏ nguy hiểm
CLR_CARD       = "#f8f9fa"  # Nền hộp kết quả trắng xám nhẹ

# Màu sắc mặc định cho các tuyến đường nền hệ thống
LINE_COLORS = {
    "1": "#f5d300", "2": "#f57521",
    "5": "#f5d300", "6": "#f57521", "*": "#555555"
}

# MÀU ĐƯỜNG ĐỊNH TUYẾN KẾT QUẢ (Thay đổi sang màu Đỏ Neon cực kỳ nổi bật)
CLR_ROUTING_PATH = "#ff2d55"


def center_window(window, width: int, height: int):
    """Căn một cửa sổ (Tk hoặc Toplevel) ra chính giữa màn hình máy tính"""
    window.update_idletasks()
    # Lấy kích thước màn hình máy tính
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Tính toán tọa độ X, Y để đặt cửa sổ vào trung tâm
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Thiết lập kích thước và vị trí (định dạng: "RộngxCao+X+Y")
    window.geometry(f"{width}x{height}+{x}+{y}")

class AppState:
    def __init__(self, mg: MetroGraph, manager: ScenarioManager):
        self.mg = mg
        self.manager = manager
        self.on_scenario_change_callbacks = []

    def notify_scenario_change(self):
        for cb in self.on_scenario_change_callbacks:
            cb()

    def register_scenario_change(self, cb):
        self.on_scenario_change_callbacks.append(cb)

# ─────────────────────────────────────────────
#  AUTOCOMPLETE ENTRY WIDGET
# ─────────────────────────────────────────────
class AutocompleteEntry(tk.Frame):
    def __init__(self, parent, suggestions, placeholder="Nhập tên ga...", **kwargs):
        super().__init__(parent, bg=CLR_PANEL)
        self.suggestions = suggestions
        self.selected_id = None
        self.var = tk.StringVar()

        self.entry = tk.Entry(self, textvariable=self.var, bg=CLR_ACCENT2, fg=CLR_TEXT,
                              insertbackground=CLR_TEXT, relief="flat", bd=0,
                              font=("Segoe UI", 11), **kwargs)
        self.entry.pack(fill="x", ipady=8, ipadx=6)
        self._placeholder = placeholder

        # KHỞI TẠO FRAME TRƯỚC KHI GỌI PLACEHOLDER
        self.listbox_frame = tk.Frame(parent, bg=CLR_ACCENT2, bd=1, relief="solid")
        self.listbox = tk.Listbox(self.listbox_frame, bg=CLR_PANEL, fg=CLR_TEXT,
                                  selectbackground=CLR_ACCENT, relief="flat", bd=0, font=("Segoe UI", 10))
        self.listbox.pack(fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        self._matches = []

        # XỬ LÝ PLACEHOLDER VÀ TRACE SAU CÙNG
        self._show_placeholder()
        self.var.trace_add("write", self._on_type)

        self.entry.bind("<FocusIn>", self._hide_placeholder)
        self.entry.bind("<FocusOut>", self._restore_placeholder)

    def _show_placeholder(self):
        if not self.var.get(): self.entry.config(fg=CLR_SUBTEXT); self.var.set(self._placeholder)

    def _hide_placeholder(self, _=None):
        if self.var.get() == self._placeholder: self.var.set(""); self.entry.config(fg=CLR_TEXT)

    def _restore_placeholder(self, _=None):
        if not self.var.get(): self._show_placeholder()
        self.listbox_frame.place_forget()

    def _on_type(self, *_):
        text = self.var.get().strip().lower()
        if text == self._placeholder.lower() or not text:
            self.listbox_frame.place_forget();
            return
        self._matches = [(sid, name) for sid, name in self.suggestions if text in name.lower()][:8]
        if self._matches:
            self.listbox.delete(0, tk.END)
            for _, name in self._matches: self.listbox.insert(tk.END, f"  {name}")
            x = self.winfo_rootx() - self.winfo_toplevel().winfo_rootx()
            y = self.winfo_rooty() - self.winfo_toplevel().winfo_rooty() + self.winfo_height()
            self.listbox_frame.place(x=x, y=y, width=self.winfo_width());
            self.listbox_frame.lift()
        else:
            self.listbox_frame.place_forget()

    def _on_select(self, _=None):
        sel = self.listbox.curselection()
        if sel:
            idx = sel[0];
            sid, name = self._matches[idx]
            self.selected_id = sid;
            self.var.set(name);
            self.listbox_frame.place_forget()

    def get_selected(self):
        return self.selected_id, self.var.get()

    def clear(self):
        self.selected_id = None; self.var.set(""); self._show_placeholder()

# ─────────────────────────────────────────────
#  MAIN WINDOW CONFIGURATION
# ─────────────────────────────────────────────
from components.user_panel import UserScreen
from components.admin_panel import AdminScreen
class MetroApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Brussels Metro Pathfinder & Infrastructure Management")
        center_window(self, 1200, 750)
        self.configure(bg=CLR_BG)
        self.verify_Admin = False

        # Cấu hình Style đồng bộ theo Light Theme
        style = ttk.Style()
        style.theme_use('default')
        style.configure(".", background=CLR_BG, foreground=CLR_TEXT)
        style.configure("TCombobox", fieldbackground=CLR_ACCENT2, background=CLR_PANEL, foreground=CLR_TEXT)
        style.configure("TNotebook", background=CLR_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=CLR_PANEL, foreground=CLR_SUBTEXT, padding=[15, 5], font=("Arial", 10))
        style.map("TNotebook.Tab", background=[("selected", CLR_ACCENT2)], foreground=[("selected", CLR_ACCENT)])

        # Khởi tạo dữ liệu nền tảng
        self.mg = MetroGraph(transfer_penalty=TRANSFER_PENALTY)
        self.mg.load_from_json(DATA_FILE)
        self.manager = ScenarioManager()
        self.state = AppState(self.mg, self.manager)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.user_screen = UserScreen(self.notebook, self.state)
        self.admin_screen = AdminScreen(self.notebook, self.state)

        self.notebook.add(self.user_screen, text=" 🗺 Bản Đồ Tìm Đường ")
        self.notebook.add(self.admin_screen, text=" 🛠 Quản Trị Hệ Thống (Admin) ")

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event):
        if self.notebook.index("current") == 1:
            if self.verify_Admin == False:
                pwd = simpledialog.askstring("Xác thực hệ thống", "Nhập mã bảo mật Admin để tiếp tục:", show="*")
                if pwd != ADMIN_PASSWORD :
                    messagebox.showerror("Từ chối", "Mã bảo mật không chính xác!")
                    self.notebook.select(0)
                else:
                    self.admin_screen._refresh_scenario_list()
                    self.verify_Admin = True
            else:
                self.admin_screen._refresh_scenario_list()
