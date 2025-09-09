# knotpy/algorithms/simplify.py
"""
Utilities for simplifying knot/link diagrams via sequences of Reidemeister moves.

This module provides several strategies that (greedily or systematically) apply
Reidemeister moves to reduce crossings, or explore non-increasing / “smart”
searches that interleave crossing-preserving and crossing-increasing steps.

Notes
-----
- The core helpers it relies on live in `knotpy.reidemeister.space` and
  `knotpy.reidemeister.reidemeister`. Logic and behavior are preserved.
- Docstrings intentionally remain detailed; this module is frequently used by
  end users. Comments were kept close to your originals and lightly unified.
"""

from itertools import combinations

from knotpy.notation.em import to_condensed_em_notation, from_condensed_em_notation
from knotpy.classes.planardiagram import PlanarDiagram, Diagram
from knotpy.algorithms.canonical import canonical
from knotpy.utils.set_utils import LeveledSet
from knotpy.reidemeister.space import (
    _simplify_greedy_decreasing,
    crossing_non_increasing_space,
    detour_space,
)
from knotpy.reidemeister.reidemeister import (
    reidemeister_preserving_moves_generator,
    detour_generator,
    reidemeister_decreasing_moves_generator,
    flype_generator,
)
from knotpy.utils.disjoint_union_set import DisjointSetUnion
from knotpy.algorithms.symmetry import flip
from knotpy._settings import settings

__all__ = ["simplify_decreasing", "simplify", "simplify_non_increasing", "reduce_equivalent_diagrams"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek"


def simplify_decreasing(k: Diagram, inplace: bool = False) -> Diagram:
    """
    Simplify a planar diagram by applying a (non-random) sequence of crossing-decreasing Reidemeister moves
    (R1, R2, R4, R5), until there are no more such moves left. The algorithm is greedy—it performs the
    first crossing-reducing move it finds and continues to do so until there are no more such moves left.

    Args:
        k (PlanarDiagram): The planar diagram to be simplified.
        inplace (bool): Whether to simplify the given diagram in place. If
            True, the input diagram `k` will be modified directly. If False,
            the function will create a copy of `k` and perform simplifications
            on it. Defaults to False.

    Return:
        PlanarDiagram: The simplified planar diagram with possibly reduced crossings.
    """
    return _simplify_greedy_decreasing(k, to_canonical=False, inplace=inplace)


def simplify_non_increasing(k: Diagram | set | tuple | list, greediness: int = 1):
    """
    Simplify a planar diagram through Reidemeister R3 moves and crossing-decreasing
    moves. The simplification process is influenced by the specified greediness level.

    Levels of Greediness:
        - Level 0: Iteratively applies all possible R3 moves, followed by crossing-
          decreasing moves until no further simplification is achievable. This is the
          slowest level.
        - Level 1: Similar to Level 0, but at each iteration step, the process only
          continues with diagrams having the lowest number of crossings.
        - Level 2: Focuses on rapid simplification by checking for and applying R3
          moves until a crossing-decreasing move becomes viable. Then takes this
          decreased diagram and repeats the steps.
        - Level 3: Similar to level 2, except that it returns a diagram immediately
          after it reduces it (does not rerun the loop to check additional R3 moves).

    The method does not perform crossing-increasing Reidemeister moves.

    Args:
        k (PlanarDiagram | set | tuple | list): The planar diagram(s) to simplify.
        greediness (int): Specifies the level of aggressiveness for simplification.
            Default is 1.

    Return:
        PlanarDiagram | type(k): The simplified planar diagram, or the original container
        type populated with simplified diagrams if a collection was provided.
    """
    if isinstance(k, (set, tuple, list)):
        return type(k)(simplify_non_increasing(_, greediness=greediness) for _ in k)

    if greediness == 0 or greediness == 1:
        if "FLIP" in settings.allowed_moves:
            k = {k, flip(k, inplace=False)}  # explore flip as well
        return min(crossing_non_increasing_space(k, greediness=greediness, assume_canonical=False))

    elif greediness == 2:
        raise NotImplementedError("Not implemented yet.")

    elif greediness == 3:
        k = k.copy()
        number_of_nodes = len(k)

        # First, try to decrease crossings directly.
        simplify_decreasing(k, inplace=True)
        if len(k) < number_of_nodes:
            return k

        # Second, make crossing-preserving moves until there are crossings to remove.
        ls = LeveledSet(canonical(k))
        while not ls.is_level_empty(-1):
            ls.new_level()
            for _ in reidemeister_preserving_moves_generator(ls.iter_level(-2)):
                __ = simplify_decreasing(_, inplace=True)
                if len(__) < number_of_nodes:
                    return __
                else:
                    ls.add(canonical(__))

        return next(ls.iter_level(0))

    else:
        raise ValueError(f"Invalid greediness level {greediness}.")


_DEBUG_SIMPLIFY = False

def simplify(k: Diagram | set | list | tuple, depth: int = 1, flype: bool = False):

    greediness = 1

    # If multiple diagrams are given, perform steps on each diagram first.
    if isinstance(k, (set, list, tuple)):
        return [simplify(_, depth, flype=flype) for _ in k]

    # From here on, k is a single diagram.
    memory_efficient = True if k.number_of_crossings + 2 * depth < 26 * 2 - 2 else False
    if _DEBUG_SIMPLIFY: print("Memory efficient:", memory_efficient)

    settings_dump = settings.dump()
    if flype:
        settings.add_allowed_move("FLYPE")

    # # If multiple diagrams are given, perform steps on each diagram.
    # if isinstance(k, (set, list, tuple)):
    #     return [simplify(_, depth, flype=flype) for _ in k]


    # We start the search with both k and simplified k (since sometimes much reduction is already done via decreasing).
    k = {canonical(k), canonical(simplify_decreasing(k, inplace=True))}

    # If we allow flipping the diagram, include flips.
    if "FLIP" in settings.allowed_moves:
        k |= {canonical(flip(_, inplace=False)) for _ in k}

    # If there are no crossings to reduce, we are done.
    if any(_.number_of_crossings == 0 for _ in k):
        settings.load(settings_dump)
        return min(k)

    # Start off by making non-increasing moves (R3 and similar).
    # TODO: if we take greediness=0, then it takes much longer
    if memory_efficient:
        ls = LeveledSet(
            items=crossing_non_increasing_space(k, greediness=0, assume_canonical=True),
            to_string=to_condensed_em_notation,
            from_string=from_condensed_em_notation,
        )
    else:
        ls = LeveledSet(crossing_non_increasing_space(k, greediness=0, assume_canonical=True))

    # If there are no crossings to reduce, we are done.
    if any(_.number_of_crossings == 0 for _ in ls):
        settings.load(settings_dump)
        return min(ls)

    if _DEBUG_SIMPLIFY: print("Initial set:", ls.level_sizes())

    # Crossing-increasing loop
    start = ls.number_of_levels()
    for depth_index in range(depth):

        if _DEBUG_SIMPLIFY: print(f"Depth {depth_index}", ls.level_sizes())

        # Increase crossings “smartly”.
        ls.new_level()
        for lvl in (ls.iter_level(start - 2), ls.iter_level(start - 1)):
            for k in lvl:
                for _ in detour_generator(k):
                    ls.add(canonical(_))

        if _DEBUG_SIMPLIFY: print(f"Depth {depth_index} (after detour)", ls.level_sizes())

        start = ls.number_of_levels()

        # Explore the new space and reduce the diagrams.
        from knotpy.reidemeister.space import crossing_preserving_space, crossing_decreasing_space  # TODO: push this to top

        ls.new_level()
        ls.extend(crossing_preserving_space(ls.iter_level(-2), assume_canonical=True))  # may be empty if R3 not allowed

        if _DEBUG_SIMPLIFY: print(f"Depth {depth_index} (after preserving)", ls.level_sizes())

        while True:
            if greediness == 0:
                ls.new_level(crossing_decreasing_space(ls.iter_level(-1), assume_canonical=True))
                if _DEBUG_SIMPLIFY: print(f"Depth {depth_index} (after decreasing, greed={greediness})", ls.level_sizes())
            elif greediness == 1:
                # The following loop was empirically much faster (≈16×) in practice.
                while not ls.is_level_empty(-1):
                    ls.new_level()  # put reduced diagrams to the next level
                    ls.extend(canonical(set(reidemeister_decreasing_moves_generator(ls.iter_level(-2)))))
                    if _DEBUG_SIMPLIFY: print(f"Depth {depth_index} (after decreasing, greed={greediness})", ls.level_sizes())

            else:
                raise ValueError(f"Invalid greediness level {greediness}.")

            if flype:
                ls.new_level(canonical(flype_generator(ls.iter_level(-1))))
                ls.new_level(crossing_preserving_space(ls.iter_level(-2), assume_canonical=True))
                ls.extend(crossing_preserving_space(ls.iter_level(-2), assume_canonical=True))
            else:
                ls.new_level(crossing_preserving_space(ls.iter_level(-1), assume_canonical=True))

            if _DEBUG_SIMPLIFY: print(f"Depth {depth_index} (after flype)", ls.level_sizes())

            if ls.is_level_empty(-1):
                break

        # If there are no crossings to reduce, we are done.
        if any(_.number_of_crossings == 0 for _ in ls):
            settings.load(settings_dump)
            return min(ls)

    settings.load(settings_dump)
    return min(ls)




_DEBUG_RED = False

def reduce_equivalent_diagrams(diagrams: set | list, depth: int = 1, flype: bool = False) -> dict:
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
    # TODO: join leveled_sets, once we found an equality! This should really speed up the computations for many diagrams.

    greediness = 1

    # TODO: only compare strings.
    def join_if_equivalent_diagrams():
        """If any two leveled sets have non-empty intersection (Reidemeister equivalence found), we join the diagrams in the DSU."""
        for (key1, ls1), (key2, ls2) in combinations(leveled_sets.items(), 2):
            # is there a non-empty intersection?
            if ls1.intersection(ls2, evaluate=False):
                DSU[key1] = key2  # join the sets (we found a diagram equivalence)

    # We default this to True
    #memory_efficient = True if max(k.number_of_crossings for k in diagrams) + 2 * depth < 26 * 2 - 2 else False

    settings_dump = settings.dump()
    if flype:
        settings.add_allowed_move("FLYPE")

    # put the diagram strings in a disjoint set union (equivalence relation)
    DSU = DisjointSetUnion([to_condensed_em_notation(k) for k in diagrams])

    # Store each diagram as a leveled set (levels are Reidemeister depths); keys are original diagrams and
    # values are the leveled sets. If flips are allowed, include flips at the beginning.

    if "FLIP" in settings.allowed_moves:
        leveled_sets = {
            k_str: LeveledSet(
                items=crossing_non_increasing_space({canonical(from_condensed_em_notation(k_str)), canonical(flip(from_condensed_em_notation(k_str)))}, greediness=0, assume_canonical=True),
                to_string=to_condensed_em_notation,
                from_string=from_condensed_em_notation,
            )
            for k_str in DSU.elements
        }
    else:
        # TODO: can we assume canonical? (check crossing_non_increasing_space)
        leveled_sets = {
            k_str: LeveledSet(
                items=crossing_non_increasing_space(canonical(from_condensed_em_notation(k_str)), greediness=0, assume_canonical=True),
                to_string=to_condensed_em_notation,
                from_string=from_condensed_em_notation,
            )
            for k_str in DSU.elements
        }

    # If there are any two diagrams equivalent in different leveled sets, mark them as equivalent.
    join_if_equivalent_diagrams()

    """
    For all next levels, increase the number of crossings by 1 or 2 (via R1 and R2 moves),
    followed by all possible R3 moves and crossing-reducing R1 and R2 moves.
    """


    # Crossing-increasing loop
    starts = [ls.number_of_levels() for ls in leveled_sets.values()]
    indices = list(range(len(leveled_sets)))
    for depth_index in range(depth):

        if _DEBUG_RED: ls_index = 0

        for ls_index, start, ls in zip(indices, starts, leveled_sets.values()):

            if _DEBUG_RED: print(f"Depth {depth_index} [{ls_index}]:", ls.level_sizes())


            # Increase crossings “smartly”.
            ls.new_level()
            for lvl in (ls.iter_level(start - 2), ls.iter_level(start - 1)):
                for k in lvl:
                    for _ in detour_generator(k):
                        ls.add(canonical(_))

            if _DEBUG_RED: print(f"Depth {depth_index} (after detour) [{ls_index}]:", ls.level_sizes())

            starts[ls_index] = ls.number_of_levels()

            # Explore the new space and reduce the diagrams.
            from knotpy.reidemeister.space import crossing_preserving_space, crossing_decreasing_space

            ls.new_level()
            ls.extend(crossing_preserving_space(ls.iter_level(-2), assume_canonical=True))  # may be empty if R3 not allowed

            if _DEBUG_RED: print(f"Depth {depth_index} (after preserving) [{ls_index}]:", ls.level_sizes())

            while True:
                if greediness == 0:
                    ls.new_level(crossing_decreasing_space(ls.iter_level(-1), assume_canonical=True))

                    if _DEBUG_RED: print(f"Depth {depth_index} (after decreasing, greed={greediness}) [{ls_index}]:", ls.level_sizes())


                elif greediness == 1:
                    # The following loop was empirically much faster (≈16×) in practice.
                    while not ls.is_level_empty(-1):
                        ls.new_level()  # put reduced diagrams to the next level
                        ls.extend(canonical(set(reidemeister_decreasing_moves_generator(ls.iter_level(-2)))))

                        if _DEBUG_RED: print(f"Depth {depth_index} (after decreasing, greed={greediness}) [{ls_index}]", ls.level_sizes())

                else:
                    raise ValueError(f"Invalid greediness level {greediness}.")

                if flype:
                    ls.new_level(canonical(flype_generator(ls.iter_level(-1))))
                    ls.new_level(crossing_preserving_space(ls.iter_level(-2), assume_canonical=True))
                    ls.extend(crossing_preserving_space(ls.iter_level(-2), assume_canonical=True))
                else:
                    ls.new_level(crossing_preserving_space(ls.iter_level(-1), assume_canonical=True))

                if _DEBUG_RED: print(f"Depth {depth_index} (after flype) [{ls_index}]", ls.level_sizes())

                if ls.is_level_empty(-1):
                    break

            # # If there are no crossings to reduce, we are done.
            # if any(_.number_of_crossings == 0 for _ in ls):
            #     settings.load(settings_dump)
            #     return min(ls)
            if _DEBUG_RED: ls_index += 1

        join_if_equivalent_diagrams()

    settings.load(settings_dump)

    # for depth_index in range(depth):
    #     # make Reidemeister moves (one depth-level)
    #     for key, ls in leveled_sets.items():
    #         # only make additional Reidemeister moves if any were found at a previous level
    #         if all(_.number_of_crossings != 0 for _ in ls):
    #             # increase number of crossings in a "smart" way
    #             ls.new_level(detour_space(ls.iter_level(-1), assume_canonical=True))
    #             # then do non-increasing exploration
    #             ls.new_level(crossing_non_increasing_space(ls.iter_level(-1), greediness=1, assume_canonical=True))
    #
    #     join_if_equivalent_diagrams()

    DSU_dict = DSU.to_dict()
    # print("keys", DSU_dict.keys())
    # print("keys", DSU_dict.values())


    # reconstruct the return dictionary
    keys = [from_condensed_em_notation(_) for _ in DSU_dict.keys()]
    values = [{from_condensed_em_notation(_) for _ in value} for value in DSU_dict.values()]

    result = {k if not v else min(k, min(v)): v for k, v in zip(keys, values)}

    return result
