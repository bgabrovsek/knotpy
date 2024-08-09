from itertools import chain

from knotpy.classes.planardiagram import PlanarDiagram
#from knotpy.reidemeister import batch_make_reidemeister_moves
from knotpy.reidemeister.reidemeister_1 import (ReidemeisterLocationAddKink, ReidemeisterLocationRemoveKink,
                                                find_reidemeister_1_add_kink, find_reidemeister_1_remove_kink,
                                                reidemeister_1_remove_kink, reidemeister_1_add_kink,
                                                choose_reidemeister_1_remove_kink, choose_reidemeister_1_add_kink)
from knotpy.reidemeister.reidemeister_2 import (ReidemeisterLocationPoke, ReidemeisterLocationUnpoke,
                                                find_reidemeister_2_unpoke, find_reidemeister_2_poke,
                                                reidemeister_2_unpoke, reidemeister_2_poke, choose_reidemeister_2_unpoke,
                                                choose_reidemeister_2_poke)
from knotpy.reidemeister.reidemeister_3 import (ReidemeisterLocationThree, find_reidemeister_3_triangle, reidemeister_3,
                                                choose_reidemeister_3_triangle)

from knotpy.reidemeister.detour_move import find_detour_moves
from knotpy.reidemeister._abstract_reidemeister_location import ReidemeisterLocation

from knotpy.utils.set_utils import MultiLevelSet
from knotpy.algorithms.canonical import canonical


def make_reidemeister_move(k: PlanarDiagram, location: ReidemeisterLocation, inplace=False):
    """Makes a Reidemeister move according to the type of location.
    TODO: move this to reidemeister
    :param k:
    :param location:
    :param inplace:
    :return:
    """
    if type(location) is ReidemeisterLocationRemoveKink:
        return reidemeister_1_remove_kink(k=k, location=location, inplace=inplace)

    elif type(location) is ReidemeisterLocationAddKink:
        return reidemeister_1_add_kink(k=k, location=location, inplace=inplace)

    elif type(location) is ReidemeisterLocationUnpoke:
        return reidemeister_2_unpoke(k=k, location=location, inplace=inplace)

    elif type(location) is ReidemeisterLocationPoke:
        return reidemeister_2_poke(k=k, location=location, inplace=inplace)

    elif type(location) is ReidemeisterLocationThree:
        return reidemeister_3(k=k, location=location, inplace=inplace)

    else:
        raise ValueError(f"Unknown Reidemesiter location {location}")


def unframe(k, inplace=False):
    """Remove framing of the planar diagram.
    :param k:
    :param inplace:
    :return:
    """
    if inplace:
        if isinstance(k, PlanarDiagram):
            k.framing = 0
            return k
        if isinstance(k, set):
            raise ValueError("Cannot perform in-place framing on a set")
        if isinstance(k, list):
            for m in k:
                m.framing = 0
            return k
        NotImplementedError("In-place framing on a generator not implemented")
    else:
        if isinstance(k, PlanarDiagram):
            return k.copy(framing=0)
        if isinstance(k, set):
            return {m.copy(framing=0) for m in k}
        if isinstance(k, list):
            return [m.copy(framing=0) for m in k]
        return (m.copy(framing=0) for m in k)


def batch_make_reidemeister_moves(k: PlanarDiagram, iterable_of_moves, put_in_canonical_form=False, framed=True):
    """Make a bunch of reidemeister moves
    :param k:
    :param iterable_of_moves:
    :param put_in_canonical_form:
    :param framed:
    :return:
    """

    if put_in_canonical_form:
        if framed:
            knots = [canonical(make_reidemeister_move(k, location, inplace=False)) for location in iterable_of_moves]
        else:
            knots = [unframe(canonical(make_reidemeister_move(k, location, inplace=False))) for location in iterable_of_moves]
    else:
        if framed:
            knots = [make_reidemeister_move(k, location, inplace=False) for location in iterable_of_moves]
        else:
            knots = [unframe(make_reidemeister_move(k, location, inplace=False)) for location in iterable_of_moves]

    return knots


def simplify_diagram_crossing_reducing(k: PlanarDiagram, inplace=False, framed=True):
    """ Use crossings reducing moves (R1 unkink and R2 unpoke) to simplify a diagram.
    :param k:
    :param inplace:
    :param framed:
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

    if not framed:
        print("fffff")
        k.framing = 0

    return k

def _reidemeister_3_space(k: PlanarDiagram):
    """Continuously perform R3 moves, until there are no unique diagrams left.
    :param k:
    :return: list of diagrams with R3 moves
    """
    mls = MultiLevelSet(canonical(k))
    while mls[-1]:
        level = len(mls)
        for k in mls[level-1]:
            mls.add_to_level(level, list(batch_make_reidemeister_moves(k, find_reidemeister_3_triangle(k), put_in_canonical_form=True)))
    return set(mls)


def _simplify_smart(k, depth, framed=True):

    if not framed:
        k.framing = 0

    def _r3_space_simp(m):
        r3_space = _reidemeister_3_space(m)
        r3_space_simpl = {canonical(simplify_diagram_crossing_reducing(m_, inplace=False)) for m_ in r3_space}
        if not framed:
            r3_space_simpl = unframe(r3_space_simpl)
        return r3_space | r3_space_simpl

    # put k and all its R3 moves into a multiset at level 0
    mls = MultiLevelSet(_r3_space_simp(simplify_diagram_crossing_reducing(k)))

    for level in range(1, 2 * depth + 1):
        #print("level 1", k)
        # make Reidemeister increasing moves on levels 1, 3, 5, ...
        # make R3 moves and decreasing moves on levels 2, 4, 6, ...

        if level % 2:  # make R3 moves every other time

            for k in mls[level - 1]:
                mls.add_to_level(level, batch_make_reidemeister_moves(k, find_detour_moves(k), put_in_canonical_form=True, framed=framed))

        else:
            for k in mls[level-1]:
                mls.add_to_level(level, _r3_space_simp(k))

            if not mls[level]:  # if there is nothing new, then break
                break

    return min(mls)




def _simplify_auto_obsolete(k, depth):
    DEBUG = False

    if DEBUG: print("Auto simplifying with depth", depth)

    kc = canonical(k.copy())
    level_diagrams = {0: {kc}}
    all_diagrams = {kc}


    for level in range(1, depth+1):  # recursion level
        if DEBUG: print(level)
        level_diagrams[level] = set()
        for k in level_diagrams[level-1]:
            if level % 3 != 0:
                r_moves = list(chain(
                        find_reidemeister_1_remove_kink(k),
                        find_reidemeister_2_unpoke(k),
                        find_reidemeister_3_triangle(k)
                    ))
                if DEBUG: print("  Level", level, r_moves)
                new_diagrams = set(batch_make_reidemeister_moves(k, r_moves))
                if DEBUG: print("       ", len(new_diagrams), "new diagrams")
            else:
                r_moves = list(chain(
                        find_reidemeister_1_remove_kink(k),
                        find_reidemeister_2_unpoke(k),
                        find_reidemeister_3_triangle(k),
                        find_reidemeister_1_add_kink(k),
                        find_reidemeister_2_poke(k)
                    ))
                if DEBUG:print(" *Level", level, r_moves)
                new_diagrams = set(batch_make_reidemeister_moves(k, r_moves, put_in_canonical_form=True))
                if DEBUG: print("       ", len(new_diagrams), "new diagrams")

            new_diagrams -= all_diagrams  # interested onlyin new diagrams
            if DEBUG: print("       ", len(new_diagrams), "new new diagrams")
            all_diagrams.update(new_diagrams)
            level_diagrams[level].update(new_diagrams)

    return canonical(min(all_diagrams))




def simplify_non_increasing(k, framed=True):
    """

    :param k:
    :param framed:
    :return:
    """

    if not framed:
        k.framing = 0

    def _r3_space_simp(m):
        r3_space = _reidemeister_3_space(m)
        r3_space_simpl = {canonical(simplify_diagram_crossing_reducing(m_, inplace=False)) for m_ in r3_space}
        if not framed:
            r3_space_simpl = unframe(r3_space_simpl)
        return r3_space | r3_space_simpl

    # put k and all its R3 moves into a multiset at level 0
    mls = MultiLevelSet(_r3_space_simp(simplify_diagram_crossing_reducing(k)))

    while mls[-1]:
        level = len(mls)
        for k in mls[-1]:
            mls.add_to_level(level, _r3_space_simp(k))

    return min(mls)


#
# def _simplify_non_increasing_OLD(k, depth, framed=True):
#     """Simplify the knot by using only non-crossing increasing Reidemeister moves
#     :param k: planar diagram
#     :param depth: depth of recursion
#     :return: minimal knot after Reidemeister moves
#     """
#     DEBUG = False
#
#     if DEBUG: print("Auto simplifying with depth", depth)
#
#     # put the canonical form at (recursion) level 0
#     kc = canonical(k)
#     level_diagrams = {0: {kc}}  # dictionary {recursion level: {new diagrams}}
#     all_diagrams = {kc}  # store all diagrams (at all levels)
#
#     #print("Simplifying", kc)
#
#     for level in range(1, depth+1):  # recursion level
#
#         if DEBUG: print(level)
#
#         level_diagrams[level] = set()
#
#         for k in level_diagrams[level-1]:  # process all knots at a level lower
#
#             # all possible Reidemeister moves
#             r_moves = list(chain(
#                     find_reidemeister_1_remove_kinks(k),
#                     find_reidemeister_2_unpokes(k),
#                     find_reidemeister_3_triangles(k)
#                 ))
#
#
#             new_diagrams = set(batch_make_reidemeister_moves(k, r_moves, put_in_canonical_form=True))
#
#             if DEBUG: print("       ", len(new_diagrams), f"diagrams at level {level}")
#             new_diagrams -= all_diagrams  # remove all diagrams that already appeared at lower recursion levels
#             if DEBUG: print("       ", len(new_diagrams), f"new diagrams  at level {level} ")
#
#             all_diagrams.update(new_diagrams)
#             level_diagrams[level].update(new_diagrams)
#
#     return min(all_diagrams)


def simplify(k, depth=1, method="auto", framed=True):
    """Simplify by performing sequences of Reidemesiter moves. if method is
    "all": all Reidemeisiter moves are performed,
    "auto": crossing-increasing Reidemesiter moves are prerformed only each 3rd time
    "decreasing": only decreasing moves are performed
    ""
    :param k:
    :param depth
    :param method:
    :return:
    """

    put_in_canonical_form = True

    method = method.strip().lower()

    if method == "smart":
        return _simplify_smart(k, depth, framed=framed)

    if method == "auto":
        return _simplify_auto_obsolete(k, depth)

    elif method == "nonincreasing" or method == "non-increasing":
        return simplify_non_increasing(k, framed=framed)

    elif method == "reducing" or method == "decreaesing":
        return simplify_diagram_crossing_reducing(k, framed=framed)

    else:
        raise NotImplementedError(f"Simplification method {method} not yet implemented")


