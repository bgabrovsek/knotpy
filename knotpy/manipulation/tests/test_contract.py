
from knotpy.catalog.graphs import bouquet
from knotpy.notation.native import from_knotpy_notation
from knotpy.catalog.graphs import path_graph, parallel_edges, cycle_graph
from knotpy.manipulation.remove import remove_arc, remove_empty_nodes
from knotpy.manipulation.contract import contract_arc
from knotpy.algorithms.canonical import canonical
from knotpy.algorithms.disjoint_sum import disjoint_sum


def test_contract_edge():

    N = 6

    # If we contract an edge from a path P(n) it becomes P(n-1)

    g = path_graph(N)
    contract_arc(g, g.arcs["a"][0], inplace=True)
    assert canonical(g) == canonical(path_graph(N - 1))

    # If we contract an edge from a cycle P(n) it becomes P(n-1)

    g = cycle_graph(N)
    contract_arc(g, g.arcs["a"][0], inplace=True)
    assert canonical(g) == canonical(cycle_graph(N - 1))

    # connect two bouquets by an arc and contract them
    A = 3
    B = 4
    g_a = bouquet(A)
    g_b = bouquet(B)
    g_ab = disjoint_sum(g_a, g_b)
    node_a, node_b = g_ab.nodes
    g_ab.set_arc( ((node_a, g_ab.degree(node_a)), (node_b, g_ab.degree(node_b))))
    contract_arc(g_ab, ((node_a, g_ab.degree(node_a) - 1), (node_b, g_ab.degree(node_b) - 1)))
    assert canonical(g_ab) == canonical(bouquet(A + B))

def test_contract_edge_attributes():

    """

++++ CONTRACTING ****
d=V(d6 e2 d3 d2 e1 e0 d0) e=V(d5 d4 d1) ['framing'=0,'A'=0,'B'=0,'X'=3,'_deletions'=1,'_contractions'=7,'name'=None; ; d2:{'color'=1} d3:{'color'=1}]
frozenset({d1, e2})
> PlanarDiagram with 2 nodes, 4 arcs, and adjacencies d → V(d5 d2=1 d1=1 e1 e0 d0), e → V(d4 d3) with framing 0 (A=0 B=0 X=3 _deletions=1 _contractions=7)
 src ('e', 0)
 dst ('d', 1)
*** d=V(d5 d2 d1 e1 e0 d0) e=V(d4 d3) ['framing'=0,'A'=0,'B'=0,'X'=3,'_deletions'=1,'_contractions'=7,'name'=None; ; d1:{'color'=1} d2:{'color'=1}]
= PlanarDiagram with 2 nodes, 4 arcs, and adjacencies d → V(d6 d4 d3=1 d2=1 d1 e0 d0), e → V(d5) with framing 0 (A=0 B=0 X=3 _deletions=1 _contractions=7)
> PlanarDiagram with 2 nodes, 4 arcs, and adjacencies d → V(d6 d4 d3=1 d2=1 d1 e0 d0), e → V(d5) with framing 0 (A=0 B=0 X=3 _deletions=1 _contractions=7)
 src ('e', 0)
 dst ('d', 1)
*** d=V(d6 d4 d3 d2 d1 e0 d0) e=V(d5) ['framing'=0,'A'=0,'B'=0,'X'=3,'_deletions'=1,'_contractions'=7,'name'=None; ; d2:{'color'=1} d3:{'color'=1}]
= PlanarDiagram with 2 nodes, 4 arcs, and adjacencies d → V(d7 d6 d5=1 d4=1 d3=1 d2 d1 d0), e → V() with framing 0 (A=0 B=0 X=3 _deletions=1 _contractions=7)
       """
    g = from_knotpy_notation("d=V(d6 e2 d3 d2 e1 e0 d0) e=V(d5 d4 d1) ['framing'=0,'A'=0,'B'=0,'X'=3,'_deletions'=1,'_contractions'=7,'name'=None; ; d2:{'color'=1} d3:{'color'=1}]")
    c = contract_arc(g, (('d', 1), ("e", 2)))



if __name__ == "__main__":

    test_contract_edge()
    test_contract_edge_attributes()