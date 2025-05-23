import heapq
from typing import List, Tuple, Optional, Dict
from app.models.graph import Graph, Node
import math

class AStarRouter:
    @staticmethod
    def haversine(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        # Calculate the great-circle distance between two points
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        R = 6371  # Earth radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def find_path(self, graph: Graph, start_id: str, end_id: str) -> Optional[Tuple[List[str], float]]:
        if start_id not in graph.nodes or end_id not in graph.nodes:
            return None
        open_set = []
        heapq.heappush(open_set, (0, start_id))
        came_from: Dict[str, Optional[str]] = {start_id: None}
        g_score: Dict[str, float] = {node_id: float('inf') for node_id in graph.nodes}
        g_score[start_id] = 0
        f_score: Dict[str, float] = {node_id: float('inf') for node_id in graph.nodes}
        f_score[start_id] = self.haversine(graph.nodes[start_id].coord, graph.nodes[end_id].coord)

        while open_set:
            current_f, current_id = heapq.heappop(open_set)
            if current_id == end_id:
                # Reconstruct path
                path = []
                while current_id:
                    path.append(current_id)
                    current_id = came_from[current_id]
                path.reverse()
                return path, g_score[end_id]
            current_node = graph.nodes[current_id]
            for edge in current_node.edges:
                neighbor = edge.to_node.id
                tentative_g = g_score[current_id] + edge.weight
                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current_id
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.haversine(graph.nodes[neighbor].coord, graph.nodes[end_id].coord)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None  # No path found

    def k_shortest_paths(self, graph: Graph, start_id: str, end_id: str, k: int) -> List[Tuple[List[str], float]]:
        # Yen's algorithm for k-shortest loopless paths
        if start_id not in graph.nodes or end_id not in graph.nodes:
            return []
        paths = []
        costs = []
        # First shortest path
        result = self.find_path(graph, start_id, end_id)
        if not result:
            return []
        path, cost = result
        paths.append(path)
        costs.append(cost)
        candidates = []
        for ki in range(1, k):
            for i in range(len(paths[-1]) - 1):
                spur_node = paths[-1][i]
                root_path = paths[-1][:i+1]
                removed_edges = []
                # Remove the edges that would create the same root_path
                for p in paths:
                    if len(p) > i and p[:i+1] == root_path:
                        from_id = p[i]
                        to_id = p[i+1]
                        from_node = graph.nodes[from_id]
                        # Remove edge from from_node to to_node
                        for edge in from_node.edges:
                            if edge.to_node.id == to_id:
                                removed_edges.append((from_node, edge))
                                from_node.edges.remove(edge)
                                break
                # Find spur path
                spur_result = self.find_path(graph, spur_node, end_id)
                if spur_result:
                    spur_path, spur_cost = spur_result
                    # Combine root and spur path
                    total_path = root_path[:-1] + spur_path
                    if total_path not in paths and not any(c[0] == total_path for c in candidates):
                        total_cost = 0
                        for j in range(len(total_path) - 1):
                            from_id = total_path[j]
                            to_id = total_path[j+1]
                            for edge in graph.nodes[from_id].edges:
                                if edge.to_node.id == to_id:
                                    total_cost += edge.weight
                                    break
                        candidates.append((total_path, total_cost))
                # Restore removed edges
                for from_node, edge in removed_edges:
                    from_node.edges.append(edge)
            if not candidates:
                break
            # Sort candidates by cost
            candidates.sort(key=lambda x: x[1])
            next_path, next_cost = candidates.pop(0)
            paths.append(next_path)
            costs.append(next_cost)
        return list(zip(paths, costs)) 