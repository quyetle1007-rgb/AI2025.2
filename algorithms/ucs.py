import heapq
from typing import Dict

def find_path_ucs(graph, start_id: str, end_id: str) -> Dict:
    """
    Tìm đường đi ngắn nhất dựa trên thời gian di chuyển (travel_time) và thời gian phạt (transfer_penalty).
    """
    if start_id not in graph.stations or end_id not in graph.stations:
        return {"error": "Ga không tồn tại"}

    # pq: (total_time, station_id, current_line)
    pq = [(0.0, start_id, None)]
    distances = {(start_id, None): 0.0}
    previous = {}
    visited = set()

    while pq:
        curr_time, u, curr_line = heapq.heappop(pq)

        state = (u, curr_line)
        if state in visited:
            continue
        visited.add(state)

        if u == end_id:
            # Chọn state ở đích có tổng thời gian nhỏ nhất
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

            new_time = curr_time + weight

            if new_time < distances.get(next_state, float('inf')):
                distances[next_state] = new_time
                previous[next_state] = state
                heapq.heappush(pq, (new_time, edge.v, edge.line_name))

    return {"error": "Không tìm thấy đường đi"}