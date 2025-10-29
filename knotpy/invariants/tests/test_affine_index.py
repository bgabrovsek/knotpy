import knotpy as kp

def test_affine_index():
    s = "a=V(b3) b=X(c0 c2 c1 a0) c=X(b0 b2 b1 d0) d=V(c3)"
    k = kp.from_knotpy_notation(s)
    assert kp.sanity_check(k)
    print(kp.affine_index_polynomial(k))

    s = "a=V(b3) b=X(d0 c3 d1 a0) c=X(e0 e2 d2 b1) d=X(b0 b2 c2 e1) e=X(c0 d3 c1 f0) f=V(e3)"
    k = kp.from_knotpy_notation(s)
    assert kp.sanity_check(k)
    print(kp.yamada(kp.closure(k, True, True)))
    print(kp.affine_index_polynomial(k))
    print(kp.yamada(kp.closure(kp.mirror(k), True, True)))


if __name__ == "__main__":
    test_affine_index()