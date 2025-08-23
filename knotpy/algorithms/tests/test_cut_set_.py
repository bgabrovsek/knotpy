
import knotpy as kp
from knotpy.algorithms.cut_set import arc_cut_sets

def test_order_2():
    a = kp.knot("3_1")
    b = kp.knot("4_1")
    ab = kp.connected_sum(a, b)

    ep1 = ab.endpoint_from_pair(("a",0))
    ep2 = ab.endpoint_from_pair(("d", 0))
    ep3 = ab.endpoint_from_pair(("b", 3))
    ep4 = ab.endpoint_from_pair(("e",3))
    ep5 = ab.endpoint_from_pair(("b", 1))
    ep6 = ab.endpoint_from_pair(("c",2))

    arc1= frozenset([ep1, ep2])
    arc2 = frozenset([ep3, ep4])
    arc3 = frozenset([ep5, ep6])

    assert arc1 in ab.arcs
    assert arc2 in ab.arcs
    assert arc3 in ab.arcs

    cut_sets = arc_cut_sets(ab, 2, minimum_partition_nodes=2)

    assert len(cut_sets) == 1
    assert set(cut_sets[0]) == {arc1, arc2}
    assert set(cut_sets[0]) != {arc1, arc3}
    assert set(cut_sets[0]) != {arc2, arc3}




    # assert is_arc_cut_set(ab, [arc1, arc2], skip_isolating_cuts=False)
    # assert not is_arc_cut_set(ab, [arc1, arc3], skip_isolating_cuts=False)
    # assert not is_arc_cut_set(ab, [arc2, arc3], skip_isolating_cuts=False)
    # assert is_arc_cut_set(ab, [arc1, arc2], skip_isolating_cuts=True)
    # assert not is_arc_cut_set(ab, [arc1, arc3], skip_isolating_cuts=True)
    # assert not is_arc_cut_set(ab, [arc2, arc3], skip_isolating_cuts=True)
    # assert len(kp.arc_cut_sets(ab, 2, skip_isolating_cuts=False)) == 1
    # assert len(kp.arc_cut_sets(ab, 2, skip_isolating_cuts=True)) == 1

def  test_arc_cut_set():
    N = 4
    w = kp.wheel_graph(N)  # "a" is the center node

    # test classical cut sets

    arcs = w.arcs["a"]
    assert len(arcs) == N - 1
    # assert is_arc_cut_set(w, arcs)
    # assert not is_arc_cut_set(w, arcs[:-1])
    # assert not is_arc_cut_set(w, arcs[1:])

    arcs = w.arcs["b"]
    assert len(arcs) == 3
    # assert is_arc_cut_set(w, arcs)
    # assert not is_arc_cut_set(w, arcs[:-1])
    # assert not is_arc_cut_set(w, arcs[1:])

    # with extra singletons
    w.set_arcs_from("b3z0") # add a vertex
    arcs = w.arcs["z"]
    # assert is_arc_cut_set(w, arcs)
    # assert not is_arc_cut_set(w, arcs, skip_isolating_cuts=True)

    w.add_vertex("w")
    # assert is_arc_cut_set(w, arcs)
    # assert not is_arc_cut_set(w, arcs, skip_isolating_cuts=True)


def test_find_cut_sets():

    # w = kp.wheel_graph(3)  # "a" is the center node
    # cs3 = arc_cut_sets(w, 3)
    # assert len(cs3) == 4

    w = kp.wheel_graph(5)  # "a" is the center node
    cs3 = arc_cut_sets(w, 3)
    assert len(cs3) == 4

def test_cut_set_knotoid():
    k = kp.from_knotpy_notation("a=V(b0) b=X(a0 c0 c2 d0) c=X(b1 d1 b2 e0) d=X(b3 c1 f0 g3) e=V(c3) f=X(d2 g2 h3 h2) g=X(h1 h0 f1 d3) h=X(g1 g0 f3 f2)")
    cs = kp.cut_nodes(k)

def test_cut_set_new():
    k = kp.knot("3_1")
    acs = kp.arc_cut_sets(k, order = 4, minimum_partition_nodes=1)
    print(acs)
    assert len(acs) == 3



if __name__ == "__main__":
    test_cut_set_new()
    test_order_2()
    test_arc_cut_set()
    test_find_cut_sets()
    test_cut_set_knotoid()
