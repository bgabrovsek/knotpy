
from knotpy.tables.families import bouquet
from knotpy.notation.native import from_knotpy_notation
from knotpy.tables.families import path_graph, cycle_graph
from knotpy.algorithms.canonical import canonical
from knotpy.algorithms.disjoint_union import disjoint_union

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.contract import contract_arc


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
    g_ab = disjoint_union(g_a, g_b)
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

# tests/test_contract_.py

def test_contract_arc():
    # 1) Contract where the removed vertex has a loop
    k, r = PlanarDiagram(), PlanarDiagram()
    k.set_arcs_from("x0a0,x1x2,x4d0,x3y2,y0e0,y1f0,y3g0,y4h0")
    r.set_arcs_from("y0e0,y1f0,y2d0,y3a0,y4y5,y6g0,y7h0")
    contract_arc(k, (("y", 2), ("x", 3)))
    assert k == r

    # 2) Contract in a “nice” graph
    k, r = PlanarDiagram(), PlanarDiagram()
    k.set_arcs_from("x0a0,x1b0,x2c0,x4d0,x3y2,y0e0,y1f0,y3g0,y4h0")
    r.set_arcs_from("y0e0,y1f0,y2d0,y3a0,y4b0,y5c0,y6g0,y7h0")
    contract_arc(k, (("y", 2), ("x", 3)))
    assert k == r

    # 3) Contract where the remaining vertex has a loop
    k, r = PlanarDiagram(), PlanarDiagram()
    k.set_arcs_from("x0a0,x1b0,x2c0,x4d0,x3y2,y0y1,y3g0,y4h0")
    r.set_arcs_from("y0y1,y2d0,y3a0,y4b0,y5c0,y6g0,y7h0")
    contract_arc(k, (("y", 2), ("x", 3)))
    assert k == r

    # 4) Mixed-loop case
    k, r = PlanarDiagram(), PlanarDiagram()
    k.set_arcs_from("x0a0,x1b0,x2c0,x4d0,x3y2,y0e0,y1y4,y3g0")
    r.set_arcs_from("y0e0,y1y7,y2d0,y3a0,y4b0,y5c0,y6g0")
    contract_arc(k, (("y", 2), ("x", 3)))
    assert k == r


if __name__ == "__main__":

    test_contract_edge()
    test_contract_edge_attributes()
    test_contract_arc()