from knotpy.algorithms.closure import closure
from knotpy.notation.native import from_knotpy_notation
from knotpy import sanity_check
from knotpy import export_png
def test_closure():
    k = from_knotpy_notation("a → V(b0), b → X(a0 c0 c3 d0), c → X(b1 d3 e3 b2), d → X(b3 e2 f3 c1), e → X(f2 f0 d1 c2), f → X(e1 g0 e0 d2), g → V(f1)")

    export_png(k, "test.png")
    assert sanity_check(k)
    u = closure(k, under=True)
    assert sanity_check(u)
    o = closure(k, over=True)
    assert sanity_check(o)
    b = closure(k, True, True)
    assert sanity_check(b)


if __name__ == '__main__':
    test_closure()