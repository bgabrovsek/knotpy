from sympy import sympify

from knotpy.reidemeister.reidemeister_3 import find_reidemeister_3_triangle, reidemeister_3
from knotpy.notation.native import from_knotpy_notation, to_knotpy_notation
from knotpy.notation.pd import from_pd_notation
from knotpy.algorithms.canonical import canonical
from knotpy.invariants.yamada import yamada_polynomial
from knotpy.invariants.jones_polynomial import jones_polynomial
from knotpy.algorithms.topology import is_knot
from knotpy.algorithms.sanity import sanity_check


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

    for diagram in _get_examples():
        j = jones_polynomial(diagram)
        for loc in find_reidemeister_3_triangle(diagram):
            k_ = reidemeister_3(diagram, loc, inplace=False)
            assert sanity_check(k_)
            assert jones_polynomial(k_) == j


    #
    # diagrams = _get_examples()
    # for k, polynomial in diagrams.items():
    #     r1_locations = list(find_reidemeister_2_poke(k))
    #
    #     for loc in r1_locations:
    #         k_ = reidemeister_2_poke(k, loc, inplace=False)
    #         if k.name[0] == 'l':
    #             assert sanity_check(k_)
    #         elif is_knot(k_):
    #             assert jones_polynomial(k_) == polynomial
    #         else:
    #             assert yamada_polynomial(k_) == polynomial


if __name__ == '__main__':
    test_r3_find_moves()
    test_make_reidemeister_3_move()