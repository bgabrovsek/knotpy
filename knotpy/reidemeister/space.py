"""
A Reidemeister space of a specific type is the set of all diagrams after performing all sequences of all possible
move types.
For example, _reidemeister_3_space returns the set of all unique knots that are the result of all possible R3 moves
performed any number of times.
"""
from collections.abc import Iterable
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.canonical import canonical
from knotpy.manipulation.attributes import clear_node_attributes
from knotpy.utils.set_utils import LeveledSet
from knotpy._settings import settings

from knotpy.reidemeister.reidemeister import (reidemeister_preserving_moves_generator,
                                              reidemeister_decreasing_moves_generator,
                                              detour_generator, reidemeister_moves_generator)
from knotpy.reidemeister.reidemeister_1 import choose_reidemeister_1_remove_kink, reidemeister_1_remove_kink
from knotpy.reidemeister.reidemeister_2 import choose_reidemeister_2_unpoke, reidemeister_2_unpoke
from knotpy.reidemeister.reidemeister_4 import choose_reidemeister_4_slide, reidemeister_4_slide
from knotpy.reidemeister.reidemeister_5 import choose_reidemeister_5_untwist, reidemeister_5_untwist

__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

# TODO: freezing

def _set(k: PlanarDiagram | OrientedPlanarDiagram | set | tuple | list | Iterable, to_canonical) -> set:
    """ Put the diagram(s) into a set."""
    if isinstance(k, set):
        return {canonical(_) for _ in k} if to_canonical else k
    if isinstance(k, tuple | list | Iterable):
        return {canonical(_) for _ in k} if to_canonical else set(k)
    if isinstance(k, PlanarDiagram | OrientedPlanarDiagram):
        return {canonical(k)} if to_canonical else {k}

    raise TypeError("k must be a PlanarDiagram, OrientedPlanarDiagram, set, tuple or list")


def _filter_minimal_diagrams(diagrams):
    """ From the set of diagrams, return only the ones with minimal number of nodes."""
    if not diagrams:
        return set()
    minimal_number_of_nodes = min(len(_) for _ in diagrams)
    return {_ for _ in diagrams if len(_) == minimal_number_of_nodes}


# OK
def _simplify_greedy_decreasing(k: PlanarDiagram | OrientedPlanarDiagram | set | tuple | list, to_canonical: bool, inplace: bool=False) -> PlanarDiagram | OrientedPlanarDiagram | set | tuple | list:
    """
    Simplify a planar diagram by applying a (non-random) sequence of crossing-reducing Reidemeister moves
    (R2, R1, and possibly R4 and R5), until there are no more such moves left.

    Args:
        k (PlanarDiagram): The planar diagram to be simplified, if a set/list/tuple is given,
        the function returns a set/list/tuple of simplified diagrams.
        to_canonical (bool): If `True`, return the simplified diagram in canonical form.
        inplace (bool): Indicates whether modifications should be performed on the input diagram `k` itself or a new copy.

    Returns:
        PlanarDiagram: A possibly simplified version of the input planar diagram.
    """

    # If a list is given, simplify each element separately.
    if isinstance(k, (set, tuple, list)):
        return type(k)(_simplify_greedy_decreasing(_, to_canonical=to_canonical, inplace=inplace) for _ in k)

    if not inplace:
        k = k.copy()

    while True:
        # No need to check allowed moves, since this is checked in the choose-function.

        if face := choose_reidemeister_2_unpoke(k, random=False):
            reidemeister_2_unpoke(k, face, inplace=True)
            continue

        if ep := choose_reidemeister_1_remove_kink(k, random=False):
            reidemeister_1_remove_kink(k, ep, inplace=True)
            continue

        if face := choose_reidemeister_5_untwist(k, random=False):
            reidemeister_5_untwist(k, face, inplace=True)
            continue

        if vert_pos := choose_reidemeister_4_slide(k, change="decreasing", random=False):
            reidemeister_4_slide(k, vert_pos, inplace=True)
            continue

        break

    return canonical(k) if to_canonical else k

# OK
def crossing_decreasing_space(diagrams: PlanarDiagram | set | list, assume_canonical) -> set:
    """
    Remove the crossings in a set of planar diagrams using Reidemeister I and
    Reidemeister II moves and return all possible reduced diagrams.

    This function applies Reidemeister moves to reduce minimize the crossings in planar diagrams. Given one or more
    diagrams, it returns a set of transformed diagrams with reduced crossings, ensuring that all diagrams are in their
    canonical form. It returns all possible reduced diagrams in all steps of the reduction process.
    This function should not be used if we are just reducing crossings, since we do not need to explore the whole
    reducing space (including also partial reducing moves).
    Args:
        diagrams (Union[PlanarDiagram, Set[PlanarDiagram]]): A single planar
            diagram or a set of planar diagrams to be processed.
        assume_canonical (bool): If `True`, assume that the input diagrams are in canonical form.

    Returns:
        set: A set of planar diagrams with reduced crossings. Each diagram is
        transformed into its canonical form during the reduction process.
    """

    ls = LeveledSet(_set(diagrams, to_canonical=not assume_canonical))  # put input diagrams in level 0
    while not ls.is_level_empty(-1):
        ls.new_level()  # put reduced diagrams to the next level
        ls.extend(canonical(set(reidemeister_decreasing_moves_generator(ls.iter_level(-2)))))
    return set(ls)

# OK
def crossing_preserving_space(diagrams, assume_canonical=False, depth=None) -> set:
    """
    Iteratively performs all possible R3 moves (and crossing-preserving R4 slides) on a given planar diagram or a set
    of planar diagrams. The function does not place input diagrams in canonical form initially but ensures that
    the output contains planar diagrams in canonical form after potential sequences of R3 moves.

    Args:
        diagrams (Union[PlanarDiagram, set[PlanarDiagram]]): A planar diagram
            or a set of planar diagrams on which R3 moves should be performed.
        assume_canonical (bool): If `True`, assume that the input diagrams are in canonical form. This saves execution
        time if we know that the input diagrams are already in canonical form.
        depth (int): The maximum number of R3 moves to perform. If `None`, perform all possible moves.

    Returns:
        set[PlanarDiagram]: A set of planar diagrams after all possible sequences of R3
            moves have been executed in canonical form.
    """

    # Put input diagrams in level 0.
    ls = LeveledSet(_set(diagrams, to_canonical=not assume_canonical))
    #print("(1.1)")

    while not ls.is_level_empty(-1):
        #print("(1.2)")
        if depth is not None and len(ls.levels) >= depth:
            break
        #print("(1.3)")

        # Put new diagrams to the next level.
        ls.new_level()
        #print("(1.4)")


        x = set(ls.levels[-2])
        s = set(reidemeister_preserving_moves_generator(x))

        #print("(1.4.1)")

        ls.extend(canonical(s))
        #print("(1.5)")

    #print("(1.6)")

    results = set(ls)
    # remove _r3 attributes, since they can be changed on next levels when different R3 moves are performed
    clear_node_attributes(results, "_r3")
    # TODO: test _r3 if we perform flypes, r1, ...

    return results

# OK
def detour_space(diagrams, assume_canonical) -> set:
    """
    Perform all R2 increasing moves that enable an R3 move in the next step. In addition, perform all R4 moves that
    increase the number of crossings.

    Args:
        diagrams: A planar diagram or a set of planar diagrams.
        assume_canonical:

    Returns:
        set: A set of canonical diagrams after performing R2 increasing moves.
    """
    # TODO: test
    # TODO: make only increasing moves at double over- or double -under arcs

    # always assume we have a set of equivalent diagrams
    diagrams = _set(diagrams, to_canonical=not assume_canonical)
    return {canonical(k) for k in detour_generator(diagrams)}


def crossing_non_increasing_space(diagrams, greediness, assume_canonical: bool) -> set:
    """
    Return the non-increasing "Reidemeister space" of a given set of diagrams.
    This process transforms the input diagrams iteratively by applying Reidemeister
    moves 3 and crossing reducing Reidemeister 1 and 2 moves until there are no more
    unique diagrams left. The function returns a set of all unique diagrams obtained
    during this process.

    Args:
        diagrams: A single instance of `PlanarDiagram` or a set/iterable of
            `PlanarDiagram` objects to process.
        greediness: level of greediness:
            - Level 0: Iteratively applies all possible R3 moves, followed by crossing-
                       decreasing moves until no further simplification is achievable. This is the lowest level.
            - Level 1: Similar to Level 0, but at each iteration step, the process only
                       continues with diagrams having the lowest number of crossings.
        assume_canonical: A boolean flag indicating whether the input diagrams
            are already in canonical form. If `False`, the diagrams are converted
            to canonical form prior to processing. Defaults to `False`.

    Returns:
        set: A set of diagrams in the non-increasing Reidemeister space.
    """

    diagrams = _set(diagrams, to_canonical=not assume_canonical)

    if greediness == 0:
        ls = LeveledSet(crossing_preserving_space(diagrams, assume_canonical=assume_canonical))  # TODO: if R3 not allowed, does preserving contain the input diagram?
        while True:

            ls.new_level(crossing_decreasing_space(ls.iter_level(-1), assume_canonical=True))
            if ls.is_level_empty(-1):
                break
            ls.new_level(crossing_preserving_space(ls.iter_level(-1), assume_canonical=True))  # TODO: if R3 not allowed, do we get ls[-1]?
            if ls.is_level_empty(-1):
                break
        return set(ls)

    elif greediness == 1:
        ls = LeveledSet(_filter_minimal_diagrams(diagrams))
        while not ls.is_level_empty(-1):
            diagrams = crossing_preserving_space(ls.iter_level(-1))
            diagrams = _simplify_greedy_decreasing(diagrams, to_canonical=True, inplace=True)
            diagrams = _filter_minimal_diagrams(diagrams)
            ls.new_level(diagrams)
        return _filter_minimal_diagrams(set(ls))

    else:
        raise ValueError("Greediness level must be 0 or 1.")


def all_reidemeister_moves_space(diagrams, depth=1, assume_canonical=False) -> set:
    """ Make all possible Reidemeister moves on a diagram."""

    diagrams = _set(diagrams, to_canonical=not assume_canonical)

    ls = LeveledSet(diagrams)

    for _depth in range(depth):
        ls.new_level([canonical(k) for k in reidemeister_moves_generator(ls.iter_level(-1))])

    return set(ls)