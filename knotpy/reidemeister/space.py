"""
A Reidemeister space is the set of all diagrams after performing all possible Reidemeister 3 moves.
For example, reidemeister_3_space returns the set of all unique knots that are the result of all possible R3 moves
performed.
"""
from knotpy.algorithms.canonical import canonical
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.reidemeister.reidemeister_1 import find_reidemeister_1_remove_kink, reidemeister_1_remove_kink
from knotpy.reidemeister.reidemeister_2 import find_reidemeister_2_unpoke, reidemeister_2_unpoke
from knotpy.reidemeister.reidemeister_3 import reidemeister_3, find_reidemeister_3_triangle
from knotpy.reidemeister.detour_move import find_detour_moves
from knotpy.reidemeister.reidemeister import make_reidemeister_move
from knotpy.manipulation.attributes import clear_node_attributes
from knotpy.utils.set_utils import LeveledSet



__all__ = ["crossing_reducing_space", "reidemeister_3_space", "detour_space", "crossing_non_increasing_space"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


def crossing_reducing_space(diagrams, assume_canonical=False) -> set:
    """
    Remove the crossings in a set of planar diagrams using Reidemeister I and
    Reidemeister II moves and return all possible reduced diagrams.

    This function applies Reidemeister moves (specifically type 1 and type 2) to
    minimize the crossings in planar diagrams. Given one or more diagrams,
    it returns a set of transformed diagrams with reduced crossings, ensuring
    that all diagrams are in their canonical form.

    Args:
        diagrams (Union[PlanarDiagram, Set[PlanarDiagram]]): A single planar
            diagram or a set of planar diagrams to be processed. Diagrams serve
            as input for the crossing reduction process.
        assume_canonical (bool): If `True`, assume that the input diagrams are in canonical form.

    Returns:
        set: A set of planar diagrams with reduced crossings. Each diagram is
        transformed into its canonical form during the reduction process.
    """

    if isinstance(diagrams, PlanarDiagram):
        diagrams = {diagrams, }

    # Put input diagrams in level 0.
    ls = LeveledSet(diagrams if assume_canonical else [canonical(k) for k in diagrams])

    while ls[-1]:
        # Put diagrams after removing kinks and unpokes to the next level.
        ls.new_level()
        ls.extend([
            canonical(reidemeister_1_remove_kink(k, ep, inplace=False))
            for k in ls[-2]
            for ep in find_reidemeister_1_remove_kink(k)
            ]
        )
        ls.extend([
            canonical(reidemeister_2_unpoke(k, face, inplace=False))
            for k in ls[-2]
            for face in find_reidemeister_2_unpoke(k)
            ]
        )

    return set(ls)


def reidemeister_3_space(diagrams, assume_canonical=False) -> set:
    """
    Iteratively performs all possible R3 moves on a given planar diagram or a set of planar diagrams.
    The function does not place input diagrams in canonical form initially but ensures that
    the output contains planar diagrams in canonical form after potential sequences of R3 moves.

    Args:
        diagrams (Union[PlanarDiagram, set[PlanarDiagram]]): A planar diagram
            or a set of planar diagrams on which R3 moves should be performed.
        assume_canonical (bool): If `True`, assume that the input diagrams are in canonical form.

    Returns:
        set[PlanarDiagram]: A set of planar diagrams after all possible sequences of R3
            moves have been executed in canonical form.
    """

    if isinstance(diagrams, PlanarDiagram):
        diagrams = {diagrams, }

    # Put input diagrams in level 0.
    ls = LeveledSet(diagrams if assume_canonical else [canonical(k) for k in diagrams])

    while ls[-1]:
        # Put diagrams after an R3 to the next level.
        ls.new_level()
        ls.extend([
            canonical(reidemeister_3(k, face, inplace=False))
            for k in ls[-2]
            for face in find_reidemeister_3_triangle(k)
            if any("_r3" not in k.nodes[ep.node].attr for ep in face)
            ]
        )


    results = set(ls)
    # remove _r3 attributes, since they can be changed on next levels when different R3 moves are performed
    clear_node_attributes(results, "_r3")

    return results


def detour_space(diagrams):
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
        assume_canonical: A boolean indicating whether the input diagram(s)
            can be assumed to be already in canonical form. Defaults to False.

    Returns:
        set: A set of canonical diagrams after performing R2 increasing moves.
    """
    # TODO: test
    # TODO: make only increasing moves at double over- or souble -under arcs

    # always assume we have a set of equivalent diagrams
    if isinstance(diagrams, PlanarDiagram):
        diagrams = {diagrams}

    # we usually have diagrams into a set, so do not waste time computing hashes and putting into a set
    # if not isinstance(diagrams, set):
    #     diagrams = set(diagrams)

    return {
        canonical(make_reidemeister_move(k, location, inplace=False))
        for k in diagrams
        for location in find_detour_moves(k)
        }


def crossing_non_increasing_space(diagrams, assume_canonical=False):
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

    if isinstance(diagrams, PlanarDiagram):
        diagrams = {diagrams, }

    if not isinstance(diagrams, set):
        diagrams = set(diagrams) if assume_canonical else {canonical(_) for _ in diagrams}
    elif not assume_canonical:
        diagrams = {canonical(_) for _ in diagrams}

    ls = LeveledSet(reidemeister_3_space(diagrams, assume_canonical=True))  # also stores inside the original diagrams

    while True:
        ls.new_level(crossing_reducing_space(ls[-1], assume_canonical=True))
        if not ls[-1]:
            break
        ls.new_level(reidemeister_3_space(ls[-1], assume_canonical=True))
        if not ls[-1]:
            break

    return set(ls)

# def smart_reidemeister_space(diagram, depth):
#     """Make depth crossing increasing moves and any number of Reidemesiter 3 moves, then returns the whole set of
#     obtained diagrams
#
#     :param diagram:
#     :param depth:
#     :return:
#     """
#     """Try to simplify the diagram k in such a way, that we perform all possible R3 moves, followed by crossing
#      decreasing moves, followed by crossing increasing moves, where the increasing moves are taken in such a way, that
#      a new non-alternating 3-gon appears. The depth counts how many times crossing increasing moves are made in this
#      process. If depth = 0, then only R3 and crossing decreasing moves are made.
#      :param k: planar diagram
#      :param depth: counts how many times crossing increasing moves are made
#      :return: the list of all obtained diagrams during the process
#     """
#
#     """
#     Diagram level is a list of list of sets
#     Outer list contains distinct diagrams
#     Inner list contains diagrams at a certain level
#     Inner inner set contains equivalent diagram at a certain level
#     I.e. the inner list contains sets of equivalent diagrams
#     """
#     # TODO: do we really need this function as it is very similar to "smart simplify"?
#     from knotpy.reidemeister.simplify import simplify_crossing_reducing
#
#     # level 0: original diagrams (reduced in canonical form)
#     ls = LeveledSet(canonical(simplify_crossing_reducing(diagram)))
#
#     # level 1: add R3 moves to the diagrams and simplify
#     ls.new_level(crossing_reducing_space(reidemeister_3_space(ls[-1])))
#
#     # level 2, 3,... make crossing increasing moves, then r3 moves, and repeat
#     for depth_index in range(depth):
#         # apply all increasing R2 moves (that form 3-regions) TODO: test
#         ls.new_level(detour_space(ls[-1]))
#         # apply all r3 moves
#         ls.new_level(crossing_reducing_space(reidemeister_3_space(ls[-1])))
#
#     return set(ls)

