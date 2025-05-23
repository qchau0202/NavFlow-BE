from app.models.graph import Graph
from app.services.routing_service import AStarRouter
import math
import networkx as nx
import matplotlib.pyplot as plt

# --- Camera data ---
camera_locations = [
    {"id": 1, "name": "NKKN - DBP2", "coordinates": (10.783443, 106.690751)},
    {"id": 2, "name": "NKKN - DBP1", "coordinates": (10.782874, 106.691395)},
    {"id": 3, "name": "NKKN - Võ Thị Sáu", "coordinates": (10.784525, 106.688563)},
    {"id": 4, "name": "NKKN - Trần Quốc Toản", "coordinates": (10.786325, 106.687634)},
    {"id": 5, "name": "Điện Biên Phủ - Cao Thắng", "coordinates": (10.772756, 106.679051)},
    {"id": 6, "name": "Cao Thắng - Võ Văn Tần 1", "coordinates": (10.768534, 106.683877)},
    {"id": 7, "name": "Cao Thắng - Võ Văn Tần 2", "coordinates": (10.769036, 106.683242)},
    {"id": 8, "name": "Lý Thái Tổ - Nguyễn Đình Chiểu", "coordinates": (10.766276, 106.678793)},
    {"id": 9, "name": "Nguyễn Thị Minh Khai - Nguyễn Thiện Thuật", "coordinates": (10.76645, 106.68261)},
    {"id": 10, "name": "Cách Mạng Tháng Tám - Võ Văn Tần", "coordinates": (10.774237, 106.688036)},
    {"id": 11, "name": "Cách Mạng Tháng Tám - Nguyễn Đình Chiểu", "coordinates": (10.77499, 106.686646)},
    {"id": 12, "name": "Điện Biên Phủ - Cách Mạng Tháng Tám", "coordinates": (10.776624, 106.683696)},
    {"id": 13, "name": "Nút giao công trường dân chủ", "coordinates": (10.777825, 106.682012)},
    {"id": 14, "name": "Điện Biên Phủ - Trương Định", "coordinates": (10.77996, 106.68721)},
    {"id": 15, "name": "Nguyễn Đình Chiểu - Trương Định", "coordinates": (10.777925, 106.689661)},
]

def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- Build the graph ---
g = Graph(directed=False)
for cam in camera_locations:
    g.add_node(str(cam["id"]), cam["coordinates"])

# Connect each camera to its 2 nearest neighbors
for cam in camera_locations:
    distances = []
    for other in camera_locations:
        if cam["id"] != other["id"]:
            dist = haversine(cam["coordinates"], other["coordinates"])
            distances.append((dist, other["id"]))
    distances.sort()
    for _, neighbor_id in distances[:2]:
        g.add_edge(str(cam["id"]), str(neighbor_id), haversine(cam["coordinates"], camera_locations[neighbor_id-1]["coordinates"]))

# Build a mapping from id to name
id_to_name = {str(cam["id"]): cam["name"] for cam in camera_locations}

# --- Visualization ---
def draw_graph(graph, path=None):
    G = nx.Graph()
    pos = {}
    labels = {}
    for node_id, node in graph.nodes.items():
        G.add_node(node_id)
        pos[node_id] = (node.coord[1], node.coord[0])
        labels[node_id] = id_to_name[node_id]  # Use name as label
        for edge in node.edges:
            G.add_edge(edge.from_node.id, edge.to_node.id, weight=round(edge.weight, 2))
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw(G, pos, labels=labels, node_color='skyblue', node_size=700, font_size=8)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    if path:
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='r', width=2)
    plt.show()

# --- Test A* routing ---
if __name__ == '__main__':
    router = AStarRouter()
    path, cost = router.find_path(g, '1', '10')
    print(f"Path: {path}")
    print(f"Total cost: {cost}")
    draw_graph(g, path) 