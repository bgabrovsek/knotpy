
import knotpy as kp
from knotpy.algorithms.cut_set import is_arc_cut_set, arc_cut_sets

def test_arc_cut_set():
    N = 4
    w = kp.wheel_graph(N)  # "a" is the center node

    # test classical cut sets

    arcs = w.arcs["a"]
    assert len(arcs) == N - 1
    assert is_arc_cut_set(w, arcs)
    assert not is_arc_cut_set(w, arcs[:-1])
    assert not is_arc_cut_set(w, arcs[1:])

    arcs = w.arcs["b"]
    assert len(arcs) == 3
    assert is_arc_cut_set(w, arcs)
    assert not is_arc_cut_set(w, arcs[:-1])
    assert not is_arc_cut_set(w, arcs[1:])

    # with extra singletons
    w.set_arcs_from("b3z0") # add a vertex
    arcs = w.arcs["z"]
    assert is_arc_cut_set(w, arcs)
    assert not is_arc_cut_set(w, arcs, include_singletons=False)

    w.add_vertex("w")
    assert is_arc_cut_set(w, arcs)
    assert not is_arc_cut_set(w, arcs, include_singletons=False)


def test_find_cut_sets():

    w = kp.wheel_graph(3)  # "a" is the center node
    cs3 = arc_cut_sets(w, 3)
    assert len(cs3) == 4

    w = kp.wheel_graph(5)  # "a" is the center node
    cs3 = arc_cut_sets(w, 3)
    assert len(cs3) == 4

def test_cut_set_knotoid():
    k = kp.from_knotpy_notation("a=V(b0) b=X(a0 c0 c2 d0) c=X(b1 d1 b2 e0) d=X(b3 c1 f0 g3) e=V(c3) f=X(d2 g2 h3 h2) g=X(h1 h0 f1 d3) h=X(g1 g0 f3 f2)")
    cs = kp.cut_nodes(k)
    print(cs)

if __name__ == "__main__":

    test_arc_cut_set()
    test_find_cut_sets()
    test_cut_set_knotoid()