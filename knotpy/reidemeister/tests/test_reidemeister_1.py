from sympy import sympify

from knotpy.reidemeister.reidemeister_1 import reidemeister_1_add_kink, reidemeister_1_remove_kink, find_reidemeister_1_add_kink, find_reidemeister_1_remove_kink
from knotpy.notation.native import from_knotpy_notation, to_knotpy_notation
from knotpy.notation.pd import from_pd_notation
from knotpy.algorithms.canonical import canonical
from knotpy.invariants.yamada import yamada
from knotpy.invariants.jones import jones
from knotpy.algorithms.topology import is_knot
from knotpy.algorithms.sanity import sanity_check

def _get_examples():
    knots = {
        # trefoil
        from_knotpy_notation("a=X(b3 c0 c3 b0) b=X(a3 c2 c1 a0) c=X(a1 b2 b1 a2) ['name'='k31']"): sympify("-t**4 + t**3 + t"),
        # 5_2 knot
        from_knotpy_notation("a=X(b3 b2 c3 c2) b=X(d3 e0 a1 a0) c=X(e3 d0 a3 a2) d=X(c1 e2 e1 b0) e=X(b1 d2 d1 c0) ['name'='k52']"): sympify("-t**6 + t**5 - t**4 + 2*t**3 - t**2 + t"),
        # hopf link
        from_knotpy_notation("a=X(b3 b2 b1 b0) b=X(a3 a2 a1 a0) ['name'='l21']"): sympify("-A**9 - A**8 - A**7 - A**6 + A**3 + A**2 + A + 1"),
    }
    thetas = {
        # trivial theta
        from_knotpy_notation("a=V(b0 b2 b1) b=V(a0 a2 a1) ['name'='t01']"): sympify("-A**4 - A**3 - 2*A**2 - A - 1"),
        # 3_1 theta
        from_knotpy_notation("a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 e1 d0) d=X(c3 e0 b1 a2) e=X(d1 c2 c1 b2) ['name'='t31']"): sympify("-A**12 - A**11 - A**10 - A**9 - A**8 - A**6 - A**4 + 1"),
        # trivial handcuff
        from_knotpy_notation("a=V(a1 a0 b0) b=V(a2 b2 b1) ['name'='h01']"): sympify("0"),
        # hopf handcuff
        from_knotpy_notation("a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2) ['name'='h21']"): sympify("-A**9 - A**8 - A**7 - A**6 + A**3 + A**2 + A + 1")
    }

    diagrams = knots.copy()
    diagrams.update(thetas)

    return diagrams

def test_r1_find_moves():
    diagrams = _get_examples()

    # make a reidemeister move
    for k, polynomial in diagrams.items():
        r1_locations = list(find_reidemeister_1_add_kink(k))
        assert len(r1_locations) == 4 * len(k.arcs)

def test_make_reidemeister_1_move():
    diagrams = _get_examples()
    for k, polynomial in diagrams.items():
        r1_locations = list(find_reidemeister_1_add_kink(k))

        for loc in r1_locations:
            k_ = reidemeister_1_add_kink(k, loc, inplace=False)
            if k.name[0] == 'l':
                assert sanity_check(k_)
            elif is_knot(k_):
                assert jones(k_) == polynomial
            else:
                assert yamada(k_) == polynomial

def test_make_undo_reidemeister_1_move():
    diagrams = _get_examples()
    for k, polynomial in diagrams.items():
        r1_locations = list(find_reidemeister_1_add_kink(k))

        for loc in r1_locations:
            k_ = reidemeister_1_add_kink(k, loc, inplace=False)
            r1_un_locations = list(find_reidemeister_1_remove_kink(k_))
            assert len(r1_un_locations) == 1
            k__ = reidemeister_1_remove_kink(k_, r1_un_locations[0], inplace=False)
            assert canonical(k) == canonical(k__)


if __name__ == '__main__':

    test_r1_find_moves()
    #test_make_reidemeister_1_move()  # slow
    test_make_undo_reidemeister_1_move()