from knotpy import canonical, find_reidemeister_1_remove_kink, to_knotpy_notation
from knotpy.invariants.jones import jones
from knotpy.notation.pd import from_pd_notation
from knotpy.algorithms.sanity import sanity_check
from knotpy.reidemeister.simplify import simplify_non_increasing, simplify_decreasing, simplify
from knotpy.algorithms.topology import is_unknot
from time import time

_DISPLAY_TIME = True

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

    j = jones(simple_unknot)
    t = time()
    s = simplify_decreasing(simple_unknot)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones(s) == j

    j = jones(nasty_unknot)
    t = time()
    s = simplify_decreasing(nasty_unknot)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones(s) == j

    j = jones(reducible_unknot)
    t = time()
    s = simplify_decreasing(reducible_unknot)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones(s) == j


    j = jones(culprit_unknot)
    t = time()
    s = simplify_decreasing(culprit_unknot)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert not is_unknot(s)
    assert len(s) == len(culprit_unknot)
    assert jones(s) == j

    j = jones(culprit_after_increase)
    t = time()
    s = simplify_decreasing(culprit_after_increase)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert not is_unknot(s)
    assert len(s) < len(culprit_after_increase)
    assert jones(s) == j

    j = jones(goeritz_unknot)
    t = time()
    s = simplify_decreasing(goeritz_unknot)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert not is_unknot(s)
    assert len(s) == len(goeritz_unknot)
    assert jones(s) == j


def test_simplify_hard_unknots_nonincreasing():

    simple_unknot, nasty_unknot, culprit_unknot, culprit_after_increase,goeritz_unknot,reducible_unknot = _get_hard_knot_examples()

    j = jones(simple_unknot)
    t = time()
    s = simplify_non_increasing(simple_unknot)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones(s) == j

    print("nasty")
    j = jones(nasty_unknot)
    t = time()

    s = simplify_non_increasing(nasty_unknot)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones(s) == j

    print("reducible")

    j = jones(reducible_unknot)
    t = time()
    s = simplify_non_increasing(reducible_unknot)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones(s) == j

    print("culprit")


    j = jones(culprit_unknot)
    t = time()
    s = simplify_non_increasing(culprit_unknot)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert not is_unknot(s)
    assert jones(s) == j

    print("culprit after")

    j = jones(culprit_after_increase)
    t = time()
    s = simplify_non_increasing(culprit_after_increase, greediness=0)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones(s) == j

    print("goeritz_unknot")


    j = jones(goeritz_unknot)
    t = time()
    s = simplify_non_increasing(goeritz_unknot)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert not is_unknot(s)
    assert jones(s) == j



def test_simplify_hard_unknots_nonincreasing_greedy():

    simple_unknot, nasty_unknot, culprit_unknot, culprit_after_increase,goeritz_unknot,reducible_unknot = _get_hard_knot_examples()

    j = jones(simple_unknot)
    t = time()
    s = simplify_non_increasing(simple_unknot, greediness=1)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones(s) == j

    j = jones(nasty_unknot)
    t = time()
    s = simplify_non_increasing(nasty_unknot, greediness=1)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones(s) == j

    j = jones(reducible_unknot)
    t = time()
    s = simplify_non_increasing(reducible_unknot, greediness=1)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert is_unknot(s)
    assert jones(s) == j

    j = jones(culprit_unknot)
    t = time()
    s = simplify_non_increasing(culprit_unknot, greediness=1)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert not is_unknot(s)
    assert jones(s) == j

    j = jones(culprit_after_increase)
    t = time()
    s = simplify_non_increasing(culprit_after_increase, greediness=1)
    if _DISPLAY_TIME: print("Time:", time() - t)
    #assert is_unknot(s)
    assert jones(s) == j

    j = jones(goeritz_unknot)
    t = time()
    s = simplify_non_increasing(goeritz_unknot, greediness=1)
    if _DISPLAY_TIME: print("Time:", time() - t)
    assert not is_unknot(s)
    assert jones(s) == j






def test_simplify_hard_unknots_smart():

    simple_unknot, nasty_unknot, culprit_unknot, culprit_after_increase,goeritz_unknot,reducible_unknot = _get_hard_knot_examples()

    j = jones(simple_unknot)
    t = time()
    print("..")
    s = simplify(simple_unknot)
    if _DISPLAY_TIME: print("Time (simple unknot):", time() - t)
    assert is_unknot(s)
    assert jones(s) == j
    # solves in 0.06s

    j = jones(reducible_unknot)
    t = time()
    s = simplify(reducible_unknot)
    if _DISPLAY_TIME: print("Time (reducible unknot):", time() - t)
    assert is_unknot(s)
    assert jones(s) == j
    # solves in 0.06s

    j = jones(nasty_unknot)
    t = time()
    s = simplify(nasty_unknot)
    if _DISPLAY_TIME: print("Time (nasty unknot):", time() - t)
    assert is_unknot(s)
    assert jones(s) == j
    # solves in 0.006s

    j = jones(culprit_unknot)
    t = time()
    s = simplify(culprit_unknot, depth=1)
    #from knotpy.reidemeister.simplify import _old_simplify_smart
    #s = OLD_simplify_smart(culprit_unknot,  depth=1)
    if _DISPLAY_TIME: print("Time (culprit knot):", time() - t)
    assert is_unknot(s)
    assert jones(s) == j
    # solves in 12.4s

#wanda_ex = from_pd_notation("[[0,12,9],[5,4,13],[0,1,10],[9,11,8],[10,13,11,12],[5,1,6,2],[2,6,3,7],[4,7,3,8]]")
#
#
#


def test_simplify_hard_unknots_smart_string():

    simple_unknot, nasty_unknot, culprit_unknot, culprit_after_increase,goeritz_unknot,reducible_unknot = _get_hard_knot_examples()

    j = jones(simple_unknot)
    t = time()
    print("..")
    s = simplify(simple_unknot)
    if _DISPLAY_TIME: print("Time (simple unknot):", time() - t)
    assert is_unknot(s)
    assert jones(s) == j
    # solves in 0.06s

    j = jones(reducible_unknot)
    t = time()
    s = simplify(reducible_unknot)
    if _DISPLAY_TIME: print("Time (reducible unknot):", time() - t)
    assert is_unknot(s)
    assert jones(s) == j
    # solves in 0.06s

    j = jones(nasty_unknot)
    t = time()
    s = simplify(nasty_unknot)
    if _DISPLAY_TIME: print("Time (nasty unknot):", time() - t)
    assert is_unknot(s)
    assert jones(s) == j
    # solves in 0.006s

    j = jones(culprit_unknot)
    t = time()
    s = simplify(culprit_unknot, depth=1)
    #from knotpy.reidemeister.simplify import _old_simplify_smart
    #s = OLD_simplify_smart(culprit_unknot,  depth=1)
    if _DISPLAY_TIME: print("Time (culprit knot):", time() - t)
    assert is_unknot(s)
    assert jones(s) == j


def test_smart():
    import knotpy as kp
    from time import time
    return

    kp.settings.allowed_moves = "r1,r2,r3"



    g = [
    "a=V(b3) b=X(c0 d0 c1 a0) c=X(b0 b2 d3 e0) d=X(b1 f0 e1 c2) e=X(c3 d2 f3 f2) f=X(d1 g0 e3 e2) g=V(f1)",
    "a=V(b0) b=X(a0 c0 d3 c1) c=X(b1 b3 e3 d0) d=X(c3 e2 f3 b2) e=X(f1 f0 d1 c2) f=X(e1 e0 g0 d2) g=V(f2)",
    "a=V(b0) b=X(a0 c0 d0 c1) c=X(b1 b3 e3 e2) d=X(b2 e1 f3 f2) e=X(g0 d1 c3 c2) f=X(g3 g2 d3 d2) g=X(e0 h0 f1 f0) h=V(g1)",
    "a=V(b0) b=X(a0 c0 d3 d2) c=X(b1 e3 f3 d0) d=X(c3 f2 b3 b2) e=X(g3 h0 g2 c1) f=X(g1 g0 d1 c2) g=X(f1 f0 e2 e0) h=V(e1)",
    "a=V(b0) b=X(a0 c0 d3 c1) c=X(b1 b3 e3 f0) d=X(f3 f2 e1 b2) e=X(g0 d2 f1 c2) f=X(c3 e2 d1 d0) g=V(e0)",
    "a=V(b0) b=X(a0 c0 d3 e0) c=X(b1 f3 g0 d0) d=X(c3 f2 e1 b2) e=X(b3 d2 f1 f0) f=X(e3 e2 d1 c1) g=V(c2)",
    "a=V(b3) b=X(c0 d0 e3 a0) c=X(b0 e2 f3 f2) d=X(b1 g0 f1 e0) e=X(d3 f0 c1 b2) f=X(e1 d2 c3 c2) g=V(d1)",
    "a=V(b3) b=X(c0 d0 c1 a0) c=X(b0 b2 e3 f0) d=X(b1 f2 e1 e0) e=X(d3 d2 f1 c2) f=X(c3 e2 d1 g0) g=V(f3)"
    ]
    k1 = {kp.from_knotpy_notation(_) for _ in g}
    print("knotoids =", len(k1))


    t = time()
    kp.settings.allowed_moves = "r1,r2,r3,flype"
    k2 = {kp.simplify(_, 1, 0) for _ in k1}
    print("knotoids =", len(k2), "(depth=1, flype)", time()-t)

    t = time()
    kp.settings.allowed_moves = "r1,r2,r3,flype"
    k2 = {kp.simplify(_, 1, 1) for _ in k1}
    print("knotoids =", len(k2), "(depth=1, flype)", time()-t)

    t = time()
    kp.settings.allowed_moves = "r1,r2,r3,flype"
    k2 = {kp.simplify(_, 2, flype=False) for _ in k1}
    print("knotoids =", len(k2), "(depth=2,flype)", time()-t)

    t = time()
    kp.settings.allowed_moves = "r1,r2,r3,flype"
    k2 = {kp.simplify(_, 2, 1, flype=False) for _ in k1}
    print("knotoids =", len(k2), "(depth=2,flype)", time()-t)

    t = time()
    kp.settings.allowed_moves = "r1,r2,r3,flype"
    k2 = {kp.simplify(_, 2, 0, flype=True) for _ in k1}
    print("knotoids =", len(k2), "(depth=2,flype)", time()-t)

    t = time()
    kp.settings.allowed_moves = "r1,r2,r3,flype"
    k2 = {kp.simplify(_, 2, 1, flype=True) for _ in k1}
    print("knotoids =", len(k2), "(depth=2,flype)", time()-t)


    """
    results:
    
    1. no flype implemented
    knotoids = 6 (depth=1) 0.2614920139312744
    knotoids = 6 (depth=1, flype) 0.23985505104064941
    knotoids = 5 (depth=2) 14.676136016845703
    knotoids = 5 (depth=2,flype) 15.1371750831604
    
    
    knotoids = 2 (depth=2,flype) 546.3404619693756 (flype after "Invalid greediness level")
    knotoids = 3 (depth=2,flype) 105.85588383674622 (to the end)
    
    f
f
f
f
f
f
f
f
knotoids = 2 (depth=2,flype) 520.7462918758392

    """

def do_not_test_goeritz_unknot():

    print(to_knotpy_notation(canonical(from_pd_notation(
        "[[2,15,3,16],[6,4,7,3],[14,6,15,5],[5,13,4,14],[1,13,2,12],[1,8,0,7],[9,0,8,19],[16,9,17,10],[10,17,11,18],[19,12,18,11]]"))))


    k = from_pd_notation("[[11,1,12,0],[1,13,2,12],[13,3,14,2],[3,15,4,14],[4,21,5,0],[20,5,21,6],[15,11,16,10],[10,16,9,17],[6,17,7,18],[18,7,19,8],[8,19,9,20]]")
    print(len(k))
    a = simplify(k, depth=2, flype=True)
    print(len(a))

    # depth=2, 11 -> 9

if __name__ == '__main__':


    culprit_unknot = from_pd_notation("[[2,15,3,16],[6,4,7,3],[14,6,15,5],[5,13,4,14],[1,13,2,12],[1,8,0,7],[9,0,8,19],[16,9,17,10],[10,17,11,18],[19,12,18,11]]")
    culprit_unknot = canonical(culprit_unknot)
    culprit_unknot.name = "culprit"
    print(to_knotpy_notation(culprit_unknot))

    goeritz_unknot = from_pd_notation("[[11,1,12,0],[1,13,2,12],[13,3,14,2],[3,15,4,14],[4,21,5,0],[20,5,21,6],[15,11,16,10],[10,16,9,17],[6,17,7,18],[18,7,19,8],[8,19,9,20]]")
    goeritz_unknot = canonical(goeritz_unknot)
    goeritz_unknot.name = "goeritz"
    print(to_knotpy_notation(goeritz_unknot))
    exit()



    do_not_test_goeritz_unknot()
    exit()

    test_smart()

    exit()

    t = time()

    t1 = time()
    print("non-increasing")
    test_simplify_hard_unknots_nonincreasing()
    t2 = time()
    print("greedy")
    test_simplify_hard_unknots_nonincreasing_greedy()
    t3 = time()
    print("Nonincreasing:", t2 - t1, "Greedy:", t3 - t2)


    print("test hard")
    test_simplify_hard_unknots_reducing()
    print("test hard smart")
    test_simplify_hard_unknots_smart()

    test_simplify_hard_unknots_smart_string()


    print("Full Time:", time() - t)