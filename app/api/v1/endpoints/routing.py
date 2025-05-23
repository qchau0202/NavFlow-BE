from fastapi import APIRouter, HTTPException
from app.schemas.routing import RouteRequest, RouteResponse
from app.services.routing_service import AStarRouter
from app.models.graph import Graph

router = APIRouter()

# --- Camera data ---
camera_locations = [
    {"id": 1, "coordinates": (10.783443, 106.690751)},
    {"id": 2, "coordinates": (10.782874, 106.691395)},
    {"id": 3, "coordinates": (10.784525, 106.688563)},
    {"id": 4, "coordinates": (10.786325, 106.687634)},
    {"id": 5, "coordinates": (10.772756, 106.679051)},
    {"id": 6, "coordinates": (10.768534, 106.683877)},
    {"id": 7, "coordinates": (10.769036, 106.683242)},
    {"id": 8, "coordinates": (10.766276, 106.678793)},
    {"id": 9, "coordinates": (10.76645, 106.68261)},
    {"id": 10, "coordinates": (10.774237, 106.688036)},
    {"id": 11, "coordinates": (10.77499, 106.686646)},
    {"id": 12, "coordinates": (10.776624, 106.683696)},
    {"id": 13, "coordinates": (10.777825, 106.682012)},
    {"id": 14, "coordinates": (10.77996, 106.68721)},
    {"id": 15, "coordinates": (10.777925, 106.689661)},
]

import math

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

astar = AStarRouter()

@router.post("/route", response_model=RouteResponse)
def get_routes(req: RouteRequest):
    k_paths = astar.k_shortest_paths(g, req.start_id, req.end_id, req.num_paths)
    if not k_paths:
        raise HTTPException(status_code=404, detail="No path found")
    paths = [p for p, c in k_paths]
    costs = [c for p, c in k_paths]
    return RouteResponse(paths=paths, costs=costs) 