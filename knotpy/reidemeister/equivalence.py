from typing import Union, Set, List
from itertools import combinations

from functools import partial
import re

from knotpy.utils.disjoint_union_set import DisjointSetUnion
from knotpy.algorithms.canonical import canonical
from knotpy.utils.set_utils import LeveledSet
from knotpy.reidemeister.space import detour_space, crossing_non_increasing_space
from knotpy.manipulation.symmetry import flip
from knotpy._settings import settings


def _debug_dsu(ls):
    print("***")
    for key, ls in ls.items():
        print(key)
        print("  ", list(ls))
    print("HHH")


def reduce_equivalent_diagrams(diagrams: set | list, depth=1):
    """
    Input: list of diagrams
    Output: dictionary of unique diagrams (keys are the original diagrams that are unique, values are list of diagrams equivalent to the key)

    if greedy is True, the algorithm is much faster, but does not explore the whole Reidmeister space.
    """

    # TODO: make some sort of progress bar
    # TODO: implement greedy

    def join_if_equivalent_diagrams():
        """If any two leveled sets have non-empty intersection (Reidemeister equivalence found), we join the diagrams in the DSU."""

        for (key1, ls1), (key2, ls2) in combinations(leveled_sets.items(), 2):
            # is there a non-empty intersection?
            if ls1.intersection(ls2):
                DSU[key1] = key2  # join the sets (we found a diagram equivalence)

    # put the diagrams in a disjoint set union (equivalence relation)
    DSU = DisjointSetUnion([k for k in diagrams])

    # Store each diagram as a leveled set (levels are Reidemeister depths), the keys are original diagram and the values
    # are the leveled sets.
    # If flips are allowed, include flips at the beginning.
    if "FLIP" in settings.allowed_moves:
        leveled_sets = {
            k: LeveledSet(crossing_non_increasing_space({canonical(k), canonical(flip(k, inplace=False))}, assume_canonical=True)) for k
            in DSU.elements}
    else:
        # TODO: can we assume canonical, check crossing_non_intersecting_space?
        leveled_sets = {
            k: LeveledSet(crossing_non_increasing_space(canonical(k), assume_canonical=True)) for k
            in DSU.elements}

    # print("0")
    # _debug_dsu(leveled_sets)

    # If there are any two diagrams equivalent in different leveled sets, mark them as equivalent
    join_if_equivalent_diagrams()
    #print(len(list(DSU.representatives())))

    # print("1")
    # _debug_dsu(leveled_sets)


    """
    For all next levels, increase the number of crossings by 1 or 2 (via R1 and R2 moves),
    followed by all possible R3 moves and crossing-reducing R1 and R2 moves.
    """
    for depth_index in range(depth):

        # make Reidemeister moves (one depth-level)
        for key, ls in leveled_sets.items():

            if all(_.number_of_crossings != 0 for _ in ls):  # only make additional Reidemeister moves if any were found at a previous level

                ls.new_level(detour_space(ls[-1], assume_canonical=True))  # increase number of crossings in a "smart" way

                ls.new_level(crossing_non_increasing_space(ls[-1], assume_canonical=True ))


        join_if_equivalent_diagrams()
        #print(len(list(DSU.representatives())))

    # return the set of unique diagrams (remove duplicates)
    # print(DSU)
    # print(repr(DSU))
    # print(str(DSU))
    #
    # print("Classes", DSU.classes())
    # print("Representatives")
    # for r in DSU.representatives():
    #     print("   ", r)
    # print("Elements")
    # for e in DSU.elements:
    #     print("   ", e)
    # print("Dictionary")
    # for g in DSU:
    #     print("    ", g)

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