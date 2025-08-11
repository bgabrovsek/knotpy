from knotpy import homflypt
from knotpy.notation.pd import from_pd_notation
from knotpy.notation.native import from_knotpy_notation
from knotpy.algorithms.sanity import sanity_check
from knotpy.reidemeister.reidemeister import random_reidemeister_move, all_reidemeister_moves
from knotpy.invariants.jones import jones

def _get_examples():
    """
    Return a tuple of example knots as planar diagrams.
    """
    knot_31 = from_pd_notation("[[1,5,2,4],[3,1,4,6],[5,3,6,2]]")
    knot_41 = from_pd_notation("[[4,2,5,1],[8,6,1,5],[6,3,7,4],[2,7,3,8]]")
    knot_52 = from_pd_notation("[[2,8,3,7],[4,10,5,9],[6,2,7,1],[8,4,9,3],[10,6,1,5]]")
    return knot_31, knot_41, knot_52

def test_choose_random_reidemeister_moves():
    """
    Test that random Reidemeister moves preserve essential invariants and pass sanity checks.
    """
    for k in _get_examples():
        original_invariant = homflypt(k)
        for _ in range(10):
            k_ = random_reidemeister_move(k)
            assert k != k_  # Ensure the diagram changes
            assert sanity_check(k_)
            modified_invariant = homflypt(k_)
            assert modified_invariant == original_invariant, (
                f"HOMFLYPT mismatch: {modified_invariant} != {original_invariant} for {k_}"
            )

def test_all_reidemeister_moves():
    """
    Test that all diagrams reachable by a single Reidemeister move have the same invariants 
    and pass the sanity check.
    """
    for k in _get_examples():
        original_invariant = jones(k)
        for k_ in all_reidemeister_moves(k):
            assert sanity_check(k_)
            modified_invariant = jones(k_)
            assert modified_invariant == original_invariant, (
                f"Jones mismatch: {modified_invariant} != {original_invariant} for {k_}"
            )

if __name__ == "__main__":
    # Manual execution of all tests
    print("Running test_choose_random_reidemeister_moves...")
    test_choose_random_reidemeister_moves()
    print("test_choose_random_reidemeister_moves PASSED.\n")

    print("Running test_all_reidemeister_moves...")
    test_all_reidemeister_moves()
    print("test_all_reidemeister_moves PASSED.")
