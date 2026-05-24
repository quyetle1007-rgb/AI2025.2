"""
components/map_view.py — Phần Visualize bản đồ Metro Brussels (Sơn)

Dùng tkintermapview để hiển thị bản đồ thực OpenStreetMap, vẽ tuyến tàu
theo màu thực tế, marker cho ga, highlight lộ trình sau khi tìm đường.

Public API:
    visualizer = MetroMapVisualizer(parent_frame, metro_graph, line_colors, line_station_order)
    visualizer.draw_network(filter_line=None)
    visualizer.highlight_route(path, path_lines)
    visualizer.clear_highlight()
    visualizer.mark_closed_stations(closed_ids)
    visualizer.reset_view()
"""

from __future__ import annotations

import json
import tkinter as tk
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw
from tkintermapview import TkinterMapView
from MetroGraph import MetroGraph


# ── Hằng số ──────────────────────────────────────────────────────────────────

BRUSSELS_CENTER_LAT = 50.8503
BRUSSELS_CENTER_LON = 4.3517
DEFAULT_ZOOM = 12

# Màu mặc định theo tuyến (dự phòng nếu JSON thiếu)
FALLBACK_LINE_COLORS: Dict[str, str] = {
    "1": "#B95192",
    "2": "#F78E1E",
    "5": "#FCB814",
    "6": "#0080B3",
}

# Tên hiển thị cho tuyến
LINE_DISPLAY_NAMES: Dict[str, str] = {
    "1": "Line 1",
    "2": "Line 2",
    "5": "Line 5",
    "6": "Line 6",
}

# Cấu hình hiển thị
LINE_WIDTH = 4                      # Độ dày vẽ tuyến bình thường
HIGHLIGHT_WIDTH = 7                 # Độ dày highlight lộ trình
HIGHLIGHT_BORDER_COLOR = "#FFFFFF"  # Viền trắng cho highlight

# Kích thước icon ga (pixel)
STATION_DOT_RADIUS = 6             # Bán kính chấm tròn ga thường
INTERCHANGE_DOT_RADIUS = 9         # Bán kính chấm tròn ga interchange
INTERCHANGE_BORDER = 3             # Viền đen cho interchange

START_MARKER_COLOR = "#2ecc71"     # Xanh lá cho ga xuất phát
END_MARKER_COLOR = "#e74c3c"       # Đỏ cho ga đích
CLOSED_MARKER_COLOR = "#888888"    # Xám cho ga đóng


# ── Tạo icon tròn nhỏ ────────────────────────────────────────────────────────

def _create_dot_icon(
    radius: int,
    fill_color: str,
    border_color: str = "",
    border_width: int = 0,
) -> tk.PhotoImage:
    """Tạo icon hình tròn nhỏ bằng PIL, trả về PhotoImage."""
    size = (radius * 2 + border_width * 2 + 2,) * 2
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size[0] // 2, size[1] // 2

    # Vẽ viền ngoài
    if border_color and border_width > 0:
        draw.ellipse(
            [cx - radius - border_width, cy - radius - border_width,
             cx + radius + border_width, cy + radius + border_width],
            fill=border_color,
        )

    # Vẽ hình tròn trong
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=fill_color,
    )

    # Chuyển sang PhotoImage (Tkinter)
    from PIL import ImageTk
    return ImageTk.PhotoImage(img)


class MetroMapVisualizer:
    """
    Widget bản đồ metro Brussels sử dụng tkintermapview.

    Marker ga là chấm tròn nhỏ (không text). Tên ga hiện khi click.
    Hỗ trợ lọc theo tuyến (filter_line).
    """

    def __init__(
        self,
        parent: tk.Widget,
        metro_graph: MetroGraph,
        line_colors: Optional[Dict[str, str]] = None,
        line_station_order: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        self.mg = metro_graph
        self.line_colors = line_colors or dict(FALLBACK_LINE_COLORS)
        self.line_station_order = line_station_order or {}

        # Tạo bản đồ
        self.map_widget = TkinterMapView(parent, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)
        self.map_widget.set_position(BRUSSELS_CENTER_LAT, BRUSSELS_CENTER_LON)
        self.map_widget.set_zoom(DEFAULT_ZOOM)

        # Lưu trữ các đối tượng vẽ
        self._line_paths: List = []
        self._station_markers: Dict[str, object] = {}
        self._highlight_paths: List = []
        self._highlight_markers: List = []
        self._closed_markers: List = []

        # Giữ reference đến PhotoImage để GC không xóa
        self._icon_refs: List = []

        # Tooltip hiện tại
        self._active_tooltip_marker = None

        # Lookup name -> id
        self._name_to_id: Dict[str, str] = {}
        for sid, station in self.mg.stations.items():
            self._name_to_id[station.name] = sid

    # ── PUBLIC API ────────────────────────────────────────────────────────

    def draw_network(self, filter_line: Optional[str] = None) -> None:
        """
        Vẽ toàn bộ mạng lưới: tuyến (polyline) + ga (chấm tròn).

        Parameters
        ----------
        filter_line : str | None
            Nếu chỉ định (ví dụ "1", "2", "5", "6"), chỉ vẽ ga và tuyến
            thuộc line đó. None = vẽ tất cả.
        """
        self._clear_network()
        self._draw_lines(filter_line)
        self._draw_stations(filter_line)

    def highlight_route(
        self,
        path: List[str],
        path_lines: List[Optional[str]],
    ) -> None:
        """
        Highlight lộ trình trên bản đồ.

        Parameters
        ----------
        path : list[str]
            Danh sách station_id theo thứ tự đi.
        path_lines : list[str | None]
            Tuyến đi vào mỗi ga (path_lines[i] = line khi đến path[i]).
        """
        self._clear_highlight_objects()

        if len(path) < 2:
            return

        # ── Vẽ polyline highlight, tách theo segment cùng tuyến ──
        segments = self._split_path_by_line(path, path_lines)

        for line_id, segment_ids in segments:
            coords = []
            for sid in segment_ids:
                if sid in self.mg.stations:
                    s = self.mg.stations[sid]
                    coords.append((s.lat, s.lon))

            if len(coords) >= 2:
                seg_color = self.line_colors.get(line_id, "#FFFFFF")

                # Viền trắng (border)
                border = self.map_widget.set_path(
                    coords, color=HIGHLIGHT_BORDER_COLOR,
                    width=HIGHLIGHT_WIDTH + 4,
                )
                self._highlight_paths.append(border)

                # Đường highlight màu tuyến
                hl = self.map_widget.set_path(
                    coords, color=seg_color, width=HIGHLIGHT_WIDTH,
                )
                self._highlight_paths.append(hl)

        # ── Marker ga xuất phát & đích ──
        start_id = path[0]
        end_id = path[-1]

        if start_id in self.mg.stations:
            s = self.mg.stations[start_id]
            m = self.map_widget.set_marker(
                s.lat, s.lon,
                text=f"▶ {s.name}",
                marker_color_circle=START_MARKER_COLOR,
                marker_color_outside="#1a8a4a",
                text_color="#1a8a4a",
            )
            self._highlight_markers.append(m)

        if end_id in self.mg.stations:
            s = self.mg.stations[end_id]
            m = self.map_widget.set_marker(
                s.lat, s.lon,
                text=f"◆ {s.name}",
                marker_color_circle=END_MARKER_COLOR,
                marker_color_outside="#a0302a",
                text_color="#a0302a",
            )
            self._highlight_markers.append(m)

        # ── Hiện tên ga trung gian trên lộ trình (interchange only) ──
        for i, sid in enumerate(path):
            if sid == start_id or sid == end_id:
                continue
            if sid in self.mg.stations:
                station = self.mg.stations[sid]
                # Chỉ hiện marker tên cho ga đổi tuyến trên lộ trình
                prev_line = path_lines[i - 1] if i > 0 and i - 1 < len(path_lines) else None
                cur_line = path_lines[i] if i < len(path_lines) else None
                is_transfer = (prev_line and cur_line and prev_line != cur_line)
                if is_transfer:
                    m = self.map_widget.set_marker(
                        station.lat, station.lon,
                        text=f"⇄ {station.name}",
                        marker_color_circle="#FFFFFF",
                        marker_color_outside="#333333",
                        text_color="#0055aa",
                    )
                    self._highlight_markers.append(m)

        # ── Zoom vào lộ trình ──
        self._fit_route(path)

    def clear_highlight(self) -> None:
        """Xóa highlight lộ trình, giữ lại mạng lưới gốc."""
        self._clear_highlight_objects()

    def mark_closed_stations(self, closed_ids: List[str]) -> None:
        """Đánh dấu các ga đang đóng (do scenario) bằng marker xám."""
        for m in self._closed_markers:
            m.delete()
        self._closed_markers.clear()

        for sid in closed_ids:
            if sid in self.mg.stations:
                s = self.mg.stations[sid]
                m = self.map_widget.set_marker(
                    s.lat, s.lon,
                    text=f"✕ {s.name}",
                    marker_color_circle=CLOSED_MARKER_COLOR,
                    marker_color_outside="#555555",
                    text_color="#cc0000",
                )
                self._closed_markers.append(m)

    def reset_view(self) -> None:
        """Reset view về trung tâm Brussels, zoom mặc định."""
        self.map_widget.set_position(BRUSSELS_CENTER_LAT, BRUSSELS_CENTER_LON)
        self.map_widget.set_zoom(DEFAULT_ZOOM)

    # ── PRIVATE HELPERS ───────────────────────────────────────────────────

    def _clear_network(self) -> None:
        """Xóa toàn bộ đối tượng mạng lưới (line paths + station markers) để vẽ lại."""
        for p in self._line_paths:
            p.delete()
        self._line_paths.clear()

        for m in self._station_markers.values():
            m.delete()
        self._station_markers.clear()

        self._icon_refs.clear()

        # Xóa tooltip nếu đang hiện
        if self._active_tooltip_marker is not None:
            try:
                self._active_tooltip_marker.delete()
            except Exception:
                pass
            self._active_tooltip_marker = None

    def _draw_lines(self, filter_line: Optional[str] = None) -> None:
        """Vẽ polyline cho từng tuyến theo thứ tự ga và màu thực."""
        for line_id, station_names in self.line_station_order.items():
            if filter_line and line_id != filter_line:
                continue

            color = self.line_colors.get(line_id, "#999999")
            coords = []
            for name in station_names:
                sid = self._name_to_id.get(name)
                if sid and sid in self.mg.stations:
                    s = self.mg.stations[sid]
                    coords.append((s.lat, s.lon))

            if len(coords) >= 2:
                path_obj = self.map_widget.set_path(
                    coords, color=color, width=LINE_WIDTH,
                )
                self._line_paths.append(path_obj)

    def _draw_stations(self, filter_line: Optional[str] = None) -> None:
        """
        Vẽ marker chấm tròn nhỏ cho từng ga.
        - Ga thường: chấm nhỏ, màu tuyến
        - Ga interchange: chấm lớn hơn, trắng viền đen
        - Tên ga hiện khi click (thông qua marker command callback)
        """
        for sid, station in self.mg.stations.items():
            if filter_line and filter_line not in station.lines:
                continue

            is_interchange = len(station.lines) > 1

            if is_interchange:
                icon = _create_dot_icon(
                    INTERCHANGE_DOT_RADIUS, "#FFFFFF", "#222222",
                    INTERCHANGE_BORDER,
                )
            else:
                line_id = station.lines[0] if station.lines else "1"
                color = self.line_colors.get(line_id, "#3a3a3a")
                icon = _create_dot_icon(
                    STATION_DOT_RADIUS, color, "#FFFFFF", 2,
                )

            self._icon_refs.append(icon)  # giữ reference

            # Tạo callback click hiện tên ga
            def _on_click(marker, _sid=sid):
                self._show_station_tooltip(_sid)

            m = self.map_widget.set_marker(
                station.lat, station.lon,
                text="",  # KHÔNG hiện text mặc định
                icon=icon,
                command=_on_click,
            )
            self._station_markers[sid] = m

    def _show_station_tooltip(self, sid: str) -> None:
        """Khi click vào chấm ga: hiện / ẩn tên ga (toggle marker text)."""
        # Xóa tooltip trước đó nếu có
        if self._active_tooltip_marker is not None:
            try:
                self._active_tooltip_marker.delete()
            except Exception:
                pass
            self._active_tooltip_marker = None

        if sid not in self.mg.stations:
            return

        station = self.mg.stations[sid]
        lines_str = ", ".join(
            LINE_DISPLAY_NAMES.get(l, f"L{l}") for l in station.lines
        )
        label = f"{station.name}\n({lines_str})"

        # Tạo marker text tạm tại vị trí ga
        tooltip = self.map_widget.set_marker(
            station.lat, station.lon,
            text=label,
            marker_color_circle="#FFFFFF",
            marker_color_outside="#333333",
            text_color="#111111",
        )
        self._active_tooltip_marker = tooltip

    def _split_path_by_line(
        self, path: List[str], path_lines: List[Optional[str]],
    ) -> List[Tuple[str, List[str]]]:
        """
        Tách path thành các segment cùng tuyến.
        Mỗi segment gối đầu 1 ga với segment trước (polyline liền mạch).
        """
        if not path:
            return []

        segments: List[Tuple[str, List[str]]] = []
        current_line = path_lines[0] if path_lines else None
        current_segment = [path[0]]

        for i in range(1, len(path)):
            line = path_lines[i] if i < len(path_lines) else current_line

            if line != current_line and current_line is not None:
                segments.append((current_line, list(current_segment)))
                current_segment = [path[i - 1]]  # gối đầu
                current_line = line

            current_segment.append(path[i])

        if current_segment:
            segments.append((current_line or "1", list(current_segment)))

        return segments

    def _fit_route(self, path: List[str]) -> None:
        """Zoom bản đồ vừa khớp với lộ trình."""
        lats, lons = [], []
        for sid in path:
            if sid in self.mg.stations:
                s = self.mg.stations[sid]
                lats.append(s.lat)
                lons.append(s.lon)

        if lats and lons:
            padding = 0.005
            try:
                self.map_widget.fit_bounding_box(
                    (max(lats) + padding, min(lons) - padding),
                    (min(lats) - padding, max(lons) + padding),
                )
            except Exception:
                center_lat = (max(lats) + min(lats)) / 2
                center_lon = (max(lons) + min(lons)) / 2
                self.map_widget.set_position(center_lat, center_lon)
                self.map_widget.set_zoom(13)

    def _clear_highlight_objects(self) -> None:
        """Xóa tất cả polyline và marker highlight."""
        for p in self._highlight_paths:
            p.delete()
        self._highlight_paths.clear()

        for m in self._highlight_markers:
            m.delete()
        self._highlight_markers.clear()

        # Xóa tooltip nếu đang hiện
        if self._active_tooltip_marker is not None:
            try:
                self._active_tooltip_marker.delete()
            except Exception:
                pass
            self._active_tooltip_marker = None


# ── Hàm tiện ích ─────────────────────────────────────────────────────────────

def load_line_info_from_json(
    json_path: str,
) -> tuple[Dict[str, str], Dict[str, List[str]]]:
    """
    Đọc file JSON dataset, trả về:
      - line_colors:        {"1": "#B95192", "2": "#F78E1E", ...}
      - line_station_order: {"1": ["Gare de l'Ouest", "Beekkant", ...], ...}
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    line_colors: Dict[str, str] = {}
    line_station_order: Dict[str, List[str]] = {}

    for line_id, line_info in data.get("lines", {}).items():
        line_colors[line_id] = line_info.get("color_hex", "#999999")
        line_station_order[line_id] = line_info.get("stations", [])

    return line_colors, line_station_order
