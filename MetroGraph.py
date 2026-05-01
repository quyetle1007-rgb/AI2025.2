import json
import heapq
from typing import List, Dict, Optional, Tuple, Set
from scipy.spatial import KDTree
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

class Station:
    def __init__(self, station_id: str, name: str, lat: float, lon: float, lines: List[str] = None):
        self.id = station_id
        self.name = name
        self.lat = float(lat)
        self.lon = float(lon)
        self.lines = lines or []

    def to_dict(self) -> dict:
        return self.__dict__

class Edge:
    def __init__(self, u: str, v: str, travel_time: float, line_name: str):
        self.u = u
        self.v = v
        self.travel_time = float(travel_time)
        self.line_name = line_name

    def to_dict(self) -> dict:
        return self.__dict__

class MetroGraph:
    def __init__(self, transfer_penalty: float = 4.0):
        self.stations: Dict[str, Station] = {}
        self.adj_list: Dict[str, List[Edge]] = {}
        self.transfer_penalty = transfer_penalty # Thời gian phạt khi đổi tuyến
        self._kd_tree: Optional[KDTree] = None
        self._node_ids: List[str] = []

    def add_station(self, s_id: str, name: str, lat: float, lon: float, lines: List[str] = None):
        station = Station(s_id, name, lat, lon, lines)
        self.stations[s_id] = station
        if s_id not in self.adj_list:
            self.adj_list[s_id] = []
        self._kd_tree = None
        return station

    def add_edge(self, u: str, v: str, travel_time: float, line_name: str, bidirectional: bool = True):
        if u in self.stations and v in self.stations:
            self.adj_list[u].append(Edge(u, v, travel_time, line_name))
            if bidirectional:
                self.adj_list[v].append(Edge(v, u, travel_time, line_name))
        else:
            print(f"[!] Warning: Cạnh {u}->{v} bỏ qua vì thiếu dữ liệu ga.")

    # --- Dijkstra update(add Transfer Penalty) ---
    def find_shortest_path(self, start_id: str, end_id: str) -> Dict:
        """
        Trả về: {path, total_time_min, stations_count, transfers}
        State = (station_id, line) để phân biệt cùng ga đi bằng line khác nhau.
        """
        if start_id not in self.stations or end_id not in self.stations:
            return {"error": "Ga không tồn tại"}

        # pq: (total_time, station_id, current_line)
        pq = [(0.0, start_id, None)]
        # distances[(station_id, line)] = best time to reach this state
        distances = {(start_id, None): 0.0}
        # previous[(station_id, line)] = (prev_station_id, prev_line)
        previous = {}
        visited = set()

        while pq:
            curr_time, u, curr_line = heapq.heappop(pq)

            state = (u, curr_line)
            if state in visited:
                continue
            visited.add(state)

            if u == end_id:
                # Tìm state tại đích có thời gian nhỏ nhất
                best_state = min(
                    [s for s in visited if s[0] == end_id],
                    key=lambda s: distances.get(s, float('inf'))
                )
                return self._reconstruct_path(previous, start_id, best_state, distances[best_state])

            for edge in self.adj_list.get(u, []):
                next_state = (edge.v, edge.line_name)
                if next_state in visited:
                    continue

                weight = edge.travel_time
                if curr_line is not None and edge.line_name != curr_line:
                    weight += self.transfer_penalty

                new_time = curr_time + weight

                if new_time < distances.get(next_state, float('inf')):
                    distances[next_state] = new_time
                    previous[next_state] = state
                    heapq.heappush(pq, (new_time, edge.v, edge.line_name))

        return {"error": "Không tìm thấy đường đi"}

    def _reconstruct_path(self, previous, start_id, final_state, total_time):
        """
        Trace ngược từ final_state về start bằng previous map.
        Loại bỏ ga trùng liên tiếp (cùng ga, đổi line tại chỗ).
        """
        states = []
        curr = final_state
        while curr is not None:
            states.append(curr)
            curr = previous.get(curr)
        states.reverse()

        # Lấy station_id + line đến ga đó, loại bỏ ga trùng liên tiếp
        path = []        # [station_id]
        path_lines = []  # line dùng để ĐI VÀO ga[i] (None ở ga đầu)
        transfers = 0
        prev_sid = None
        prev_line = None

        for i, (sid, line) in enumerate(states):
            if sid == prev_sid:
                # Cùng ga, khác line = đổi tuyến tại chỗ, cập nhật line vào ga này
                path_lines[-1] = line
                if prev_line and line and line != prev_line:
                    transfers += 1
            else:
                path.append(sid)
                path_lines.append(line)  # line dùng để đến ga này
                if prev_line and line and line != prev_line:
                    transfers += 1
            prev_sid = sid
            prev_line = line

        return {
            "path": path,
            "path_lines": path_lines,  # path_lines[i] = line đi vào ga path[i]
            "total_time_min": round(total_time, 2),
            "stations_count": len(path),
            "transfers": transfers,
        }

    # utilites related to ID
    def find_nearest_stations(self, lat: float, lon: float, k: int = 3) -> List[Dict]:
        if not self.stations: return []
        
        if not self._kd_tree:
            self._node_ids = list(self.stations.keys())
            coords = [[self.stations[s].lat, self.stations[s].lon] for s in self._node_ids]
            self._kd_tree = KDTree(coords)

        dist, idxs = self._kd_tree.query([lat, lon], k=min(k, len(self._node_ids)))
        if k == 1: idxs = [idxs]

        results = []
        for i in idxs:
            sid = self._node_ids[i]
            s = self.stations[sid]
            real_dist = geodesic((lat, lon), (s.lat, s.lon)).meters
            results.append({"id": sid, "name": s.name, "dist_m": round(real_dist, 1)})
        return sorted(results, key=lambda x: x['dist_m'])

    def is_connected(self) -> bool:
        if not self.stations: return True
        start = list(self.stations.keys())[0]
        visited = {start}
        stack = [start]
        while stack:
            u = stack.pop()
            for edge in self.adj_list.get(u, []):
                if edge.v not in visited:
                    visited.add(edge.v)
                    stack.append(edge.v)
        return len(visited) == len(self.stations)

    # --- I/O ---
    def load_from_json(self, filename: str):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.stations = {}
                self.adj_list = {}
                
                # transition name to id
                name_to_id = {s['name']: s['id'] for s in data['stations']}
                
                for s in data['stations']:
                    self.add_station(s['id'], s['name'], s['lat'], s['lon'], s['lines'])
                
                for e in data['edges']:
                    # transition name to id
                    u_id = name_to_id.get(e['from'], e['from'])
                    v_id = name_to_id.get(e['to'], e['to'])
                    self.add_edge(u_id, v_id, e['travel_time_min'], e['line'], bidirectional=False)
            print(f"[*] Loaded {len(self.stations)} stations from {filename}")
        except Exception as e:
            print(f"[!] Error loading JSON: {e}")
    def debug_print(self):
        
        print("\n" + "="*50)
        print("DEBUG: DANH SACH KE HE THONG METRO")
        print("="*50)
        for u_id, edges in self.adj_list.items():
            u_name = self.stations[u_id].name
            print(f"[{u_name}] ({u_id}):")
            for e in edges:
                # Kiểm tra xem ga đích có trong danh sách stations không để tránh crash
                v_name = self.stations[e.v].name if e.v in self.stations else "Unknown"
                print(f"  --> KET NOI TOI: {v_name} ({e.v}) | ThOI GIAN: {e.travel_time}p | TUYEN: {e.line_name}")
        print("="*50 + "\n")
