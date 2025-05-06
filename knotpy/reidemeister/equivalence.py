from typing import Union, Set, List
from itertools import combinations

from functools import partial
import re

from knotpy.utils.disjoint_union_set import DisjointSetUnion
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.canonical import canonical
from knotpy.utils.set_utils import LeveledSet
from knotpy.reidemeister.space import reidemeister_3_space, detour_space, crossing_non_increasing_space, \
    reduce_crossings_greedy, crossing_non_increasing_space_greedy
from knotpy.reidemeister.reidemeister_1 import reidemeister_1_remove_kink, choose_reidemeister_1_remove_kink
from knotpy.reidemeister.reidemeister_2 import reidemeister_2_unpoke, choose_reidemeister_2_unpoke
from knotpy.reidemeister.reidemeister import make_all_reidemeister_moves
from knotpy.algorithms.topology import is_unknot
from knotpy.manipulation.symmetry import flip
from knotpy.reidemeister.reidemeister import _clean_allowed_moves


def reduce_equivalent_diagrams(diagrams: Union[Set[PlanarDiagram], List[PlanarDiagram]], depth=1, allowed_moves=None):
    """
    Input: list of diagrams
    Output: dictionary of unique diagrams (keys are the original diagrams that are unique, values are list of diagrams equivalent to the key)

    """

    _DEBUG = True

    def join_if_equivalent_diagrams():
        """If any two leveled sets have non-empty intersection (Reidemeister equivalence found), we join the diagrams in the DSU."""

        for (key1, ls1), (key2, ls2) in combinations(leveled_sets.items(), 2):
            # is there a non-empty intersection?
            if ls1.intersection(ls2):
                DSU[key1] = key2  # join the sets (we found a diagram equivalence)

    allowed_moves = _clean_allowed_moves(allowed_moves)

    # put the diagrams in a disjoint set union (equivalence relation)
    DSU = DisjointSetUnion([canonical(k) for k in diagrams])

    # If flip move is allowed, flips are equivalent to the primary diagrams
    if allowed_moves is not None and "FLIP" in allowed_moves:
        raise NotImplementedError("Flip moves are not yet implemented for equivalence.")
        # for k in DSU.elements:
        #     DSU[k] = canonical(flip(k, inplace=False))

    # Store each diagram as a leveled set (levels are Reidemeister depths), the keys are original diagram and the values
    # are the leveled sets.
    leveled_sets = {k: LeveledSet(crossing_non_increasing_space(k, assume_canonical=False, allowed_moves=allowed_moves)) for k in DSU.elements}

    # If there are any two diagrams equivalent in different leveled sets, mark them as equivalent
    join_if_equivalent_diagrams()

    # # If there are no crossings to reduce, we are done.
    # if any(_.number_of_crossings == 0 for _ in ls):
    #     return min(ls)

    """
    For all next levels, increase the number of crossings by 1 or 2 (via R1 and R2 moves),
    followed by all possible R3 moves and crossing-reducing R1 and R2 moves.
    """
    for depth_index in range(depth):
        if _DEBUG:
            print("Depth:", depth_index)

        # make Reidemeister moves (one depth-level)
        for key, ls in leveled_sets.items():
            if _DEBUG:
                print("  Key:", key)

            if all(_.number_of_crossings != 0 for _ in ls):  # only make additional Reidemeister moves if any were found at a previous level
                ls.new_level(detour_space(ls[-1]))
                ls.new_level(crossing_non_increasing_space(ls[-1], allowed_moves=allowed_moves))

        join_if_equivalent_diagrams()

    # return the set of unique diagrams (remove duplicates)
    return DSU.to_dict()

if __name__ == "__main__":

    # DSU test
    dsu = DisjointSetUnion("abcdefg")
    dsu["a"] = "b"
    dsu["c"] = "d"
    dsu["e"] = "f"
    dsu["b"] = "c"
    print(dsu)
    print("Groups:", [group for group in dsu])
    print("Classes:", [classes for classes in dsu.classes()])
    print("Representatives:", [rep for rep in dsu.representatives()])
    print("Elements:", [e for e in dsu.elements])
    print("Dictionary:", dsu.to_dict())

    # leveled set
    ls1 = LeveledSet(["a", "b"])
    ls1.new_level(["c", "d"])
    ls1.new_level(["e", "f"])
    ls2 = LeveledSet(["g", "h"])
    ls2.new_level(["i", "j"])
    ls2.new_level(["k", "c"])
    print(ls1)
    print(ls2)
    print("Intersection:", ls1.intersection(ls2))