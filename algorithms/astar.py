import heapq
import math
from typing import Dict


def haversine_heuristic(graph, current_id: str, end_id: str) -> float:
    """
    Ước tính thời gian từ ga hiện tại đến ga đích bằng khoảng cách đường chim bay (Haversine).
    Giả định vận tốc trung bình tàu điện ngầm là 30 km/h.
    """
    s1 = graph.stations[current_id]
    s2 = graph.stations[end_id]

    lat1, lon1 = math.radians(s1.lat), math.radians(s1.lon)
    lat2, lon2 = math.radians(s2.lat), math.radians(s2.lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371.0  # Bán kính Trái Đất theo km
    dist_km = c * r

    # Thời gian (phút) = (Quãng đường / Vận tốc) * 60
    return (dist_km / 30.0) * 60.0


def find_path_astar(graph, start_id: str, end_id: str) -> Dict:
    """
    Tìm đường đi bằng A* = Chi phí thực tế (g) + Ước lượng thời gian (h).
    """
    if start_id not in graph.stations or end_id not in graph.stations:
        return {"error": "Ga không tồn tại"}

    h_start = haversine_heuristic(graph, start_id, end_id)
    # pq: (f_score, g_score, station_id, current_line)
    pq = [(h_start, 0.0, start_id, None)]

    distances = {(start_id, None): 0.0}  # Lưu g_score tốt nhất
    previous = {}
    visited = set()

    while pq:
        f_score, g_score, u, curr_line = heapq.heappop(pq)

        state = (u, curr_line)
        if state in visited:
            continue
        visited.add(state)

        if u == end_id:
            best_state = min(
                [s for s in visited if s[0] == end_id],
                key=lambda s: distances.get(s, float('inf'))
            )
            return graph._reconstruct_path(previous, start_id, best_state, distances[best_state])

        for edge in graph.adj_list.get(u, []):
            next_state = (edge.v, edge.line_name)
            if next_state in visited:
                continue

            weight = edge.travel_time
            if curr_line is not None and edge.line_name != curr_line:
                weight += graph.transfer_penalty

            new_g = g_score + weight

            if new_g < distances.get(next_state, float('inf')):
                distances[next_state] = new_g
                previous[next_state] = state

                h_score = haversine_heuristic(graph, edge.v, end_id)
                new_f = new_g + h_score

                heapq.heappush(pq, (new_f, new_g, edge.v, edge.line_name))

    return {"error": "Không tìm thấy đường đi"}