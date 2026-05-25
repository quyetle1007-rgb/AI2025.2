import heapq
import math


def heuristic(station_a, station_b):
    """
    Tính hàm heuristic h(n) bằng khoảng cách đường chim bay (Euclidean)
    giữa hai ga dựa vào tọa độ địa lý kinh độ (lon) và vĩ độ (lat).
    """
    return math.sqrt((station_a.lat - station_b.lat) ** 2 + (station_a.lon - station_b.lon) ** 2)


def find_path_greedy(graph, start_id, end_id):
    """
    Thuật toán Greedy Best-First Search (Tìm kiếm lựa chọn tối ưu tham lam).
    Chỉ sử dụng giá trị Heuristic h(n) để mở rộng các nút gần đích nhất.
    """
    if start_id not in graph.stations or end_id not in graph.stations:
        return {"error": "Ga xuất phát hoặc ga đích không tồn tại!"}

    if start_id == end_id:
        return {
            "path": [start_id],
            "path_lines": [None],
            "total_time_min": 0,
            "transfers": 0
        }

    goal_station = graph.stations[end_id]

    # Hàng đợi ưu tiên lưu các cặp: (h_value, current_node)
    start_station = graph.stations[start_id]
    pq = [(heuristic(start_station, goal_station), start_id)]

    visited = set()

    # Từ điển lưu thông tin truy vết lộ trình và chi phí thực tế
    parent = {start_id: None}
    edge_info = {start_id: (0, None)}  # Lưu dạng: (thời_gian_thực_tế, tên_tuyến)

    found = False
    while pq:
        _, current = heapq.heappop(pq)

        if current == end_id:
            found = True
            break

        if current in visited:
            continue
        visited.add(current)

        # TỰ ĐỘNG THÍCH ỨNG THEO CẤU TRÚC ĐỒ THỊ CỦA METROGRAPH
        neighbors = []
        if hasattr(graph, 'get_neighbors'):
            neighbors = graph.get_neighbors(current)
        elif hasattr(graph, 'graph') and current in graph.graph:
            neighbors = graph.graph[current]
        elif hasattr(graph, 'adj') and current in graph.adj:
            neighbors = graph.adj[current]

        for neighbor in neighbors:
            # Kiểm tra định dạng dữ liệu trả về của chặng kề để bóc tách thông tin
            if isinstance(neighbor, (tuple, list)):
                if len(neighbor) == 3:
                    # Định dạng phổ biến dạng (v, cost, line) hoặc (v, line, cost)
                    v, val1, val2 = neighbor[0], neighbor[1], neighbor[2]
                    if isinstance(val1, str):  # Nếu phần tử thứ 2 là chuỗi (tên tuyến)
                        line, cost = val1, val2
                    else:
                        cost, line = val1, val2
                elif len(neighbor) == 2:
                    v, cost = neighbor[0], neighbor[1]
                    line = "*"
                else:
                    continue
            else:
                v = neighbor
                cost = 1.0
                line = "*"

            # Trong Greedy BFS truyền thống, ta chỉ thêm vào hàng đợi nếu nút chưa từng được xét qua
            if v not in visited and v not in parent:
                parent[v] = current
                edge_info[v] = (cost, str(line))

                # Sắp xếp hàng đợi ưu tiên theo duy nhất hàm h(n)
                h_val = heuristic(graph.stations[v], goal_station)
                heapq.heappush(pq, (h_val, v))

    if not found:
        return {
            "error": f"Không tìm thấy lộ trình từ ga {graph.stations[start_id].name} đến {graph.stations[end_id].name}."}

    # TRUY VẾT ĐƯỜNG ĐI (RECONSTRUCT PATH) VÀ TÍNH TOÁN KẾT QUẢ HIỂN THỊ UI
    path = []
    path_lines = []
    total_time = 0

    curr = end_id
    while curr is not None:
        path.append(curr)
        cost, line = edge_info[curr]
        path_lines.append(line)
        total_time += cost
        curr = parent[curr]

    path.reverse()
    path_lines.reverse()

    # Đếm số lần chuyển tuyến thực tế
    transfers = 0
    prev_line = None
    for i in range(1, len(path_lines)):
        curr_line = path_lines[i]
        if prev_line is not None and curr_line != prev_line and curr_line != "*" and prev_line != "*":
            transfers += 1
        if curr_line != "*":
            prev_line = curr_line

    return {
        "path": path,
        "path_lines": path_lines,
        "total_time_min": round(total_time, 1),
        "transfers": transfers
    }