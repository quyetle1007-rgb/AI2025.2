from MetroGraph import MetroGraph

g = MetroGraph(transfer_penalty=4.0)

g.load_from_json("brussels_metro_dataset (1).json")
#printf for debug
g.debug_print()

# BFS
print(f"Connected: {g.is_connected()}")

#ajdj_lít
adj = g.adj_list
print("\n--- Adjacency List (Partial) ---")

for i, (node, edges) in enumerate(adj.items()):
    if i > 5: break 
    print(f"Node {node} has {len(edges)} connections.")


print("\n--- Test Shortest Path ---")
route = g.find_shortest_path("gare_de_louest", "stockel")
if "path" in route:
    print(f"Time: {route['total_time_min']} mins")
    print(f"Path: {' -> '.join(route['path'])}")