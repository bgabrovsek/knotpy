import knotpy as kp

def test_closure():
    k = kp.from_knotpy_notation("a → V(b0), b → X(a0 c0 c3 d0), c → X(b1 d3 e3 b2), d → X(b3 e2 f3 c1), e → X(f2 f0 d1 c2), f → X(e1 g0 e0 d2), g → V(f1)")
    assert kp.sanity_check(k)

    u = kp.closure(k, under=True)
    assert kp.sanity_check(u)
    assert kp.is_knot(u)

    o = kp.closure(k, over=True)
    assert kp.sanity_check(o)
    assert kp.is_knot(o)

    b = kp.closure(k, over=True, under=True)
    assert kp.sanity_check(b)
    assert not kp.is_knot(b)


if __name__ == '__main__':
    test_closure()