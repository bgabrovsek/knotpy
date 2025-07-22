
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.canonical import canonical
from knotpy.utils.set_utils import LeveledSet
from knotpy.reidemeister.space import _simplify_greedy_decreasing, crossing_non_increasing_space, detour_space
from knotpy.reidemeister.reidemeister import reidemeister_preserving_moves_generator, detour_generator, reidemeister_decreasing_moves_generator
from knotpy.manipulation.symmetry import flip
from knotpy._settings import settings

__all__ = ["simplify_decreasing", "simplify_smart", "simplify_non_increasing"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

def simplify_decreasing(k: PlanarDiagram, inplace=False):
    """
    Simplify a planar diagram by applying a (non-random) sequence of crossing-decreasing Reidemeister moves
    (R1, R2, R4, R5), until there are no more such moves left. The algorithm is greedy, it performs the
    first crossing-reducing move it finds and continues to do so until there are no more such moves left.

    Args:
        k (PlanarDiagram): The planar diagram to be simplified.
        inplace (bool): Whether to simplify the given diagram in-place. If
            `True`, the input diagram `k` will be modified directly. If `False`,
            the function will create a copy of `k` and perform simplifications
            on it. Defaults to `False`.

    Returns:
        PlanarDiagram: The simplified planar diagram with possibly reduced crossings.
    """


    return _simplify_greedy_decreasing(k, to_canonical=False, inplace=inplace)



def simplify_non_increasing(k:PlanarDiagram, greediness:int = 1):
    """
    Simplifies a planar diagram through Reidemeister R3 moves and crossing-decreasing
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
          level.
        - Level 3: Similar to level 2, except that it returns a diagram immediately
          after it reduces it (does not rerun the loop to check additional R3 moves).

    The method does not perform crossing-increasing Reidemeister moves.

    Args:
        k (PlanarDiagram): The planar diagram to simplify.
        greediness (int): Specifies the level of aggressiveness for simplification.
            Default is 1.

    Returns:
        PlanarDiagram: The simplified planar diagram, or the original diagram if no
        simplifications were applied.
    """

    if isinstance(k, (set, tuple, list)):
        return type(k)(simplify_non_increasing(_) for _ in k)

    if greediness == 0 or greediness == 1:
        if "FLIP" in settings.allowed_moves:
            k = {k, flip(k, inplace=False)}

        return min(crossing_non_increasing_space(k, greediness=greediness, assume_canonical=False))

    elif greediness == 2:
        raise NotImplementedError("Not implemented yet.")

    elif greediness == 3:
        k = k.copy()
        number_of_nodes = len(k)

        # First, try to decrease crossing directly.
        simplify_decreasing(k, inplace=True)
        if len(k) < number_of_nodes:
            return k

        # Second, make crossing preserving moves until there are crossings to remove
        ls = LeveledSet(canonical(k))
        while not ls.is_level_empty(-1):
            ls.new_level()
            for _ in reidemeister_preserving_moves_generator(ls.iter_level(-2)):
                __ = simplify_decreasing(_, inplace=True)
                if len(__) < number_of_nodes:
                    return __
                else:
                    ls.add(canonical(__))

        return ls.levels[0].pop()

    else:
        raise ValueError(f"Invalid greediness level {greediness}.")


def simplify_smart(k: PlanarDiagram, depth=1, greediness=1):
    """ Make "smart" Reidemeister moves to simplify a diagram. "Smart" moves refer to this process at each step:

    - perform all non-increasing moves (R3, decreasing R1 and R2,...) any number of times, until the set of obtained
    diagrams stabalizes (no new diagrams are generated with R3, R1, R2, ... moves),
    - perform all crossing-increasing moves once (increasing R1, R2, and possibly R5), in such a way that at the next
    step a new R3 move can be performed.

    :param k: Input diagram.
    :param depth: How many times crossing increasing moves should be performed.
    :return: The minimal diagram after the above process is applied.
    """

    # If multiple diagrams are given, perform steps on each diagram.
    if isinstance(k, (set, list, tuple)):
        return [simplify_smart(_, depth) for _ in k]

    if not k:
        return []

    #k = {canonical(k),}
    k = {canonical(k), canonical(simplify_decreasing(k, inplace=True))}

    # If we allow flipping the diagram, flip it.
    if "FLIP" in settings.allowed_moves:
        k |= {canonical(flip(_, inplace=False)) for _ in k}

    if any(_.number_of_crossings == 0 for _ in k):
        return min(k)

    # Level 0: perform all R3 and crossing reducing R2, R1, R4, and R5 moves.
    # TODO: if we take greediness=0, then it takes much longer
    ls = LeveledSet(crossing_non_increasing_space(k, greediness=0, assume_canonical=True))

    # If there are no crossings to reduce, we are done.
    if any(_.number_of_crossings == 0 for _ in ls):
        return min(ls)


    """
    For all next levels, increase the number of crossings by 1 or 2 (via R1 and R2 moves),
    followed by all possible R3 moves and crossing-reducing R1 and R2 moves.
    """
    start = len(ls.levels)
    for depth_index in range(depth):

        # increase crossings
        #ls.new_level(detour_space(ls.levels[-1], assume_canonical=True))
        ls.new_level()
        for lvl in ls.levels[start-1:-1]:
            for k in lvl:
                for _ in detour_generator(k):
                    ls.add(canonical(_))

        start = len(ls.levels)

        # explore the new space and reduce the diagrams
        #ls.new_level(crossing_non_increasing_space(ls[-1], greediness=0, assume_canonical=True))
        from knotpy.reidemeister.space import crossing_preserving_space, crossing_decreasing_space
        ls.new_level()
        ls.extend(crossing_preserving_space(ls.iter_level(-2), assume_canonical=True))  # TODO: if R3 not allowed, does preserving contain the input diagram?
        while True:

            #ls.new_level(crossing_decreasing_space(ls[-1], assume_canonical=True))

            # TODO after adding the bottom three line, it works much faster (16x), but I do not know why
            if greediness == 0:
                ls.new_level(crossing_decreasing_space(ls.iter_level(-1), assume_canonical=True))
            elif greediness == 1:
                while not ls.is_level_empty(-1):
                    ls.new_level()  # put reduced diagrams to the next level
                    ls.extend(canonical(set(reidemeister_decreasing_moves_generator(ls.iter_level(-2)))))
            else:
                raise ValueError(f"Invalid greediness level {greediness}.")


            ls.new_level(crossing_preserving_space(ls.iter_level(-1), assume_canonical=True))  # TODO: if R3 not allowed, do we get ls[-1]?
            if ls.is_level_empty(-1):
                break

        # If there are no crossings to reduce, we are done.
        if any(_.number_of_crossings == 0 for _ in ls):
            return min(ls)

    return min(ls)



# def _old_simplify_smart(k: PlanarDiagram, depth=1):
#     """ Make "smart" Reidemeister moves to simplify a diagram. "Smart" moves refer to this process at each step:
#
#     - perform all non-increasing moves (R3, decreasing R1 and R2,...) any number of times, until the set of obtained
#     diagrams stabalizes (no new diagrams are generated with R3, R1, R2, ... moves),
#     - perform all crossing-increasing moves once (increasing R1, R2, and possibly R5), in such a way that at the next
#     step a new R3 move can be performed.
#
#     :param k: Input diagram.
#     :param depth: How many times crossing increasing moves should be performed.
#     :return: The minimal diagram after the above process is applied.
#     """
#
#     # If multiple diagrams are given, perform steps on each diagram.
#     if isinstance(k, (set, list, tuple)):
#         return [simplify_smart(_, depth) for _ in k]
#
#     if not k:
#         return []
#
#     k = canonical(k)
#     # If we allow flipping the diagram, flip it.
#     if "FLIP" in settings.allowed_moves:
#         k = {k, canonical(flip(k, inplace=False))}
#
#     # Level 0: perform all R3 and crossing reducing R2, R1, R4, and R5 moves.
#     ls = LeveledSet(crossing_non_increasing_space(k, greediness=0, assume_canonical=False))
#
#     # If there are no crossings to reduce, we are done.
#     if any(_.number_of_crossings == 0 for _ in ls):
#         return min(ls)
#
#     """
#     For all next levels, increase the number of crossings by 1 or 2 (via R1 and R2 moves),
#     followed by all possible R3 moves and crossing-reducing R1 and R2 moves.
#     """
#     for depth_index in range(depth):
#
#         # increase crossings
#         ls.new_level(detour_space(ls[-1], assume_canonical=True))
#
#         # explore the new space and reduce the diagrams
#         ls.new_level(crossing_non_increasing_space(ls[-1], greediness=0, assume_canonical=True))
#
#         # If there are no crossings to reduce, we are done.
#         if any(_.number_of_crossings == 0 for _ in ls):
#             #print("levels!:", [len(c) for c in ls.levels])
#             return min(ls)
#
#     #print("levels :", [len(c) for c in ls.levels])
#     return min(ls)
#
