from sympy import sympify

from knotpy import homflypt, homflypt
from knotpy.reidemeister.reidemeister_3 import find_reidemeister_3_triangle, reidemeister_3
from knotpy.notation.native import from_knotpy_notation, to_knotpy_notation
from knotpy.notation.pd import from_pd_notation
from knotpy.algorithms.canonical import canonical
from knotpy.invariants.yamada import yamada
from knotpy.invariants.jones import jones
from knotpy.invariants.bracket import bracket
from knotpy.algorithms.topology import is_knot
from knotpy.algorithms.sanity import sanity_check



"""
AssertionError: Bracket is not equal. Expected -1/sqrt(t) - 1/t**(5/2), got -1/t**2 - 1/t**4. Diagram: Diagram a → X(b0 c3 a3 a2), b → X(a0 c2 c1 c0), c → X(b3 b2 b1 a1) and Diagram a → X(a1 a0 b2 c1) _r3=True, b → X(c3 c2 a2 c0) _r3=True, c → X(b3 a3 b1 b0) _r3=True (_sequence=R3 )
E               assert -1/t**2 - 1/t**4 == -1/sqrt(t) - 1/t**(5/2)

"""

def _get_examples():
    diagram1 = from_knotpy_notation("a=X(c0 b0 b3 e0) b=X(a1 c3 f0 a2) c=X(a0 e3 d3 b1) d=X(e2 g0 f1 c2) e=X(a3 g1 d0 c1) f=X(b2 d2 g3 g2) g=X(d1 e1 f3 f2)")
    diagram2 = from_knotpy_notation("a=X(b0 c3 a3 a2) b=X(a0 c2 c1 c0) c=X(b3 b2 b1 a1)")
    diagram3 = from_knotpy_notation("a=X(b0 c3 c2 b1) b=X(a0 a3 c1 c0) c=X(b3 b2 a2 a1)")
    diagram4 = from_knotpy_notation("a=X(a1 a0 b0 c3) b=X(a2 b2 b1 c0) c=X(b3 c2 c1 a3)")
    return diagram1, diagram2, diagram3, diagram4

def test_r3_find_moves():
    diagram1, diagram2, diagram3, diagram4 = _get_examples()

    r3_locations_1 = list(find_reidemeister_3_triangle(diagram1))
    r3_locations_2 = list(find_reidemeister_3_triangle(diagram2))
    r3_locations_3 = list(find_reidemeister_3_triangle(diagram3))
    r3_locations_4 = list(find_reidemeister_3_triangle(diagram4))

    assert len(r3_locations_1) == 4
    assert len(r3_locations_2) == 1
    assert len(r3_locations_3) == 2
    assert len(r3_locations_4) == 1


def test_make_reidemeister_3_move():

    # -1/sqrt(t) - 1/t**(5/2) == -1/t**2 - 1/t**4

    for diagram in _get_examples():
        j = jones(diagram)
        b = bracket(diagram, normalize=True)
        for loc in find_reidemeister_3_triangle(diagram):
            k_ = reidemeister_3(diagram, loc, inplace=False)
            assert sanity_check(k_)

            # b_ = bracket(k_, normalize=True)
            # assert b_ == b,
            # print(k_)
            #
            # print(jones(k_))
            # print(j)
            # print()
            j_ = jones(k_)
            assert j_ == j, "Bracket is not equal. Expected {}, got {}. Diagram: {} and {}".format(j, j_, diagram, k_)


def test_strange_case():
    import knotpy as kp


    w = kp.knot("3_1")


    a = "a → X(b0 c3 a3 a2), b → X(a0 c2 c1 c0), c → X(b3 b2 b1 a1)"
    #    a → X(b0 c3 a3 a2), b → X(a0 c2 c1 c0), c → X(b3 b2 b1 a1)
    b = "a → X(a1 a0 b2 c1), b → X(c3 c2 a2 c0), c → X(b3 a3 b1 b0)"




    a = kp.from_knotpy_notation(a)
    b = kp.from_knotpy_notation(b)

    o = kp.orientations(b)
    for _ in o:
        print(kp.writhe(_))

    #
    # print(canonical(a))
    # print(canonical(b))


    ha = bracket(a)
    hb = bracket(b)
    print(ha)
    print(hb)
    print(ha==hb)

    ja = jones(a)
    jb = jones(b)
    print(ja)
    print(jb)
    print(ja==jb)

    """
    AssertionError: Bracket is not equal. Expected -1/sqrt(t) - 1/t**(5/2), got -1/t**2 - 1/t**4. Diagram: Diagram a → X(b0 c3 a3 a2), b → X(a0 c2 c1 c0), c → X(b3 b2 b1 a1) and Diagram a → X(a1 a0 b2 c1) _r3=True, b → X(c3 c2 a2 c0) _r3=True, c → X(b3 a3 b1 b0) _r3=True (_sequence=R3 )
E               assert -1/t**2 - 1/t**4 == -1/sqrt(t) - 1/t**(5/2)

    Returns:

    """

if __name__ == '__main__':
    test_strange_case()
    exit()
    for x in range(100):
        test_make_reidemeister_3_move()