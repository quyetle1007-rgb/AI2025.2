from collections import deque
from typing import Dict


def find_path_bfs(graph, start_id: str, end_id: str) -> Dict:
    """
    Tìm đường đi ít chặng nhất trên đồ thị Metro (không xét thời gian phút thực tế).
    """
    if start_id not in graph.stations or end_id not in graph.stations:
        return {"error": "Ga không tồn tại"}

    # Hàng đợi chứa state: (station_id, current_line)
    queue = deque([(start_id, None)])
    visited = {(start_id, None)}
    previous = {}

    # distance vẫn được lưu để cộng dồn thời gian đi thực tế cho output
    distances = {(start_id, None): 0.0}
    found_state = None

    while queue:
        u, curr_line = queue.popleft()

        if u == end_id:
            found_state = (u, curr_line)
            break

        for edge in graph.adj_list.get(u, []):
            next_state = (edge.v, edge.line_name)

            if next_state not in visited:
                visited.add(next_state)
                previous[next_state] = (u, curr_line)

                # Tính chi phí thời gian thực tế để trả về kết quả (dù BFS không ưu tiên theo nó)
                weight = edge.travel_time
                if curr_line is not None and edge.line_name != curr_line:
                    weight += graph.transfer_penalty

                distances[next_state] = distances[(u, curr_line)] + weight
                queue.append(next_state)

    if found_state:
        # Gọi lại hàm trace đường từ MetroGraph
        return graph._reconstruct_path(previous, start_id, found_state, distances[found_state])

    return {"error": "Không tìm thấy đường đi"}