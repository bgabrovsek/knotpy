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

def _get_hand_knot_examples():

    nasty_unknot = from_pd_notation("[[0,3,1,4],[3,10,2,9],[9,2,8,1],[6,10,5,11],[11,7,12,6],[7,13,8,12],[0,4,13,5]]")
    culprit_unknot = from_pd_notation("[[2,15,3,16],[6,4,7,3],[14,6,15,5],[5,13,4,14],[1,13,2,12],[1,8,0,7],[9,0,8,19],[16,9,17,10],[10,17,11,18],[19,12,18,11]]")
    simple_unknot = from_pd_notation("[[8,10,7,1],[7,2,6,1],[5,3,6,2],[4,9,5,10],[4,8,3,9]]")
    culprit_after_increase = from_pd_notation("[[20,15,3,16],[6,4,7,3],[14,6,15,22],[23,13,4,14],[1,13,2,12],[1,8,0,7],[9,0,8,19],[16,9,17,10],[10,17,11,18],[19,12,18,11],[20,5,21,22],[2,23,21,5]]")
    goeritz_unknot = from_pd_notation("[[11,1,12,0],[1,13,2,12],[13,3,14,2],[3,15,4,14],[4,21,5,0],[20,5,21,6],[15,11,16,10],[10,16,9,17],[6,17,7,18],[18,7,19,8],[8,19,9,20]]")

    assert sanity_check(nasty_unknot)
    assert sanity_check(culprit_unknot)
    assert sanity_check(simple_unknot)
    assert sanity_check(goeritz_unknot)

    return simple_unknot, nasty_unknot, culprit_unknot, culprit_after_increase, goeritz_unknot

def test_simplify_hard_unknots_reducing():

    simple_unknot, nasty_unknot, culprit_unknot, culprit_after_increase,goeritz_unknot = _get_hand_knot_examples()

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

    simple_unknot, nasty_unknot, culprit_unknot, culprit_after_increase,goeritz_unknot = _get_hand_knot_examples()

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

def test_simplify_hard_unknots_smart():

    simple_unknot, nasty_unknot, culprit_unknot, culprit_after_increase,goeritz_unknot = _get_hand_knot_examples()

    j = jones_polynomial(simple_unknot)
    t = time()
    s = simplify(simple_unknot, "smart")
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


def test_wanda_example():
    k = from_pd_notation("[[0,12,9],[5,4,13],[0,1,10],[9,11,8],[10,13,11,12],[5,1,6,2],[2,6,3,7],[4,7,3,8]]")
    assert sanity_check(k)


    s = simplify(k, "reducing")
    assert len(s) == 6
    assert len(k) == 8

    s = simplify(k, "non-increasing")
    assert len(s) == 6
    assert len(k) == 8

    s = simplify(k, "smart")
    assert len(s) == 6
    assert len(k) == 8


if __name__ == '__main__':
    # takes 13.3 seconds to solve all knots (culprit and Goeritz)

    t = time()
    # we should be able to solve the culprit and the Goeritz unknot

    test_wanda_example()

    test_simplify_hard_unknots_reducing()
    test_simplify_hard_unknots_nonincreasing()
    test_simplify_hard_unknots_smart()

    print("Time:", time() - t)