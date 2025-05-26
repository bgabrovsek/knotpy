from knotpy.notation.native import from_knotpy_notation
from knotpy.algorithms.canonical import canonical
from knotpy.algorithms.sanity import sanity_check
from knotpy.notation.pd import from_pd_notation
from knotpy.algorithms.orientation import orient

def test_canonical():
    native_a = "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2)"
    native_b = "x=X(y1 m0 w1 w0) y=V(m1 x0 w3) w=X(x3 x2 m2 y2) m=V(x1 y0 w2)"
    native_c = "a=V(b0 c3 d3) b=V(a0 d2 c0) c=X(b2 d1 d0 a1) d=X(c2 c1 b1 a2)" # different

    k_a = from_knotpy_notation(native_a)
    k_b = from_knotpy_notation(native_b)
    k_c = from_knotpy_notation(native_c)

    assert sanity_check(k_a)
    assert sanity_check(k_b)

    c_a = canonical(k_a)
    c_b = canonical(k_b)
    c_c = canonical(k_c)

    assert sanity_check(c_a)
    assert sanity_check(c_b)

    assert c_a == c_b
    assert not c_a == c_c

def test_canonical_oriented():
    native_a = "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2)"
    native_b = "x=X(y1 m0 w1 w0) y=V(m1 x0 w3) w=X(x3 x2 m2 y2) m=V(x1 y0 w2)"
    native_c = "a=V(b0 c3 d3) b=V(a0 d2 c0) c=X(b2 d1 d0 a1) d=X(c2 c1 b1 a2)" # different

    k_a = orient(from_knotpy_notation(native_a))
    k_b = orient(from_knotpy_notation(native_b))
    k_c = orient(from_knotpy_notation(native_c))

    assert sanity_check(k_a)
    assert sanity_check(k_b)


    c_a = canonical(k_a)
    c_b = canonical(k_b)
    c_c = canonical(k_c)

    assert c_a.is_oriented()
    assert c_b.is_oriented()
    assert c_c.is_oriented()


    assert sanity_check(c_a)
    assert sanity_check(c_b)

    assert c_a.is_oriented()
    assert c_b.is_oriented()

    assert c_a == c_b
    assert not c_a == c_c


def test_canonical_degenerate():
    a = from_knotpy_notation("a=V(a1 a0 a3 a2)")
    b = from_knotpy_notation("a=V(a3 a2 a1 a0)")

    ka = canonical(a)
    kb = canonical(b)

    assert sanity_check(a)
    assert sanity_check(b)
    assert sanity_check(ka)
    assert sanity_check(kb)

    assert ka == kb


def test_canonical_degenerate_oriented():
    a = orient(from_knotpy_notation("a=V(a1 a0 a3 a2)"))
    b = orient(from_knotpy_notation("a=V(a3 a2 a1 a0)"))

    ka = canonical(a)
    kb = canonical(b)

    assert sanity_check(ka)
    assert sanity_check(kb)

    assert ka == kb

def test_canonical_knots():
    pd1 = "X[0,1,2,3],X[4,5,3,2],X[5,4,1,0]"
    pd2 = "X[0,1,2,3],X[4,5,1,0],X[5,4,3,2]"
    k1 = from_pd_notation(pd1)
    k2 = from_pd_notation(pd2)
    c1 = canonical(k1)
    c2 = canonical(k2)

    assert sanity_check(c2)
    assert sanity_check(c1)

    assert c1 == c2


def test_canonical_knots_oriented():
    pd1 = "X[0,1,2,3],X[4,5,3,2],X[5,4,1,0]"
    pd2 = "X[0,1,2,3],X[4,5,1,0],X[5,4,3,2]"
    k1 = orient(from_pd_notation(pd1))
    k2 = orient(from_pd_notation(pd2))
    c1 = canonical(k1)
    c2 = canonical(k2)
    assert sanity_check(c2)
    assert sanity_check(c1)
    assert c1 == c2

if __name__ == "__main__":
    test_canonical()
    test_canonical_degenerate()
    test_canonical_knots()

    test_canonical_oriented()
    test_canonical_degenerate_oriented()
    test_canonical_knots_oriented()