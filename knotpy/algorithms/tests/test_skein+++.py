from knotpy.notation.native import from_knotpy_notation
from knotpy.algorithms.canonical import canonical
from knotpy.invariants.skein import crossing_to_vertex, smoothen_crossing

def test_skein():
    trefoil = "a=X(b3 c0 c3 b0) b=X(a3 c2 c1 a0) c=X(a1 b2 b1 a2)"
    trefoil_A = "b=X(c3 c2 c1 c0) c=X(b3 b2 b1 b0)"
    trefoil_B = "b=X(b3 c2 c1 b0) c=X(c3 b2 b1 c0)"
    trefoil_X = "a=V(b3 c0 c3 b0) b=X(a3 c2 c1 a0) c=X(a1 b2 b1 a2)"

    k = from_knotpy_notation(trefoil)
    k_A = from_knotpy_notation(trefoil_A)
    k_B = from_knotpy_notation(trefoil_B)
    k_X = from_knotpy_notation(trefoil_X)

    k_A_skein = smoothen_crossing(k, crossing_for_smoothing="a", method="A", inplace=False)
    k_B_skein = smoothen_crossing(k, crossing_for_smoothing="a", method="B", inplace=False)
    k_X_skein = crossing_to_vertex(k, crossing="a", inplace=False)

    assert canonical(k_A_skein) == canonical(k_A)
    assert canonical(k_B_skein) == canonical(k_B)
    assert canonical(k_X_skein) == canonical(k_X)


if __name__ == "__main__":
    test_skein()
