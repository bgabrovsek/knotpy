import knotpy as kp
from knotpy import export_pdf


def test_flype():
    for k in kp.knots((4, 8)):
        h = kp.homflypt(k)
        for f in kp.find_flypes(k):
            fk = kp.flype(k, f)
            assert kp.sanity_check(fk)
            fh = kp.homflypt(fk)
            assert h == fh
            assert k != fk

def test_flype_case():
    k = kp.knot("6_2")

    for i, f in enumerate(kp.find_flypes(k)):

        print(f)
        fk = kp.flype(k, f)
        print(fk)
        assert kp.sanity_check(fk)


if __name__ == '__main__':
    pass

    test_flype()
    test_flype_case()

    # a = kp.from_knotpy_notation("a → V(b0), b → X(a0 c0 d3 c1), c → X(b1 b3 e0 d2), d → X(f3 g0 c3 b2), e → V(c2), f → X(g3 h0 i3 d0), g → X(d1 i2 h1 f0), h → X(f1 g2 j3 j2), i → X(j1 j0 g1 f2), j → X(i1 i0 h3 h2)")
    # b = kp.from_knotpy_notation("a → V(b0), b → X(a0 c0 d3 c1), c → X(b1 b3 e0 d2), d → X(h3 g0 c3 b2), e → V(c2), f → X(i1 g2 g1 h2), g → X(d1 f2 f1 i0), h → X(j1 j0 f3 d0), i → X(g3 f0 j3 j2), j → X(h1 h0 i3 i2)")
    # kp.draw(a, with_labels=True, show=True)
    # #kp.draw(b, show=True)

    #test_flype()
    # test_flype_multiple_knotoids()