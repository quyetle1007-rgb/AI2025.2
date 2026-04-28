import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from MetroGraph import MetroGraph, Station, Edge
 
 
@dataclass
class Scenario:
    name: str
    description: str
    active: bool = False
    closed_stations: List[str] = field(default_factory=list)
    closed_edges: List[Tuple[str, str]] = field(default_factory=list)
    delays: Dict[Tuple[str, str], float] = field(default_factory=dict)
 
 
class ScenarioManager:
    SAVE_PATH = Path("scenarios.json")
 
    def __init__(self):
        self.scenarios: Dict[str, Scenario] = {}
        self.load()
 
 
    def create_scenario(self, name: str, description: str) -> Scenario:
        if name in self.scenarios:
            raise ValueError(f"Tình huống '{name}' đã tồn tại.")
        sc = Scenario(name=name, description=description)
        self.scenarios[name] = sc
        self.save()
        return sc
 
    def get_scenario(self, name: str) -> Optional[Scenario]:
        return self.scenarios.get(name)
 
    def update_scenario(self, name: str, description: str = None, active: bool = None) -> Scenario:
        sc = self._get_or_raise(name)
        if description is not None:
            sc.description = description
        if active is not None:
            sc.active = active
        self.save()
        return sc
 
    def delete_scenario(self, name: str) -> None:
        self._get_or_raise(name)
        del self.scenarios[name]
        self.save()
 
    def delete_scenarios(self, names: List[str]) -> List[str]:
        deleted = []
        for name in names:
            if name in self.scenarios:
                del self.scenarios[name]
                deleted.append(name)
        if deleted:
            self.save()
        return deleted
 
    def delete_all_scenarios(self) -> int:
        count = len(self.scenarios)
        self.scenarios.clear()
        self.save()
        return count
 
    def delete_inactive_scenarios(self) -> List[str]:
        to_delete = [name for name, sc in self.scenarios.items() if not sc.active]
        for name in to_delete:
            del self.scenarios[name]
        if to_delete:
            self.save()
        return to_delete
 
    def list_scenarios(self) -> List[Scenario]:
        return list(self.scenarios.values())
 
    # Đóng/ mở ga
 
    def close_station(self, scenario_name: str, station_id: str) -> Scenario:
        sc = self._get_or_raise(scenario_name)
        if station_id not in sc.closed_stations:
            sc.closed_stations.append(station_id)
            self.save()
        return sc
 
    def reopen_station(self, scenario_name: str, station_id: str) -> Scenario:
        sc = self._get_or_raise(scenario_name)
        if station_id in sc.closed_stations:
            sc.closed_stations.remove(station_id)
            self.save()
        return sc
 
    # Đóng/mở đường
 
    def close_edge(self, scenario_name: str, u: str, v: str) -> Scenario:
        sc = self._get_or_raise(scenario_name)
        if (u, v) not in sc.closed_edges:
            sc.closed_edges.append((u, v))
            self.save()
        return sc
 
    def reopen_edge(self, scenario_name: str, u: str, v: str) -> Scenario:
        sc = self._get_or_raise(scenario_name)
        for e in ((u, v), (v, u)):
            if e in sc.closed_edges:
                sc.closed_edges.remove(e)
        self.save()
        return sc
 
    #Delay
 
    def add_delay(self, scenario_name: str, u: str, v: str, extra_minutes: float) -> Scenario:
        if extra_minutes < 0:
            raise ValueError("Thời gian trì hoãn không được âm.")
        sc = self._get_or_raise(scenario_name)
        key = tuple(sorted([u, v]))
        sc.delays[key] = extra_minutes
        self.save()
        return sc
 
    def remove_delay(self, scenario_name: str, u: str, v: str) -> Scenario:
        sc = self._get_or_raise(scenario_name)
        key = tuple(sorted([u, v]))
        sc.delays.pop(key, None)
        self.save()
        return sc
 
    # kh/huy scenario
 
    def activate(self, scenario_name: str) -> Scenario:
        sc = self._get_or_raise(scenario_name)
        sc.active = True
        self.save()
        return sc
 
    def deactivate(self, scenario_name: str) -> Scenario:
        sc = self._get_or_raise(scenario_name)
        sc.active = False
        self.save()
        return sc
 
    # save/load json
 
    def save(self) -> None:
        data = {}
        for name, sc in self.scenarios.items():
            data[name] = {
                "name": sc.name,
                "description": sc.description,
                "active": sc.active,
                "closed_stations": sc.closed_stations,
                "closed_edges": [list(e) for e in sc.closed_edges],
                "delays": {json.dumps(list(k)): v for k, v in sc.delays.items()},
            }
        self.SAVE_PATH.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
 
    def load(self) -> None:
        if not self.SAVE_PATH.exists():
            return
        text = self.SAVE_PATH.read_text(encoding="utf-8").strip()
        if not text:
            return
        data = json.loads(text)
        for name, entry in data.items():
            raw_edges = entry.get("closed_edges") or []
            self.scenarios[name] = Scenario(
                name=entry["name"],
                description=entry["description"],
                active=entry["active"],
                closed_stations=entry["closed_stations"],
                closed_edges=[tuple(e) for e in raw_edges],
                delays={tuple(sorted(json.loads(k))): v for k, v in entry["delays"].items()},
            )
 
 
    def _copy_metrograph(self, base_mg: MetroGraph) -> MetroGraph:
        """Tạo deep copy MetroGraph mà không dùng thư viện ngoài."""
        mg = MetroGraph(transfer_penalty=base_mg.transfer_penalty)
 
        for sid, s in base_mg.stations.items():
            mg.stations[sid] = Station(s.id, s.name, s.lat, s.lon, list(s.lines))
 
        for sid, edges in base_mg.adj_list.items():
            mg.adj_list[sid] = [
                Edge(e.u, e.v, e.travel_time, e.line_name) for e in edges
            ]
 
        return mg
 
    def _apply_scenario(self, sc: Scenario, mg: MetroGraph) -> None:
        """Áp một scenario lên MetroGraph mg IN-PLACE."""
 
        # 1. Đóng ga
        for sid in sc.closed_stations:
            if sid in mg.stations:
                del mg.stations[sid]
                del mg.adj_list[sid]
                # xóa cạnh từ các ga khác trỏ vào sid
                for u in list(mg.adj_list):
                    mg.adj_list[u] = [e for e in mg.adj_list[u] if e.v != sid]
 
        # 2. Đóng đường 
        for (u, v) in sc.closed_edges:
            if u in mg.adj_list:
                mg.adj_list[u] = [e for e in mg.adj_list[u] if e.v != v]
            if v in mg.adj_list:
                mg.adj_list[v] = [e for e in mg.adj_list[v] if e.v != u]
 
        #3. Delay
        for (u, v), extra in sc.delays.items():
            for src, dst in [(u, v), (v, u)]:
                if src in mg.adj_list:
                    for edge in mg.adj_list[src]:
                        if edge.v == dst:
                            edge.travel_time += extra
 
    def get_modified_graph(self, base_mg: MetroGraph) -> MetroGraph:
        """
        Trả về bản sao MetroGraph đã áp tất cả scenario đang active.
        base_mg gốc KHÔNG bị thay đổi.
        """
        modified = self._copy_metrograph(base_mg)
        for sc in self.scenarios.values():
            if sc.active:
                self._apply_scenario(sc, modified)
        return modified
 
    #API
 
    def find_path(self, base_mg: MetroGraph, start_id: str, end_id: str) -> Dict:
        """
        Tìm đường ngắn nhất sau khi áp tất cả scenario đang active.
        Trả về dict: { path, total_time_min, stations_count } hoặc { error }
        """
        modified = self.get_modified_graph(base_mg)
        return modified.find_shortest_path(start_id, end_id)
 
    def _get_or_raise(self, name: str) -> Scenario:
        sc = self.scenarios.get(name)
        if sc is None:
            raise ValueError(f"Tình huống '{name}' không tồn tại.")
        return sc
