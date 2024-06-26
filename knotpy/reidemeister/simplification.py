from itertools import chain
from collections import Counter

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.reidemeister._abstract_reidemeister_location import ReidemeisterLocation
from knotpy.reidemeister.reidemeister_1 import (ReidemeisterLocationAddKink, ReidemeisterLocationRemoveKink,
                                                find_reidemeister_1_add_kinks, find_reidemeister_1_remove_kinks,
                                                reidemeister_1_remove_kink, reidemeister_1_add_kink,
                                                choose_reidemeister_1_remove_kink, choose_reidemeister_1_add_kink)
from knotpy.reidemeister.reidemeister_2 import (ReidemeisterLocationPoke, ReidemeisterLocationUnpoke,
                                                find_reidemeister_2_unpokes, find_reidemeister_2_pokes,
                                                reidemeister_2_unpoke, reidemeister_2_poke, choose_reidemeister_2_unpoke,
                                                choose_reidemeister_2_poke)
from knotpy.reidemeister.reidemeister_3 import (ReidemeisterLocationThree, find_reidemeister_3_triangles, reidemeister_3,
                                                choose_reidemeister_3_triangle)
from knotpy.notation.pd import to_pd_notation

#from knotpy.reidemeister.reidemeister import reidemeister_1_remove_kink, reidemeister_2_unpoke, reidemeister_2_poke, reidemeister_1_add_kink, reidemeister_3
# from knotpy.reidemeister.find_reidemeister_moves import choose_reidemeister_1_unkink, choose_reidemeister_2_unpoke
# from knotpy.reidemeister.find_reidemeister_moves import (find_reidemeister_1_kinks, find_reidemeister_1_unkinks,
#                                                          find_reidemeister_2_pokes, find_reidemeister_2_unpokes,
#                                                          find_reidemeister_3_triangles)
from knotpy.algorithms.canonical import canonical


def simplify_diagram_crossing_reducing(k: PlanarDiagram, inplace=False):
    """ Use crossings reducing moves (R1 unkink and R2 unpoke) to simplify a diagram.
    :param k:
    :param inplace:
    :return:
    """

    changes_were_made = True

    if inplace:
        k = k.copy()

    while changes_were_made:

        changes_were_made = False

        while location := choose_reidemeister_1_remove_kink(k, random=False):
            reidemeister_1_remove_kink(k, location, inplace=True)
            changes_were_made = True

        while location := choose_reidemeister_2_unpoke(k, random=False):
            #print("eps", k, eps)
            reidemeister_2_unpoke(k, location, inplace=True)
            changes_were_made = True

    return k


def make_reidemeister_move(k: PlanarDiagram, location: ReidemeisterLocation, inplace=False):
    """
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
        raise ValueError(f"Unknown Reidemesiter locatio {location}")


def batch_make_reidemeister_moves(k: PlanarDiagram, iterable_of_moves, put_in_canonical_form=False):
    """Make a bunch of reidemeister moves

    :param k:
    :param iterable_of_moves:
    :return:
    """
    if put_in_canonical_form:
        knots = [canonical(make_reidemeister_move(k, location, inplace=False)) for location in iterable_of_moves]
    else:
        knots = [canonical(make_reidemeister_move(k, location, inplace=False)) for location in iterable_of_moves]

    return knots

# def _all_reidemeister_moves(k, move):
#     """
#     :param k:
#     :param move:
#     :return:
#     """
#     move = move.lower()
#
#     result = set()
#
#     if move == "kink":
#         # add kink
#         for ep, sign in find_reidemeister_1_kinks(k):
#             k_ = reidemeister_1_add_kink(k, ep, sign)
#             result.add(canonical(k_))
#     elif move == "unkink":
#         # unkink
#         for ep in find_reidemeister_1_unkinks(k):
#             k_ = reidemeister_1_remove_kink(k, ep)
#             result.add(canonical(k_))
#     elif move == "poke":
#         # poke
#         for ep_a, ep_b in find_reidemeister_2_pokes(k):
#             k_ = reidemeister_2_poke(k, ep_a, ep_b)
#             result.add(canonical(k_))
#     elif move == "unpoke":
#         # unpoke
#         for face in find_reidemeister_2_unpokes(k):
#             k_ = reidemeister_2_unpoke(k, face)
#             result.add(canonical(k_))
#     elif move == "triangle":
#         # triangle move
#         #print("All triangle moves")
#         for face in find_reidemeister_3_triangles(k):
#             k_ = reidemeister_3(k, face)
#             #print("--")
#             result.add(canonical(k_))
#     else:
#         raise ValueError(f"Move {move} not known.")
#
#     return result

def _simplify_auto(k, depth):
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
                        find_reidemeister_1_remove_kinks(k),
                        find_reidemeister_2_unpokes(k),
                        find_reidemeister_3_triangles(k)
                    ))
                if DEBUG: print("  Level", level, r_moves)
                new_diagrams = set(batch_make_reidemeister_moves(k, r_moves))
                if DEBUG: print("       ", len(new_diagrams), "new diagrams")
            else:
                r_moves = list(chain(
                        find_reidemeister_1_remove_kinks(k),
                        find_reidemeister_2_unpokes(k),
                        find_reidemeister_3_triangles(k),
                        find_reidemeister_1_add_kinks(k),
                        find_reidemeister_2_pokes(k)
                    ))
                if DEBUG:print(" *Level", level, r_moves)
                new_diagrams = set(batch_make_reidemeister_moves(k, r_moves, put_in_canonical_form=True))
                if DEBUG: print("       ", len(new_diagrams), "new diagrams")

            new_diagrams -= all_diagrams  # interested onlyin new diagrams
            if DEBUG: print("       ", len(new_diagrams), "new new diagrams")
            all_diagrams.update(new_diagrams)
            level_diagrams[level].update(new_diagrams)

    return canonical(min(all_diagrams))


def _simplify_non_increasing(k, depth):
    """Simplify the knot by using only non-crossing increasing Reidemeister moves
    :param k: planar diagram
    :param depth: depth of recursion
    :return: minimal knot after Reidemeister moves
    """
    DEBUG = False

    if DEBUG: print("Auto simplifying with depth", depth)

    # put the canonical form at (recursion) level 0
    kc = canonical(k)
    level_diagrams = {0: {kc}}  # dictionary {recursion level: {new diagrams}}
    all_diagrams = {kc}  # store all diagrams (at all levels)

    #print("Simplifying", kc)

    for level in range(1, depth+1):  # recursion level

        if DEBUG: print(level)

        level_diagrams[level] = set()

        for k in level_diagrams[level-1]:  # process all knots at a level lower

            # all possible Reidemeister moves
            r_moves = list(chain(
                    find_reidemeister_1_remove_kinks(k),
                    find_reidemeister_2_unpokes(k),
                    find_reidemeister_3_triangles(k)
                ))


            new_diagrams = set(batch_make_reidemeister_moves(k, r_moves, put_in_canonical_form=True))

            if DEBUG: print("       ", len(new_diagrams), f"diagrams at level {level}")
            new_diagrams -= all_diagrams  # remove all diagrams that already appeared at lower recursion levels
            if DEBUG: print("       ", len(new_diagrams), f"new diagrams  at level {level} ")

            all_diagrams.update(new_diagrams)
            level_diagrams[level].update(new_diagrams)

    return min(all_diagrams)


def simplify(k, depth, method="auto"):
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


    method = method.lower()

    if method == "auto":
        return _simplify_auto(k, depth)

    elif method == "nonincreasing" or method == "non-increasing":
        return _simplify_non_increasing(k, depth)

    else:
        raise NotImplementedError(f"Simplification method {method} not yet implemented")



    # print(Counter([len(d) for d in all_diagrams]))
    # mindeg = min(len(d) for d in all_diagrams)
    #
    # mink = [d for d in all_diagrams if len(d) == mindeg][0]
    # print(mink < k, mink)






    #
    #
    # changes_made = True
    #
    # while changes_made:
    #
    #     changes_made = False
    #
    #     while kink := choose_kink(k):
    #
    #         if _debug:
    #             kc = deepcopy(k)
    #             poly_1 = __bracket_polynomial(kc)
    #         remove_kink(k, kink)
    #
    #         if _debug:
    #             poly_2 = __bracket_polynomial(k)
    #             if poly_1 != poly_2:
    #                 print("Wrong unkink:")
    #                 print("before removal", kc)
    #                 print(" after removal", k)
    #                 print("poly before removal", poly_1)
    #                 print(" poly after removal", poly_2)
    #
    #         changes_made = True
    #     while poke := choose_poke(k):
    #
    #         if _debug:
    #             kc = deepcopy(k)
    #             poly_1 = __bracket_polynomial(kc)
    #
    #
    #         reidemeister_2_unpoke(k, poke)
    #
    #         if _debug:
    #             poly_2 = __bracket_polynomial(k)
    #             if poly_1 != poly_2:
    #                 print("Wrong unkink:")
    #                 print("mod", k)
    #                 print("ori", kc)
    #                 print("poke", poke)
    #                 print("p1",poly_1)
    #                 print("p2",poly_2)
    #
    #         changes_made = True
    #
    # return k
    #
    #
