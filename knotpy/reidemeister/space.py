"""
Reidemesiter space (all moves, all diagrams up to some degree,...)

"""
from itertools import chain

from knotpy.algorithms.canonical import canonical
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.reidemeister.reidemeister_1 import choose_reidemeister_1_remove_kink, reidemeister_1_remove_kink
from knotpy.reidemeister.reidemeister_2 import choose_reidemeister_2_unpoke, reidemeister_2_unpoke
from knotpy.reidemeister.reidemeister_3 import reidemeister_3, find_reidemeister_3_triangle
from knotpy.reidemeister.detour_move import find_detour_moves
from knotpy.reidemeister.reidemeister import make_reidemeister_move
from knotpy.utils.set_utils import LevelSet


def simplify_crossing_reducing(k: PlanarDiagram, inplace=False):
    """ Use crossings reducing moves, R1 unkink and R2 unpoke, to simplify a diagram.
    :param k:
    :param inplace:
    :return:
    """
    if not inplace:
        k = k.copy()
    changes_were_made = True

    while changes_were_made:
        changes_were_made = False
        while location := choose_reidemeister_1_remove_kink(k, random=False):
            reidemeister_1_remove_kink(k, location, inplace=True)
            changes_were_made = True
        while location := choose_reidemeister_2_unpoke(k, random=False):
            reidemeister_2_unpoke(k, location, inplace=True)
            changes_were_made = True

    return k


def reidemeister_3_space(diagrams, depth=None) -> set:
    """Iteratively make all possible R3 moves on a diagram. We do not put diagrams in canonical form.
    :param diagrams: planar diagram or set of planar diagrams
    :param depth:
    :return: list of diagrams after possible sequences of R3 moves
    """
    depth = len(diagrams) if depth is None else depth

    # allways assume we have a set of equivalent diagrams
    diagrams = {diagrams} if isinstance(diagrams, PlanarDiagram) else diagrams
    diagrams = diagrams if isinstance(diagrams, set) else set(diagrams)

    levels = [diagrams]  # level 1 contains diagrams after one R3 move, level 2 contains diagrams after two R3 moves,...

    # add all possible R3 moves in level
    while levels[-1] and len(levels) <= depth:
        levels.append(
            {
                canonical(reidemeister_3(k, location, inplace=False))
                for k in levels[-1]
                for location in find_reidemeister_3_triangle(k)
                if "_r3" not in k.attr or k.attr != {location.face[0].node, location.face[1].node, location.face[2].node}
            }
        )

        # remove diagrams that are already in lower levels
        for prev_lvl in levels[:-1]:
            levels[-1] -= prev_lvl


    results = set(chain(*levels))
    # remove _r3 attributes, since they can be changed on next levels when different R3 moves are performed
    for k in results:
        if "_r3" in k.attr:
            del k.attr["_r3"]

    return results


def detour_space(diagram):
    """Perform all R2 increasing moves, such that an R3 move can be made in the future.
    diagram can be a planr diagram or a set of planar diagrams"""

    # always assume we have a set of equivalent diagrams
    diagrams = {diagram} if isinstance(diagram, PlanarDiagram) else (diagram if isinstance(diagram, set) else set(diagram))

    return {
        canonical(make_reidemeister_move(k, location, inplace=False))
        for k in diagrams
        for location in find_detour_moves(k)
        }

def simplification_space(diagrams):
    return {canonical(simplify_crossing_reducing(k, inplace=False)) for k in diagrams}


def smart_reidemeister_space(diagram, depth):
    """Make depth crossing increasing moves and any number of Reidemesiter 3 moves, then returns the whole set of
    obtained diagrams

    :param diagram:
    :param depth:
    :return:
    """
    """Try to simplify the diagram k in such a way, that we perform all possible R3 moves, followed by crossing
     decreasing moves, followed by crossing increasing moves, where the increasing moves are taken in such a way, that
     a new non-alternating 3-gon appears. The depth counts how many times crossing increasing moves are made in this
     process. If depth = 0, then only R3 and crossing decreasing moves are made.
     :param k: planar diagram
     :param depth: counts how many times crossing increasing moves are made
     :return: the list of all obtained diagrams during the process
    """

    """
    Diagram level is a list of list of sets
    Outer list contains distinct diagrams
    Inner list contains diagrams at a certain level
    Inner inner set contains equivalent diagram at a certain level
    I.e. the inner list contains sets of equivalent diagrams 
    """



    # level 0: original diagrams (reduced in canonical form)
    levels = LevelSet([canonical(simplify_crossing_reducing(diagram))])

    # level 1: add R3 moves to the diagrams and simplify
    levels.extend(simplification_space(reidemeister_3_space(levels[0])), level=1)

    # level 2, 3,... make crossing increasing moves, then r3 moves, and repeat
    for depth_index in range(depth):
        level = 2 * depth_index + 2

        # apply all increasing R2 moves (that form 3-regions)
        levels.extend(detour_space(levels[level - 1]), level=level)

        # apply all r3 moves
        levels.extend(simplification_space(reidemeister_3_space(levels[0])), level=level + 1)

    S = levels[0] | levels[1]
    return S.union(*(levels[2 * i + 2 + 1] for i in range(depth)))

