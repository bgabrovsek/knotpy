from sympy import sympify

from knotpy.notation.native import from_knotpy_notation, to_knotpy_notation
from knotpy.invariants.jones import jones
from knotpy.algorithms.sanity import sanity_check
from knotpy.reidemeister.space import crossing_preserving_space, crossing_decreasing_space, crossing_non_increasing_space, detour_space


def _get_examples():
    diagram1 = from_knotpy_notation("a=X(c0 b0 b3 e0) b=X(a1 c3 f0 a2) c=X(a0 e3 d3 b1) d=X(e2 g0 f1 c2) e=X(a3 g1 d0 c1) f=X(b2 d2 g3 g2) g=X(d1 e1 f3 f2)")
    #diagram2 = from_knotpy_notation("a=X(b0 c3 a3 a2) b=X(a0 c2 c1 c0) c=X(b3 b2 b1 a1)")
    diagram3 = from_knotpy_notation("a=X(b0 c3 c2 b1) b=X(a0 a3 c1 c0) c=X(b3 b2 a2 a1)")
    diagram4 = from_knotpy_notation("a=X(a1 a0 b0 c3) b=X(a2 b2 b1 c0) c=X(b3 c2 c1 a3)")
    return diagram1, diagram3, diagram4


def test_r3_space():
    for diagram in _get_examples():
        j = jones(diagram)
        r3s = crossing_preserving_space(diagram, assume_canonical=False)
        for d in r3s:
            assert sanity_check(d)
            jd = jones(d)
            assert j == jd, "Jones polynomials are not equal. Expected {}, got {}. Diagram: {}".format(j, jd, to_knotpy_notation(diagram))


def test_crossing_reducing_space():
    for diagram in _get_examples():
        j = jones(diagram)
        r3s = crossing_decreasing_space(diagram, assume_canonical=False)
        for d in r3s:
            assert sanity_check(d)
            jd = jones(d)
            assert j == jd, "Jones polynomials are not equal. Expected {}, got {}. Diagram: {}".format(j, jd, to_knotpy_notation(diagram))

def test_non_increasing_space():
    for g in [0,1]:
        for diagram in _get_examples():
            j = jones(diagram)
            r3s = crossing_non_increasing_space(diagram, greediness=g, assume_canonical=False)
            for d in r3s:
                assert sanity_check(d)
                jd = jones(d)
                assert j == jd, "Jones polynomials are not equal. Expected {}, got {}. Diagram: {}".format(j, jd, to_knotpy_notation(diagram))

def test_detour_space():
    for diagram in _get_examples():
        j = jones(diagram)
        r3s = detour_space(diagram, assume_canonical=False)
        for d in r3s:
            assert sanity_check(d)
            jd = jones(d)
            assert j == jd, "Jones polynomials are not equal. Expected {}, got {}. Diagram: {}".format(j, jd, to_knotpy_notation(diagram))


def test_empty_space():
    assert crossing_preserving_space(set(), assume_canonical=True) == set()
    assert crossing_decreasing_space(set(), assume_canonical=True) == set()
    assert crossing_non_increasing_space(set(), greediness=1,assume_canonical=True) == set()
    assert crossing_non_increasing_space(set(), greediness=0,assume_canonical=True) == set()
    assert detour_space(set(), assume_canonical=True) == set()

if __name__ == '__main__':
    import knotpy as kp
    # s = "a → X(a3 b1 c0 a0), b → X(a1 a1 g2 d3), c → X(a2 c2 c1 e3), d → X(b2 f3 e0 b3), e → X(d2 f2 g3 c3), f → X(g1 g0 e1 d1), g → X(f1 f0 b2 e2)"
    # s = kp.from_knotpy_notation(s)
    # print(s)
    # print(sanity_check(s))
    # exit()

    test_r3_space()
    test_crossing_reducing_space()
    test_non_increasing_space()
    test_detour_space()
    test_empty_space()