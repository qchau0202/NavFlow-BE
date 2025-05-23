from typing import Dict, List, Tuple, Optional

class Node:
    def __init__(self, node_id: str, coord: Tuple[float, float]):
        self.id: str = node_id
        self.coord: Tuple[float, float] = coord
        self.edges: List['Edge'] = []

    def __repr__(self):
        return f"Node({self.id}, {self.coord})"

class Edge:
    def __init__(self, from_node: 'Node', to_node: 'Node', weight: float):
        self.from_node: Node = from_node
        self.to_node: Node = to_node
        self.weight: float = weight

    def __repr__(self):
        return f"Edge({self.from_node.id} -> {self.to_node.id}, {self.weight})"

class Graph:
    def __init__(self, directed: bool = True):
        self.nodes: Dict[str, Node] = {}
        self.directed: bool = directed

    def add_node(self, node_id: str, coord: Tuple[float, float]):
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(node_id, coord)

    def add_edge(self, from_id: str, to_id: str, weight: float):
        if from_id not in self.nodes or to_id not in self.nodes:
            raise ValueError("Both nodes must exist before adding an edge.")
        from_node = self.nodes[from_id]
        to_node = self.nodes[to_id]
        edge = Edge(from_node, to_node, weight)
        from_node.edges.append(edge)
        if not self.directed:
            # Add the reverse edge for undirected graphs
            reverse_edge = Edge(to_node, from_node, weight)
            to_node.edges.append(reverse_edge)

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)

    def __repr__(self):
        return f"Graph(nodes={list(self.nodes.keys())}, directed={self.directed})"