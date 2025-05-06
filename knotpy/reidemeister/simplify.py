from concurrent.futures import ProcessPoolExecutor
from typing import List, Set
from functools import partial
import re

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

__all__ = ['simplify', 'simplify_crossing_reducing', 'simplify_smart', 'simplify_brute_force', 'simplify_non_increasing', 'simplify_non_increasing_greedy']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


_METHOD_NON_INCREASING = ("nonincreasing","noninc","ni")
_METHOD_NON_INCREASING_GREEDY = ("nonincreasinggreedy","greedynonincreasing","nonincgreedy","greedynoninc","gni","nig")
_METHOD_SMART = ("auto","smart")
_METHOD_BRUTE_FORCE = ("bf","brute","bruteforce","force")
_METHOD_DECREASING = ("decreasing","reducing", "crossingreducing", "cr")





def simplify_crossing_reducing(k: PlanarDiagram, inplace=False, allowed_moves=None):
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
    allowed_moves = _clean_allowed_moves(allowed_moves)

    if allowed_moves is not None and "FLIP" in allowed_moves:
        pass  # we are just reducing moves, ignore flip

    return reduce_crossings_greedy(k, inplace=inplace, allowed_moves=allowed_moves)



def simplify_non_increasing(k:PlanarDiagram, show_progress=False, allowed_moves=None):
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
    allowed_moves = _clean_allowed_moves(allowed_moves)

    if isinstance(k, (set, tuple, list)):
        return type(k)(simplify_non_increasing(_, allowed_moves=allowed_moves) for _ in k)

    if allowed_moves is not None and "FLIP" in allowed_moves:
        k = {k, flip(k, inplace=False)}

    return min(crossing_non_increasing_space(k, show_progress=show_progress, allowed_moves=allowed_moves))

    #
    # # Put simplified diagrams in canonical form into level 0
    # #ls = LeveledSet(canonical(simplify_crossing_reducing(k, inplace=False)))
    # ls = LeveledSet()
    #
    # while ls[-1]:
    #     ls.new_level(reidemeister_3_space(ls[-1]))  # add all possible R3 moves
    #     ls.new_level(simplify_non_increasing(ls[-1]))  # add all possible reductions
    # return min(ls)

def simplify_non_increasing_greedy(k:PlanarDiagram, show_progress=False, allowed_moves=None):
    """
    Simplifies a planar diagram by attempting possible Reidemeister Type-3 (R3) moves, followed by crossing-reducing
    moves, iteratively. At each level only take the diagrams with the lowest number of crossings.
    Args:
        k (PlanarDiagram): The planar diagram to be simplified.

    Returns:
        PlanarDiagram: The simplified diagram if simplifications were successful, otherwise returns the input diagram.
    """
    allowed_moves = _clean_allowed_moves(allowed_moves)

    if isinstance(k, (set, tuple, list)):
        return type(k)(simplify_non_increasing_greedy(_, show_progress, allowed_moves=allowed_moves) for _ in k)

    if allowed_moves is not None and "FLIP" in allowed_moves:
        k = {k, flip(k, inplace=False)}

    return min(crossing_non_increasing_space_greedy(k, show_progress=show_progress, allowed_moves=allowed_moves))

def simplify_brute_force(k: PlanarDiagram, depth: int, allowed_moves=None):
    """
    Simplify a given PlanarDiagram through all possible Reidemeister moves
    up to a specified recursion depth and return the minimum result.

    Args:
        k (PlanarDiagram): The planar diagram object representing a knot or link
            to be simplified.
        depth (int): The maximum recursion depth for applying Reidemeister moves.

    Returns:
        PlanarDiagram: The simplest version of the planar diagram obtained
            using the applied Reidemeister moves.
    """
    allowed_moves = _clean_allowed_moves(allowed_moves)

    if allowed_moves is not None and "FLIP" in allowed_moves:
        pass

    raise NotImplementedError("Not implemented yet.")


def simplify_smart(k: PlanarDiagram, depth=1, allowed_moves=None):
    """ Make "smart" Reidemeister moves:

    :param k:
    :param depth:
    :return:
    """
    allowed_moves = _clean_allowed_moves(allowed_moves)

    if isinstance(k, (set, list, tuple)):
        return [simplify_smart(_, depth, allowed_moves=allowed_moves) for _ in k]

    if not k:
        return set()

    if allowed_moves is not None and "FLIP" in allowed_moves:
        k = {k, flip(k, inplace=False)}

    # Level 0: perform all R3 and crossing reducing R2 and R1 moves.
    ls = LeveledSet(crossing_non_increasing_space(k, assume_canonical=False, allowed_moves=allowed_moves))

    # If there are no crossings to reduce, we are done.
    if any(_.number_of_crossings == 0 for _ in ls):
        return min(ls)

    #print(len(ls.levels),":", len(ls[-1]))

    """
    For all next levels, increase the number of crossings by 1 or 2 (via R1 and R2 moves),
    followed by all possible R3 moves and crossing-reducing R1 and R2 moves.
    """
    for depth_index in range(depth):
        ls.new_level(detour_space(ls[-1]))
        #print(len(ls.levels), ":", len(ls[-1]))
        ls.new_level(crossing_non_increasing_space(ls[-1], allowed_moves=allowed_moves))
        #print(len(ls.levels), ":", len(ls[-1]))

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


def simplify(k: PlanarDiagram, method: str = "auto", depth: int = 1, allowed_moves=None):
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
    allowed_moves = _clean_allowed_moves(allowed_moves)

    method = ''.join(c for c in method if c.isalpha()).lower()  # remove any hyphens/dashes

    if method in _METHOD_SMART:
        return simplify_smart(k, depth, allowed_moves=allowed_moves)
    elif method in _METHOD_BRUTE_FORCE:
         return simplify_brute_force(k, depth, allowed_moves=allowed_moves)
    elif method in _METHOD_NON_INCREASING:
        return simplify_non_increasing(k, allowed_moves=allowed_moves)
    elif method in _METHOD_NON_INCREASING_GREEDY:
        return simplify_non_increasing_greedy(k, allowed_moves=allowed_moves)
    elif method in _METHOD_DECREASING:
        return simplify_crossing_reducing(k, allowed_moves=allowed_moves)
    else:
        raise ValueError("Invalid method. Choose one of 'auto', 'non-increasing', or 'decreasing'.")


