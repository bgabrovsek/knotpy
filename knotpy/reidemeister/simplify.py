
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.freezing import freeze, unfreeze
from knotpy.algorithms.canonical import canonical
from knotpy.utils.set_utils import LeveledSet
from knotpy.reidemeister.space import reidemeister_3_space, detour_space, crossing_non_increasing_space, \
    reduce_crossings_greedy, crossing_non_increasing_space_greedy
from knotpy.reidemeister.reidemeister_3 import reidemeister_3, find_reidemeister_3_triangle
from knotpy.manipulation.symmetry import flip
from knotpy._settings import settings

__all__ = ['simplify', 'simplify_crossing_reducing', 'simplify_smart', 'simplify_non_increasing', 'simplify_non_increasing_greedy', 'fast_simplification_greedy']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


_METHOD_NON_INCREASING = ("nonincreasing","noninc","ni")
_METHOD_NON_INCREASING_GREEDY = ("nonincreasinggreedy","greedynonincreasing","nonincgreedy","greedynoninc","gni","nig")
_METHOD_SMART = ("auto","smart")
#_METHOD_BRUTE_FORCE = ("bf","brute","bruteforce","force")
_METHOD_DECREASING = ("decreasing","reducing", "crossingreducing", "cr")



def simplify_crossing_reducing(k: PlanarDiagram, inplace=False):
    """
    Simplify a planar diagram by applying a (non-random) sequence of crossing-reducing Reidemeister moves
    (remove R1 kinks and R2 unpokes), until there are no more such moves left.

    Args:
        k (PlanarDiagram): The planar diagram representing the knot, which will
            be simplified by applying Reidemeister moves.
        inplace (bool): Whether to simplify the given diagram in-place. If
            `True`, the input diagram `k` will be modified directly. If `False`,
            the function will create a copy of `k` and perform simplifications
            on it. Defaults to `False`.

    Returns:
        PlanarDiagram: The simplified planar diagram with reduced crossings,
        either modified in-place or as a new object if `inplace` is `False`.
    """

    #print("reducing", k)

    if "FLIP" in settings.allowed_moves:
        pass  # we are just reducing moves, ignore flip

    return reduce_crossings_greedy(k, inplace=inplace)



def simplify_non_increasing(k:PlanarDiagram):
    """
    Simplifies a planar diagram by attempting all possible Reidemeister Type-3 (R3) moves, followed by crossing-reducing
    moves, iteratively. The simplification process halts when no new diagrams are generated during the process.
    We do not perform any crossing-increasing Reidemeiser moves.
    Args:
        k (PlanarDiagram): The planar diagram to be simplified.
        inplace (bool):

    Returns:
        PlanarDiagram: The simplified diagram if simplifications were successful, otherwise returns the input diagram.
    """

    if isinstance(k, (set, tuple, list)):
        return type(k)(simplify_non_increasing(_) for _ in k)

    if "FLIP" in settings.allowed_moves:
        k = {k, flip(k, inplace=False)}

    return min(crossing_non_increasing_space(k))

    #
    # # Put simplified diagrams in canonical form into level 0
    # #ls = LeveledSet(canonical(simplify_crossing_reducing(k, inplace=False)))
    # ls = LeveledSet()
    #
    # while ls[-1]:
    #     ls.new_level(reidemeister_3_space(ls[-1]))  # add all possible R3 moves
    #     ls.new_level(simplify_non_increasing(ls[-1]))  # add all possible reductions
    # return min(ls)


def simplify_non_increasing_greedy(k:PlanarDiagram):
    """
    Simplifies a planar diagram by attempting possible Reidemeister Type-3 (R3) moves, followed by crossing-reducing
    moves, iteratively. At each level only take the diagrams with the lowest number of crossings.
    Args:
        k (PlanarDiagram): The planar diagram to be simplified.

    Returns:
        PlanarDiagram: The simplified diagram if simplifications were successful, otherwise returns the input diagram.
    """

    if isinstance(k, (set, tuple, list)):
        return type(k)(simplify_non_increasing_greedy(_) for _ in k)

    if "FLIP" in settings.allowed_moves:
        k = {k, flip(k, inplace=False)}

    return min(crossing_non_increasing_space_greedy(k))


# def simplify_brute_force(k: PlanarDiagram, depth: int):
#     """
#     Simplify a given PlanarDiagram through all possible Reidemeister moves
#     up to a specified recursion depth and return the minimum result.
#
#     Args:
#         k (PlanarDiagram): The planar diagram object representing a knot or link
#             to be simplified.
#         depth (int): The maximum recursion depth for applying Reidemeister moves.
#
#     Returns:
#         PlanarDiagram: The simplest version of the planar diagram obtained
#             using the applied Reidemeister moves.
#     """
#
#     if "FLIP" in settings.allowed_moves:
#         pass
#
#     raise NotImplementedError("Not implemented yet.")


def simplify_smart(k: PlanarDiagram, depth=1):
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

    k = canonical(k)
    # If we allow flipping the diagram, flip it.
    if "FLIP" in settings.allowed_moves:
        k = {k, canonical(flip(k, inplace=False))}

    # Level 0: perform all R3 and crossing reducing R2, R1, R4, and R5 moves.
    ls = LeveledSet(crossing_non_increasing_space(k, assume_canonical=False,))

    # If there are no crossings to reduce, we are done.
    if any(_.number_of_crossings == 0 for _ in ls):
        return min(ls)

    """
    For all next levels, increase the number of crossings by 1 or 2 (via R1 and R2 moves),
    followed by all possible R3 moves and crossing-reducing R1 and R2 moves.
    """
    for depth_index in range(depth):

        # increase crossings
        ls.new_level(detour_space(ls[-1]))

        # explore the new space and reduce the diagrams
        ls.new_level(crossing_non_increasing_space(ls[-1]))

        # If there are no crossings to reduce, we are done.
        if any(_.number_of_crossings == 0 for _ in ls):
            return min(ls)

    return min(ls)
    #
    # # level 0: original diagrams (reduced in canonical form)
    # ls = LeveledSet(canonical(simplify_crossing_reducing(k)))
    #
    # # level 1: add R3 moves to the diagrams and simplify
    # ls.new_level(batch_crossing_reducing_simplify(reidemeister_3_space(ls[-1])))
    # # TODO: Choice: should we simplify after R3 moves?
    #
    # for depth_index in range(depth):
    #     # make all increasing R2 moves (that form 3-regions) TODO: test
    #     ls.new_level(detour_space(ls[-1]))
    #     # make all r3 moves
    #     ls.new_level(batch_crossing_reducing_simplify(reidemeister_3_space(ls[-1])))
    #
    # return min(ls)


def simplify(k: PlanarDiagram, method: str = "auto", depth: int = 1):
    """
    Simplifies a planar diagram using Reidemeister moves.

    :param k: The input planar diagram.
    :type k: PlanarDiagram
    :param method: The simplification method to use. Options are:
                   "auto" - Uses simplify_smart,
                   "non-increasing" - Uses simplify_non_increasing,
                   "decreasing" - Uses simlify_decresing.
    :type method: str
    :param depth: The depth parameter for the simplification process.
    :type depth: int
    :return: The simplified planar diagram.
    :rtype: PlanarDiagram
    :raises ValueError: If the method is not recognized.
    """

    method = ''.join(c for c in method if c.isalpha()).lower()  # remove any hyphens/dashes

    if method in _METHOD_SMART:
        return simplify_smart(k, depth)
    # elif method in _METHOD_BRUTE_FORCE:
    #      return simplify_brute_force(k, depth)
    elif method in _METHOD_NON_INCREASING:
        return simplify_non_increasing(k)
    elif method in _METHOD_NON_INCREASING_GREEDY:
        return simplify_non_increasing_greedy(k)
    elif method in _METHOD_DECREASING:
        return simplify_crossing_reducing(k)
    else:
        raise ValueError("Invalid method. Choose one of 'auto', 'non-increasing', or 'decreasing'.")


def fast_simplification_greedy(k: PlanarDiagram):
    """
    Perform R3 until no more R3 moves are possible or crossings can be reduced.
    Returns a simplified diagram as soon as there are possible simplifications to be made
    """

    # TODO: also use R5 moves

    k = k.copy()

    # try to reduce the input diagram
    number_of_nodes = len(k)
    reduce_crossings_greedy(k, inplace=True)
    if len(k) < number_of_nodes:
        return k

    # if R3 moves are not allowed, we cannot do further simplifications
    if "R3" not in settings.allowed_moves:
        return k

    ls =LeveledSet(freeze(canonical(k)))

    while ls[-1]:
        # Put diagrams after an R3 to the next level.
        ls.new_level()

        for k in ls[-2]:
            for location in find_reidemeister_3_triangle(k):
                k_r3 = reidemeister_3(k, location, inplace=False)
                reduce_crossings_greedy(k_r3, inplace=True)
                if len(k_r3) < len(k):
                    return k_r3
                ls.add(freeze(canonical(k_r3)))

    return unfreeze(ls[0].pop())
