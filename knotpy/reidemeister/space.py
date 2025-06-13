"""
A Reidemeister space of a specific type is the set of all diagrams after performing all sequences of all possible
move types.
For example, _reidemeister_3_space returns the set of all unique knots that are the result of all possible R3 moves
performed any number of times.
"""

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.canonical import canonical
from knotpy.reidemeister.reidemeister_1 import find_reidemeister_1_remove_kink, reidemeister_1_remove_kink, choose_reidemeister_1_remove_kink, reidemeister_1_add_kink, find_reidemeister_1_add_kink
from knotpy.reidemeister.reidemeister_2 import find_reidemeister_2_unpoke, reidemeister_2_unpoke, choose_reidemeister_2_unpoke, find_reidemeister_2_poke, reidemeister_2_poke
from knotpy.reidemeister.reidemeister_3 import reidemeister_3, find_reidemeister_3_triangle
from knotpy.reidemeister.reidemeister_4 import find_reidemeister_4_slide, reidemeister_4_slide, choose_reidemeister_4_slide
from knotpy.reidemeister.reidemeister_5 import find_reidemeister_5_untwists, reidemeister_5_untwist, choose_reidemeister_5_twist, choose_reidemeister_5_untwist, find_reidemeister_5_twists, reidemeister_5_twist
from knotpy.reidemeister.detour_move import find_detour_moves
from knotpy.reidemeister.reidemeister import make_reidemeister_move, detect_move_type
from knotpy.manipulation.attributes import clear_node_attributes
from knotpy.utils.set_utils import LeveledSet


from knotpy._settings import settings

__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


def _set(k: PlanarDiagram | OrientedPlanarDiagram | set | tuple | list, to_canonical) -> set:
    """ Put the diagram(s) into a set."""
    if isinstance(k, set):
        return {canonical(_) for _ in k} if to_canonical else k
    if isinstance(k, tuple | list):
        return {canonical(_) for _ in k} if to_canonical else set(k)
    if isinstance(k, PlanarDiagram | OrientedPlanarDiagram):
        return {canonical(k)} if to_canonical else {k}

    return set()


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


def reidemeister_3_space(diagrams, assume_canonical=False, depth=None) -> set:
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

    while ls[-1]:

        if depth is not None and len(ls.levels) >= depth:
            break

        # Put new diagrams to the next level.
        ls.new_level()

        # Make all R3 moves.
        ls.extend([
            canonical(reidemeister_3(k, face, inplace=False))
            for k in ls[-2]
            for face in find_reidemeister_3_triangle(k)
            if any("_r3" not in k.nodes[ep.node].attr for ep in face)  # do not repeat R3 moves, TODO: test this
            ])

        # Also include crossing-preserving R4 slides.
        ls.extend([
            canonical(reidemeister_4_slide(k, v_pos, inplace=False))
            for k in ls[-2]
            for v_pos in find_reidemeister_4_slide(k, "constant")
            # TODO: mark R4 slides
        ])

    results = set(ls)
    # remove _r3 attributes, since they can be changed on next levels when different R3 moves are performed
    clear_node_attributes(results, "_r3")

    return results



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


    # Put input diagrams in level 0.
    ls = LeveledSet(_set(diagrams, to_canonical=not assume_canonical))

    while ls[-1]:

        # Put diagrams after removing kinks and unpokes to the next level.
        ls.new_level()

        ls.extend([
            canonical(reidemeister_1_remove_kink(k, ep, inplace=False))
            for k in ls[-2]
            for ep in find_reidemeister_1_remove_kink(k)
            ])

        ls.extend([
            canonical(reidemeister_2_unpoke(k, face, inplace=False))
            for k in ls[-2]
            for face in find_reidemeister_2_unpoke(k)
            ])

        ls.extend([
            canonical(reidemeister_4_slide(k, v_pos, inplace=False))
            for k in ls[-2]
            for v_pos in find_reidemeister_4_slide(k, "decrease")
            ])

        ls.extend([
            canonical(reidemeister_5_untwist(k, face, inplace=False))
            for k in ls[-2]
            for face in find_reidemeister_5_untwists(k)
            ])

    return set(ls)


def detour_space(diagrams, assume_canonical) -> set:
    """
    Perform all R2 increasing moves to enable an R3 move in the future.

    This function aims to prepare the input diagram(s) by performing all
    Reidemeister type 2 (R2) increasing moves that could potentially allow
    a subsequent Reidemeister type 3 (R3) move. The input can be either a
    single planar diagram or a set of planar diagrams. The function works
    on these diagrams and returns a set of canonical diagrams resulting
    from the performed moves.

    Args:
        diagrams: A planar diagram or a set of planar diagrams to perform
            the detour space computation on.
        assume_canonical:

    Returns:
        set: A set of canonical diagrams after performing R2 increasing moves.
    """
    # TODO: test
    # TODO: make only increasing moves at double over- or double -under arcs

    # always assume we have a set of equivalent diagrams
    diagrams = _set(diagrams, to_canonical=not assume_canonical)


    # we usually have diagrams into a set, so do not waste time computing hashes and putting into a set
    # if not isinstance(diagrams, set):
    #     diagrams = set(diagrams)

    return {
            canonical(make_reidemeister_move(k, location, inplace=False))
            for k in diagrams
            for location in find_detour_moves(k)
        }


def crossing_non_increasing_space(diagrams, assume_canonical: bool) -> set:
    """
    Return the non-increasing "Reidemeister space" of a given set of diagrams.
    This process transforms the input diagrams iteratively by applying Reidemeister
    moves 3 and crossing reducing Reidemeister 1 and 2 moves until there are no more
    unique diagrams left. The function returns a set of all unique diagrams obtained
    during this process.

    Args:
        diagrams: A single instance of `PlanarDiagram` or a set/iterable of
            `PlanarDiagram` objects to process.
        assume_canonical: A boolean flag indicating whether the input diagrams
            are already in canonical form. If `False`, the diagrams are converted
            to canonical form prior to processing. Defaults to `False`.

    Returns:
        set: A set of diagrams in the non-increasing Reidemeister space.
    """

    diagrams = _set(diagrams, to_canonical=not assume_canonical)

    # TODO: test if R3 is not allowed, that r3space also stores the input diagrams.
    ls = LeveledSet(reidemeister_3_space(diagrams, assume_canonical=assume_canonical))

    while True:

        ls.new_level(crossing_decreasing_space(ls[-1], assume_canonical=True))
        if not ls[-1]:
            break

        # TODO: test if R3 is not allowed, that r3space also stores the input diagrams.
        ls.new_level(reidemeister_3_space(ls[-1], assume_canonical=True))

        # TODO: include FLIPS, FLYPES

        if not ls[-1]:
            break

    return set(ls)


def _filter_minimal_diagrams(diagrams):
    """ From the set of diagrams, return only the ones with minimal number of nodes."""
    minimal_number_of_nodes = min(len(_) for _ in diagrams)
    return {_ for _ in diagrams if len(_) == minimal_number_of_nodes}


def crossing_non_increasing_space_greedy(diagrams) -> set:
    """
    Return the non-increasing "Reidemeister space" of a given set of diagrams.
    This process transforms the input diagrams iteratively by applying Reidemeister
    moves 3 and crossing reducing Reidemeister 1 and 2 moves until there are no more
    unique diagrams left. The function returns a set of all unique diagrams obtained
    during this process.

    Args:
        diagrams: A single instance of `PlanarDiagram` or a set/iterable of
            `PlanarDiagram` objects to process.
        assume_canonical: A boolean flag indicating whether the input diagrams
            are already in canonical form. If `False`, the diagrams are converted
            to canonical form prior to processing. Defaults to `False`.

    Returns:
        set: A set of diagrams in the non-increasing Reidemeister space.
    """

    # TODO: THIS WAS NOT CHECKED

    # we perform R3 moves, then decreasing moves, then R3,... but we only keep the minimal diagrams after the reducing step

    if isinstance(diagrams, PlanarDiagram):
        diagrams = {diagrams, }

    ls = LeveledSet(_filter_minimal_diagrams(diagrams))

    while ls[-1]:

        if "R3" in settings.allowed_moves:
            diagrams = reidemeister_3_space(ls[-1], assume_canonical=True, depth=1)
        else:
            diagrams = ls[-1]

        diagrams = _simplify_greedy_decreasing(diagrams, to_canonical=True,inplace=True)
        diagrams = _filter_minimal_diagrams(diagrams)
        ls.new_level(diagrams)

    return _filter_minimal_diagrams(set(ls))



def all_reidemeister_moves_space(k, depth=1):
    """ Make all possible Reidemeister moves on a diagram."""

    # TODO: we can make a brute-force algorithm with this.

    ls = LeveledSet([k.copy()])

    for _depth in range(depth):
        ls.new_level()

        ls.extend([canonical(reidemeister_1_remove_kink(k, loc, inplace=False)) for k in ls[-2] for loc in find_reidemeister_1_remove_kink(k)])
        ls.extend([canonical(reidemeister_1_add_kink(k, loc, inplace=False)) for k in ls[-2] for loc in find_reidemeister_1_add_kink(k)])

        ls.extend([canonical(reidemeister_2_unpoke(k, loc, inplace=False)) for k in ls[-2] for loc in find_reidemeister_2_unpoke(k)])
        ls.extend([canonical(reidemeister_2_poke(k, loc, inplace=False)) for k in ls[-2] for loc in find_reidemeister_2_poke(k)])

        ls.extend([canonical(reidemeister_3(k, loc, inplace=False)) for k in ls[-2] for loc in find_reidemeister_3_triangle(k)])

        ls.extend([canonical(reidemeister_4_slide(k, loc, inplace=False)) for k in ls[-2] for loc in find_reidemeister_4_slide(k)])

        ls.extend([canonical(reidemeister_5_untwist(k, loc, inplace=False)) for k in ls[-2] for loc in find_reidemeister_5_untwists(k)])
        ls.extend([canonical(reidemeister_5_twist(k, loc, inplace=False)) for k in ls[-2] for loc in find_reidemeister_5_twists(k)])

        # TODO: FLIPS, FLYPES

    return set(ls)