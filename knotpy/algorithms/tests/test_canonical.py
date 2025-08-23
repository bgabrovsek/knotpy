import knotpy as kp

def test_canonical():
    native_a = "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2)"
    native_b = "x=X(y1 m0 w1 w0) y=V(m1 x0 w3) w=X(x3 x2 m2 y2) m=V(x1 y0 w2)"
    native_c = "a=V(b0 c3 d3) b=V(a0 d2 c0) c=X(b2 d1 d0 a1) d=X(c2 c1 b1 a2)"  # different

    k_a = kp.from_knotpy_notation(native_a)
    k_b = kp.from_knotpy_notation(native_b)
    k_c = kp.from_knotpy_notation(native_c)

    assert kp.sanity_check(k_a)
    assert kp.sanity_check(k_b)
    c_a = kp.canonical(k_a)
    c_b = kp.canonical(k_b)
    c_c = kp.canonical(k_c)
    assert kp.sanity_check(c_a)
    assert kp.sanity_check(c_b)
    assert c_a == c_b
    assert not c_a == c_c

def test_canonical_oriented():
    native_a = "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2)"
    native_b = "w=X(m1 y2 x1 x0) y=V(m0 x2 w1) x=X(w3 w2 y1 m2) m=V(y0 w0 x3)"
    native_c = "a=V(b0 c3 d3) b=V(a0 d2 c0) c=X(b2 d1 d0 a1) d=X(c2 c1 b1 a2)"  # different

    k_a = kp.orient(kp.from_knotpy_notation(native_a))
    k_b = kp.orient(kp.from_knotpy_notation(native_b))
    k_c = kp.orient(kp.from_knotpy_notation(native_c))

    assert kp.canonical(k_a) == kp.canonical(k_b)
    assert kp.canonical(k_b) != kp.canonical(k_c)
    assert kp.sanity_check(k_a)
    assert kp.sanity_check(k_b)
    c_a = kp.canonical(k_a)
    c_b = kp.canonical(k_b)
    c_b_ = kp.canonical(kp.reverse(k_b))
    c_c = kp.canonical(k_c)
    assert c_a.is_oriented()
    assert c_b.is_oriented()
    assert c_c.is_oriented()
    assert kp.sanity_check(c_a)
    assert kp.sanity_check(c_b)
    assert c_a.is_oriented()
    assert c_b.is_oriented()
    assert c_a == c_b or c_a == c_b_
    assert not c_a == c_c

def test_canonical_degenerate():
    a = kp.from_knotpy_notation("a=V(a1 a0 a3 a2)")
    b = kp.from_knotpy_notation("a=V(a3 a2 a1 a0)")
    ka = kp.canonical(a)
    kb = kp.canonical(b)
    assert kp.sanity_check(a)
    assert kp.sanity_check(b)
    assert kp.sanity_check(ka)
    assert kp.sanity_check(kb)
    assert ka == kb

def test_canonical_degenerate_oriented():
    a = kp.orient(kp.from_knotpy_notation("a=V(a1 a0 a3 a2)"))
    b = kp.orientations(kp.from_knotpy_notation("a=V(a3 a2 a1 a0)"))
    ka = kp.canonical(a)
    kb = [kp.canonical(_) for _ in b]
    assert kp.sanity_check(ka)
    assert all(kp.sanity_check(_) for _ in b)
    assert ka in kb

def test_canonical_knots():
    pd1 = "X[0,1,2,3],X[4,5,3,2],X[5,4,1,0]"
    pd2 = "X[0,1,2,3],X[4,5,1,0],X[5,4,3,2]"
    k1 = kp.from_pd_notation(pd1)
    k2 = kp.from_pd_notation(pd2)
    c1 = kp.canonical(k1)
    c2 = kp.canonical(k2)
    assert kp.sanity_check(c2)
    assert kp.sanity_check(c1)
    assert c1 == c2

def test_canonical_knots_oriented():
    pd1 = "X[0,1,2,3],X[4,5,3,2],X[5,4,1,0]"
    pd2 = "X[0,1,2,3],X[4,5,1,0],X[5,4,3,2]"
    k1 = kp.orient(kp.from_pd_notation(pd1))
    k2 = kp.orient(kp.from_pd_notation(pd2))
    c1 = kp.canonical(k1)
    c2 = kp.canonical(k2)
    assert kp.sanity_check(c2)
    assert kp.sanity_check(c1)
    assert c1 == c2

if __name__ == "__main__":
    test_canonical()
    test_canonical_degenerate()
    test_canonical_knots()
    test_canonical_oriented()
    test_canonical_degenerate_oriented()
    test_canonical_knots_oriented()