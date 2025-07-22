from itertools import combinations

from knotpy.utils.disjoint_union_set import DisjointSetUnion
from knotpy.algorithms.canonical import canonical
from knotpy.utils.set_utils import LeveledSet
from knotpy.reidemeister.space import detour_space, crossing_non_increasing_space
from knotpy.manipulation.symmetry import flip
from knotpy._settings import settings

def reduce_equivalent_diagrams(diagrams: set | list, depth=1):
    """
    Input: list of diagrams
    Output: dictionary of unique diagrams (keys are the original diagrams that are unique, values are list of diagrams equivalent to the key)

    if greedy is True, the algorithm is much faster, but does not explore the whole Reidmeister space.

    Example:

        input = [k1, k2, k3, l1, l2, l3]
        output = {simplified(k1): {k1, k2, k3}, simplified(l1): {l1, l2, l3}}

    OUTPUT: {
    Diagram named 3_1 a → X(b3 c0 c3 b0), b → X(a3 c2 c1 a0), c → X(a1 b2 b1 a2):
            {Diagram named 3_1 a → X(e0 e3 d1 b0), b → X(a3 d0 d3 f2), d → X(b1 a2 f3 b2), e → X(a0 f1 f0 a1), f → X(e2 e1 b3 d2) (_sequence=R2+R2-R2+R2-R2+),
             Diagram named 3_1 a → X(e3 f2 c3 e0), c → X(f3 e2 e1 a2), e → X(a3 c2 c1 a0), f → X(f1 f0 a1 c0) (_sequence=R2+R2-R1+R1+R1-),
             Diagram named 3_1 a → X(b3 c0 d3 b0), b → X(a3 c2 c1 a0), c → X(a1 b2 b1 d0), d → X(c3 d2 d1 a2) (_sequence=R1+R2+R2-R1+R1-)},
    Diagram named 4_1 a → X(b3 b2 c3 d0), b → X(d3 c0 a1 a0), c → X(b1 d2 d1 a2), d → X(a3 c2 c1 b0):
            {Diagram named 4_1 a → X(b3 b2 c2 e2) _r3=True, b → X(f0 d1 a1 a0) _r3=True, c → X(c3 e3 a2 c0) _r3=True, d → X(e0 b1 f3 f2), e → X(d0 f1 a3 c1) _r3=True, f → X(b0 e1 d3 d2) (_sequence=R2+R3 R3 R3 R3 ),
            Diagram named 4_1 a → X(b3 b2 e2 d0), b → X(d3 c0 a1 a0), c → X(b1 d2 d1 e3), d → X(a3 c2 c1 b0), e → X(e1 e0 a2 c3) (_sequence=R1+R1+R1-R1-R1+),
            Diagram named 4_1 a → X(b3 b2 f3 d0), b → X(d3 c0 a1 a0), c → X(b1 d2 e0 e3), d → X(a3 f2 c1 b0), e → X(c2 f1 f0 c3), f → X(e2 e1 d1 a2) (_sequence=R1+R1+R1-R1-R2+)}}

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
            k: LeveledSet(crossing_non_increasing_space(canonical(k), greediness=0, assume_canonical=True)) for k
            in DSU.elements}

    # If there are any two diagrams equivalent in different leveled sets, mark them as equivalent
    join_if_equivalent_diagrams()

    """
    For all next levels, increase the number of crossings by 1 or 2 (via R1 and R2 moves),
    followed by all possible R3 moves and crossing-reducing R1 and R2 moves.
    """
    for depth_index in range(depth):

        # make Reidemeister moves (one depth-level)
        for key, ls in leveled_sets.items():

            if all(_.number_of_crossings != 0 for _ in ls):  # only make additional Reidemeister moves if any were found at a previous level

                ls.new_level(detour_space(ls.iter_level(-1), assume_canonical=True))  # increase number of crossings in a "smart" way

                ls.new_level(crossing_non_increasing_space(ls.iter_level(-1), greediness=1, assume_canonical=True ))


        join_if_equivalent_diagrams()

    return DSU.to_dict()








def OLD_reduce_equivalent_diagrams(diagrams: set | list, depth=1):
    """
    Input: list of diagrams
    Output: dictionary of unique diagrams (keys are the original diagrams that are unique, values are list of diagrams equivalent to the key)

    if greedy is True, the algorithm is much faster, but does not explore the whole Reidmeister space.

    Example:

        input = [k1, k2, k3, l1, l2, l3]
        output = {simplified(k1): {k1, k2, k3}, simplified(l1): {l1, l2, l3}}

    OUTPUT: {
    Diagram named 3_1 a → X(b3 c0 c3 b0), b → X(a3 c2 c1 a0), c → X(a1 b2 b1 a2):
            {Diagram named 3_1 a → X(e0 e3 d1 b0), b → X(a3 d0 d3 f2), d → X(b1 a2 f3 b2), e → X(a0 f1 f0 a1), f → X(e2 e1 b3 d2) (_sequence=R2+R2-R2+R2-R2+),
             Diagram named 3_1 a → X(e3 f2 c3 e0), c → X(f3 e2 e1 a2), e → X(a3 c2 c1 a0), f → X(f1 f0 a1 c0) (_sequence=R2+R2-R1+R1+R1-),
             Diagram named 3_1 a → X(b3 c0 d3 b0), b → X(a3 c2 c1 a0), c → X(a1 b2 b1 d0), d → X(c3 d2 d1 a2) (_sequence=R1+R2+R2-R1+R1-)},
    Diagram named 4_1 a → X(b3 b2 c3 d0), b → X(d3 c0 a1 a0), c → X(b1 d2 d1 a2), d → X(a3 c2 c1 b0):
            {Diagram named 4_1 a → X(b3 b2 c2 e2) _r3=True, b → X(f0 d1 a1 a0) _r3=True, c → X(c3 e3 a2 c0) _r3=True, d → X(e0 b1 f3 f2), e → X(d0 f1 a3 c1) _r3=True, f → X(b0 e1 d3 d2) (_sequence=R2+R3 R3 R3 R3 ),
            Diagram named 4_1 a → X(b3 b2 e2 d0), b → X(d3 c0 a1 a0), c → X(b1 d2 d1 e3), d → X(a3 c2 c1 b0), e → X(e1 e0 a2 c3) (_sequence=R1+R1+R1-R1-R1+),
            Diagram named 4_1 a → X(b3 b2 f3 d0), b → X(d3 c0 a1 a0), c → X(b1 d2 e0 e3), d → X(a3 f2 c1 b0), e → X(c2 f1 f0 c3), f → X(e2 e1 d1 a2) (_sequence=R1+R1+R1-R1-R2+)}}

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
            k: LeveledSet(crossing_non_increasing_space(canonical(k), greediness=0, assume_canonical=True)) for k
            in DSU.elements}

    # If there are any two diagrams equivalent in different leveled sets, mark them as equivalent
    join_if_equivalent_diagrams()

    """
    For all next levels, increase the number of crossings by 1 or 2 (via R1 and R2 moves),
    followed by all possible R3 moves and crossing-reducing R1 and R2 moves.
    """
    for depth_index in range(depth):

        # make Reidemeister moves (one depth-level)
        for key, ls in leveled_sets.items():

            if all(_.number_of_crossings != 0 for _ in ls):  # only make additional Reidemeister moves if any were found at a previous level

                ls.new_level(detour_space(ls.iter_level(-1), assume_canonical=True))  # increase number of crossings in a "smart" way

                ls.new_level(crossing_non_increasing_space(ls.iter_level(-1), greediness=1, assume_canonical=True ))


        join_if_equivalent_diagrams()

    return DSU.to_dict()

if __name__ == "__main__":

    pass
