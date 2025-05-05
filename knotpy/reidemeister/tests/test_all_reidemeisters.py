
from knotpy.notation.native import from_knotpy_notation
from knotpy.algorithms.sanity import sanity_check
from knotpy.notation.pd import from_pd_notation
from knotpy.reidemeister.reidemeister import find_all_reidemeister_moves, make_all_reidemeister_moves, choose_random_reidemeister_moves, make_reidemeister_move
from knotpy.invariants.jones_polynomial import jones_polynomial

def _get_examples():
    knot_31 = from_pd_notation("[[1,5,2,4],[3,1,4,6],[5,3,6,2]]")
    knot_41 = from_pd_notation("[[4,2,5,1],[8,6,1,5],[6,3,7,4],[2,7,3,8]]")
    knot_52 = from_pd_notation("[[2,8,3,7],[4,10,5,9],[6,2,7,1],[8,4,9,3],[10,6,1,5]]")
    diagram1 = from_knotpy_notation("a=X(c0 b0 b3 e0) b=X(a1 c3 f0 a2) c=X(a0 e3 d3 b1) d=X(e2 g0 f1 c2) e=X(a3 g1 d0 c1) f=X(b2 d2 g3 g2) g=X(d1 e1 f3 f2)")
    #diagram2 = from_knotpy_notation("a=X(b0 c3 a3 a2) b=X(a0 c2 c1 c0) c=X(b3 b2 b1 a1)")
    diagram3 = from_knotpy_notation("a=X(b0 c3 c2 b1) b=X(a0 a3 c1 c0) c=X(b3 b2 a2 a1)")
    diagram4 = from_knotpy_notation("a=X(a1 a0 b0 c3) b=X(a2 b2 b1 c0) c=X(b3 c2 c1 a3)")
    return diagram1, diagram3, diagram4, knot_31, knot_41, knot_52


def test_choose_random_reidemeister_moves():

    diagrams = _get_examples()
    for i in range(10):
        for k in diagrams:
            j = jones_polynomial(k)
            moves = choose_random_reidemeister_moves(k)
            for move in moves:
                k_ = make_reidemeister_move(k, move)
                j_ = jones_polynomial(k_)
                assert sanity_check(k_)
                assert jones_polynomial(k_) == j

    for k in diagrams:
        j = jones_polynomial(k)
        moves = choose_random_reidemeister_moves(k, 10)
        for move in moves:
            k_ = make_reidemeister_move(k, move)
            j_ = jones_polynomial(k_)
            assert sanity_check(k_)
            assert jones_polynomial(k_) == j

def test_all_reidemeister_moves():
    diagrams = _get_examples()
    for k in diagrams:
        j = jones_polynomial(k)
        #moves = list(find_all_reidemeister_moves(k))
        k_ = make_all_reidemeister_moves(k, 1)
        for k__ in k_:
            assert sanity_check(k__)
            assert jones_polynomial(k__) == j

def test_all_reidemeister_moves_depth_2():
    diagrams = _get_examples()
    for k in diagrams:
        j = jones_polynomial(k)
        moves = list(find_all_reidemeister_moves(k))
        k_ = make_all_reidemeister_moves(k, moves, depth=2)
        for k__ in k_:
            assert sanity_check(k__)
            assert jones_polynomial(k__) == j

if __name__ == "__main__":
    test_choose_random_reidemeister_moves()
    test_all_reidemeister_moves()
    #test_all_reidemeister_moves_depth_2()  # slow