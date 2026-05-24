import heapq
from typing import Dict

def find_path_dijkstra(graph, start_id: str, end_id: str) -> Dict:
    if start_id not in graph.stations or end_id not in graph.stations:
        return {"error": "Ga không tồn tại"}

    
    heap = [(0.0, start_id, None)]
    
    
    visited = set()
    
    previous = {}
    distances = {(start_id, None): 0.0}
    found_state = None

    while heap:
        curr_time, u, curr_line = heapq.heappop(heap)
        current_state = (u, curr_line)

        if current_state in visited:
            continue
        visited.add(current_state)

        
        if u == end_id:
            found_state = current_state
            break

        
        for edge in graph.adj_list.get(u, []):
            next_state = (edge.v, edge.line_name)
            
            if next_state in visited:
                continue

            
            weight = edge.travel_time
           
            if curr_line is not None and edge.line_name != curr_line:
                weight += graph.transfer_penalty

            new_time = curr_time + weight

            if next_state not in distances or new_time < distances[next_state]:
                distances[next_state] = new_time
                previous[next_state] = current_state
                heapq.heappush(heap, (new_time, edge.v, edge.line_name))

    if found_state:
        
        return graph._reconstruct_path(previous, start_id, found_state, distances[found_state])

    return {"error": "Không tìm thấy đường đi"}