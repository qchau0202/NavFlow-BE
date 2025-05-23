from app.models.graph import Graph

def test_graph():
    g = Graph(directed=True)
    g.add_node('CAM1', (10.0, 20.0))
    g.add_node('CAM2', (10.1, 20.1))
    g.add_node('CAM3', (10.2, 20.2))
    g.add_edge('CAM1', 'CAM2', 5.0)
    g.add_edge('CAM2', 'CAM3', 3.0)
    assert 'CAM1' in g.nodes
    assert 'CAM2' in g.nodes
    assert len(g.nodes['CAM1'].edges) == 1
    assert g.nodes['CAM1'].edges[0].to_node.id == 'CAM2'
    print(g)
    print(g.nodes['CAM1'])
    print(g.nodes['CAM1'].edges)

if __name__ == '__main__':
    test_graph() 