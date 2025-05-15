from knotpy import canonical, find_reidemeister_1_remove_kink
from knotpy.invariants.jones_polynomial import jones_polynomial
from knotpy.notation.pd import from_pd_notation
from knotpy.algorithms.sanity import sanity_check
from knotpy.reidemeister.simplify import simplify
from knotpy.reidemeister.space import detour_space, crossing_reducing_space
from knotpy.notation.native import to_knotpy_notation
from knotpy.algorithms.topology import is_unknot
from time import time

_DISPLAY_TIME = False

def _get_hard_knot_examples():

    nasty_unknot = from_pd_notation("[[0,3,1,4],[3,10,2,9],[9,2,8,1],[6,10,5,11],[11,7,12,6],[7,13,8,12],[0,4,13,5]]")
    culprit_unknot = from_pd_notation("[[2,15,3,16],[6,4,7,3],[14,6,15,5],[5,13,4,14],[1,13,2,12],[1,8,0,7],[9,0,8,19],[16,9,17,10],[10,17,11,18],[19,12,18,11]]")
    simple_unknot = from_pd_notation("[[8,10,7,1],[7,2,6,1],[5,3,6,2],[4,9,5,10],[4,8,3,9]]")
    culprit_after_increase = from_pd_notation("[[20,15,3,16],[6,4,7,3],[14,6,15,22],[23,13,4,14],[1,13,2,12],[1,8,0,7],[9,0,8,19],[16,9,17,10],[10,17,11,18],[19,12,18,11],[20,5,21,22],[2,23,21,5]]")
    goeritz_unknot = from_pd_notation("[[11,1,12,0],[1,13,2,12],[13,3,14,2],[3,15,4,14],[4,21,5,0],[20,5,21,6],[15,11,16,10],[10,16,9,17],[6,17,7,18],[18,7,19,8],[8,19,9,20]]")

    reducible_unknot = from_pd_notation("[[8,1,7,0],[8,0,9,19],[19,2,18,1],[18,6,17,7],[12,11,11,10],[9,3,10,2],[12,3,13,4],[4,13,5,14],[14,5,15,6],[15,16,16,17]]")

    assert sanity_check(nasty_unknot)
    assert sanity_check(culprit_unknot)
    assert sanity_check(simple_unknot)
    assert sanity_check(goeritz_unknot)
    assert sanity_check(reducible_unknot)
    assert sanity_check(culprit_after_increase)

    return simple_unknot, nasty_unknot, culprit_unknot, culprit_after_increase, goeritz_unknot, reducible_unknot

def test_simplify_hard_unknots_reducing():

    simple_unknot, nasty_unknot, culprit_unknot, culprit_after_increase, goeritz_unknot, reducible_unknot = _get_hard_knot_examples()

    j = jones_polynomial(simple_unknot)
    t = time()
    s = simplify(simple_unknot, "reducing")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones_polynomial(s) == j

    j = jones_polynomial(nasty_unknot)
    t = time()
    s = simplify(nasty_unknot, "reducing")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones_polynomial(s) == j

    j = jones_polynomial(reducible_unknot)
    t = time()
    s = simplify(reducible_unknot, "reducing")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones_polynomial(s) == j


    j = jones_polynomial(culprit_unknot)
    t = time()
    s = simplify(culprit_unknot, "reducing")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert not is_unknot(s)
    assert len(s) == len(culprit_unknot)
    assert jones_polynomial(s) == j

    j = jones_polynomial(culprit_after_increase)
    t = time()
    s = simplify(culprit_after_increase, "reducing")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert not is_unknot(s)
    assert len(s) < len(culprit_after_increase)
    assert jones_polynomial(s) == j

    j = jones_polynomial(goeritz_unknot)
    t = time()
    s = simplify(goeritz_unknot, "reducing")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert not is_unknot(s)
    assert len(s) == len(goeritz_unknot)
    assert jones_polynomial(s) == j


def test_simplify_hard_unknots_nonincreasing():

    simple_unknot, nasty_unknot, culprit_unknot, culprit_after_increase,goeritz_unknot,reducible_unknot = _get_hard_knot_examples()

    j = jones_polynomial(simple_unknot)
    t = time()
    s = simplify(simple_unknot, "nonincreasing")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones_polynomial(s) == j

    j = jones_polynomial(nasty_unknot)
    t = time()
    s = simplify(nasty_unknot, "nonincreasing")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones_polynomial(s) == j

    j = jones_polynomial(reducible_unknot)
    t = time()
    s = simplify(reducible_unknot, "nonincreasing")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones_polynomial(s) == j

    j = jones_polynomial(culprit_unknot)
    t = time()
    s = simplify(culprit_unknot, "nonincreasing")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert not is_unknot(s)
    assert jones_polynomial(s) == j

    j = jones_polynomial(culprit_after_increase)
    t = time()
    s = simplify(culprit_after_increase, "nonincreasing")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones_polynomial(s) == j

    j = jones_polynomial(goeritz_unknot)
    t = time()
    s = simplify(goeritz_unknot, "nonincreasing")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert not is_unknot(s)
    assert jones_polynomial(s) == j



def test_simplify_hard_unknots_nonincreasing_greedy():

    simple_unknot, nasty_unknot, culprit_unknot, culprit_after_increase,goeritz_unknot,reducible_unknot = _get_hard_knot_examples()

    j = jones_polynomial(simple_unknot)
    t = time()
    s = simplify(simple_unknot, "nig")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones_polynomial(s) == j

    j = jones_polynomial(nasty_unknot)
    t = time()
    s = simplify(nasty_unknot, "nig")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones_polynomial(s) == j

    j = jones_polynomial(reducible_unknot)
    t = time()
    s = simplify(reducible_unknot, "nig")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones_polynomial(s) == j

    j = jones_polynomial(culprit_unknot)
    t = time()
    s = simplify(culprit_unknot, "nig")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert not is_unknot(s)
    assert jones_polynomial(s) == j

    j = jones_polynomial(culprit_after_increase)
    t = time()
    s = simplify(culprit_after_increase, "nig")
    if _DISPLAY_TIME: print("Time:", time() - t)
    #assert is_unknot(s)
    assert jones_polynomial(s) == j

    j = jones_polynomial(goeritz_unknot)
    t = time()
    s = simplify(goeritz_unknot, "nig")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert not is_unknot(s)
    assert jones_polynomial(s) == j

def test_simplify_hard_unknots_smart():

    simple_unknot, nasty_unknot, culprit_unknot, culprit_after_increase,goeritz_unknot,reducible_unknot = _get_hard_knot_examples()

    j = jones_polynomial(simple_unknot)
    t = time()
    s = simplify(simple_unknot, "smart")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones_polynomial(s) == j
    # solves in 0.06s

    j = jones_polynomial(reducible_unknot)
    t = time()
    s = simplify(reducible_unknot, "smart")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones_polynomial(s) == j
    # solves in 0.06s

    j = jones_polynomial(nasty_unknot)
    t = time()
    s = simplify(nasty_unknot, "smart")
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones_polynomial(s) == j
    # solves in 0.006s

    j = jones_polynomial(culprit_unknot)
    t = time()
    s = simplify(culprit_unknot, "smart", depth=1)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones_polynomial(s) == j
    # solves in 12.4s

#wanda_ex = from_pd_notation("[[0,12,9],[5,4,13],[0,1,10],[9,11,8],[10,13,11,12],[5,1,6,2],[2,6,3,7],[4,7,3,8]]")



if __name__ == '__main__':
    # takes 13.3 seconds to solve all knots (culprit and Goeritz)
    t = time()

    # test greedy
    t1 = time()
    test_simplify_hard_unknots_nonincreasing()
    t2 = time()
    test_simplify_hard_unknots_nonincreasing_greedy()
    t3 = time()
    print("Nonincreasing:", t2 - t1, "Greedy:", t3 - t2)



    test_simplify_hard_unknots_reducing()
    test_simplify_hard_unknots_smart()

    print("Time:", time() - t)