import knotpy as kp
from sympy import expand


def helper_test_connected_sum_on_knots(a, b, arcs=None, test_jones=True):

    ab = kp.connected_sum(a, b, arcs)
    assert kp.sanity_check(ab)
    if test_jones:
        assert expand(jab := kp.jones(ab)) == expand((ja := kp.jones(a)) * (jb := kp.jones(b)))



    components = kp.connected_sum_decomposition(ab)
    assert len(components) == 2
    ab1, ab2 = components
    assert kp.sanity_check(ab1)
    assert kp.sanity_check(ab2)
    if test_jones:
        j1 = kp.jones(ab1)
        j2 = kp.jones(ab2)
        assert j1 == ja or j1 == jb
        assert j2 == ja or j2 == jb
        assert j1 != j2

    assert kp.canonical(ab2) != kp.canonical(ab1)
    assert kp.canonical(ab1) == kp.canonical(a) or kp.canonical(ab1) == kp.canonical(b)
    assert kp.canonical(ab2) == kp.canonical(a) or kp.canonical(ab2) == kp.canonical(b)


def test_connected_sum():
    helper_test_connected_sum_on_knots(kp.knot("3_1"), kp.knot("4_1"))


def test_disjoint_sum():
    a = kp.knot("3_1")
    b = kp.knot("4_1")

    ab = kp.disjoint_union(a, b)

    assert kp.sanity_check(ab)

    ja = kp.jones(a)
    jb = kp.jones(b)
    jab = kp.jones(ab)

    components = kp.disjoint_union_decomposition(ab)
    assert len(components) == 2

    ab1, ab2 = components

    j1 = kp.jones(ab1)
    j2 = kp.jones(ab2)

    assert kp.sanity_check(ab1)
    assert kp.sanity_check(ab2)

    assert j1 == ja or j1 == jb
    assert j2 == ja or j2 == jb
    assert j1 != j2

    assert kp.canonical(ab2) != kp.canonical(ab1)
    assert kp.canonical(ab1) == kp.canonical(a) or kp.canonical(ab1) == kp.canonical(b)
    assert kp.canonical(ab2) == kp.canonical(a) or kp.canonical(ab2) == kp.canonical(b)


def test_all_connected_sums():
    a = kp.knot("3_1")
    b = kp.knot("4_1")

    d = []

    for arc_a in a.arcs:
        for arc_b in b.arcs:
            d.append(kp.connected_sum(a, b, [arc_a, arc_b]))
            helper_test_connected_sum_on_knots(a, b, arcs=[arc_a, arc_b], test_jones=False)


if __name__ == '__main__':

    test_disjoint_sum()
    test_connected_sum()
    test_all_connected_sums()

"""


a → X(b3 c0 c3 b0), b → X(a3 c2 c1 a0), c → X(a1 b2 b1 a2)
a → X(b3 c0 c3 b0), b → X(a3 c2 c1 a0), c → X(a1 b2 b1 a2)

a → X(b3 b2 c3 d0), b → X(d3 c0 a1 a0), c → X(b1 d2 d1 a2), d → X(a3 c2 c1 b0)
a → X(b3 b2 c3 d0), b → X(d3 c0 a1 a0), c → X(b1 d2 d1 a2), d → X(a3 c2 c1 b0) with framing 0

"""