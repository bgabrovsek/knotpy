from itertools import chain, combinations, product
import multiprocessing
from collections import Counter
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.reidemeister.reidemeister_1 import (ReidemeisterLocationAddKink, ReidemeisterLocationRemoveKink,
                                                reidemeister_1_remove_kink, reidemeister_1_add_kink,
                                                choose_reidemeister_1_remove_kink, choose_reidemeister_1_add_kink)
from knotpy.reidemeister.reidemeister_2 import (ReidemeisterLocationPoke, ReidemeisterLocationUnpoke,
                                                reidemeister_2_unpoke, reidemeister_2_poke, choose_reidemeister_2_unpoke,
                                                choose_reidemeister_2_poke)
from knotpy.reidemeister.reidemeister_3 import (ReidemeisterLocationThree, find_reidemeister_3_triangle, reidemeister_3,
                                                choose_reidemeister_3_triangle)

from knotpy.reidemeister.detour_move import find_detour_moves
from knotpy.reidemeister._abstract_reidemeister_location import ReidemeisterLocation

from knotpy.utils.set_utils import LevelSet
from knotpy.algorithms.canonical import canonical
from knotpy.notation.pd import to_pd_notation
from knotpy.utils.equivalence import EquivalenceRelation
from knotpy.utils.multiprogressbar import Bar, FakeBar
from knotpy.reidemeister.space import simplification_space, simplify_crossing_reducing

USE_TANGLE_CANONICAL = False












def _minimal_crossing_diagrams(diagrams, max_difference=0):
    """ from all diagrams, return those that have the minimal number of crossings"""
    if diagrams:
        minimal_crossings = min(len(__k) for __k in diagrams)
        return {__k for __k in diagrams if len(__k) <= minimal_crossings + abs(max_difference)}
    else:
        return set()



def _group_intersecting_levels(diagram_levels):
    """join levels level-by-level if any two sets from the levels are intersect"""
    # join levels that are not disjoint in a set
    er = EquivalenceRelation(range(len(diagram_levels)))
    for (i, level_i), (j, level_j) in combinations(enumerate(diagram_levels), 2):
        if not all(set1.isdisjoint(set2) for set1, set2 in product(level_i, level_j)):  # are not disjoint?
            er[i] = j
    # join level-by-level levels that are in the same equivalence class
    return [[set.union(*sets) for sets in zip(*(diagram_levels[i] for i in indices))] for indices in er.classes()]

# diagram_levels = [
#     [{1}, {2,3,4}, {5,6,7}],
#     [{11}, {12, 13, 14}, {15, 16, 13}],
#     [{21}, {7, 23, 24}, {25, 26, 27}],
#     [{31}, {32, 33, 34}, {35, 26, 37}],
# ]
# print(_group_intersecting_levels(diagram_levels))


def simultaneously_simplify_diagrams(diagrams, depth, return_equivalences=False, progress_bar=None):
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


    PBar = Bar if progress_bar else FakeBar
    PBar = FakeBar

    progress_bar = progress_bar or (depth >= 2)

    # print("Simplify")
    # for d in diagrams:
    #     print("  ", d)

    if return_equivalences:
        # TODO: just add 0th level as dict
        raise NotImplementedError("return equivalences not working")

    # level 0: original diagrams (reduced in canonical form)
    diagram_levels = [
        [
            {canonical(simplify_crossing_reducing(k))}
        ]
        for k in diagrams
    ]
    original_diagram_dict = {k: k_ for k, (k_,) in zip(diagrams, diagram_levels)}  # for reconstructing the result

    number_of_diagrams = len(diagrams)

    # level 1: add R3 moves to the diagrams
    for levels in diagram_levels:
        levels.append(reidemeister_3_space(levels[0]))  # r3 depth is infinite
        levels[-1] = _simplification_space(levels[-1])  # overwrite
        levels[-1] = _minimal_crossing_diagrams(levels[-1]) # keep only minimal

    diagram_levels = _group_intersecting_levels(diagram_levels)

    # level 2, 3,... make crossing increasing moves, then r3 moves, and repeat
    for depth_index in PBar(range(depth), total=depth):

        #print("depth", depth_index, type(diagram_levels), type(diagram_levels[0]), type(next(iter(diagram_levels[0]))))

        PBar.set_comment(f"depth {depth_index} R2 {number_of_diagrams}->{len(diagram_levels)}")

        for levels in PBar(diagram_levels, total=len(diagram_levels)):
            #prpriint(levels)
            # add R2 poke moves
            levels.append(_detour_space(levels[-1]))
            # remove previous diagrams
            for prev_lvl in levels[:-1]:
                levels[-1] -= prev_lvl

        diagram_levels = _group_intersecting_levels(diagram_levels)

        PBar.set_comment(f"depth {depth_index} R3 {number_of_diagrams}->{len(diagram_levels)}")

        for levels in PBar(diagram_levels, total=len(diagram_levels)):
            # add R2 poke moves
            levels.append(reidemeister_3_space(levels[-1]))
            levels[-1] = _simplification_space(levels[-1])  # overwrite
            #levels[-1] = _minimal_crossing_diagrams(levels[-1])  # keep only minimal (weaker but faster)
            # remove previous diagrams
            for prev_lvl in levels[:-1]:
                levels[-1] -= prev_lvl

        diagram_levels = _group_intersecting_levels(diagram_levels)

        PBar.set_comment(f"{number_of_diagrams}->{len(diagram_levels)}")

    flattened = [set(chain(*level)) for level in diagram_levels]
    return set(min(f) for f in flattened) #_minimal_crossing_diagrams(flattened)


def all_minimal_crossings_simplifications(k, depth, max_difference=0):

    levels = [{canonical(simplify_crossing_reducing(k))}]

    # level 1: add R3 moves to the diagrams
    levels.append(reidemeister_3_space(levels[0]))  # r3 depth is infinite
    levels[-1] = _simplification_space(levels[-1])  # overwrite
    levels[-1] = _minimal_crossing_diagrams(levels[-1])  # keep only minimal

    # level 2, 3,... make crossing increasing moves, then r3 moves, and repeat
    for depth_index in range(depth):

        # add R2 poke moves
        levels.append(_detour_space(levels[-1]))
        for prev_lvl in levels[:-1]:
            levels[-1] -= prev_lvl

        levels.append(reidemeister_3_space(levels[-1]))
        levels[-1] |= _simplification_space(levels[-1])  # overwrite
        # levels[-1] = _minimal_crossing_diagrams(levels[-1])  # keep only minimal (weaker but faster)
        # remove previous diagrams
        for prev_lvl in levels[:-1]:
            levels[-1] -= prev_lvl

    levels_min = [_minimal_crossing_diagrams(level, max_difference=max_difference) for level in levels]

    return set(chain(*levels_min))

def simplify_smart(k, depth, progress_bar=False):
    return simultaneously_simplify_diagrams([k], depth, progress_bar=progress_bar).pop()


def simplify_non_increasing(k):
    """Try to simplify the diagram k in such a way, that we perform all possible R3 moves, followed by crossing
    decreasing moves. This is repeated until no new diagrams appear during the process.
    :param k: planar diagram
    :return: simplified diagram, if exists, otherwise returns k
    """

    levels = [{canonical(k)}]

    while levels[-1]:
        # add diagrams after all possible R3 moves from previous level
        levels.append(reidemeister_3_space(levels[-1]))
        # add also all simplified diagrams from current level
        levels[-1].update(_simplification_space(levels[-1]))
        #levels[-1].update([simplify_crossing_reducing(k) for k in levels[-1]])
        # remove diagrams from previous levels
        for prev_lvl in levels[:-1]:
            levels[-1] -= prev_lvl

    # find the minimal diagram
    candidates = {k for lvl in levels for k in lvl}
    candidates = _minimal_crossing_diagrams(candidates)
    return min(candidates)

def simplify(k, depth=1, method="smart"):
    """Simplify by performing sequences of Reidemesiter moves. Supported methods: "smart", "non-increasing",
    "decreasing".
    :param k:
    :param depth:
    :param method:
    :return:
    """

    method = method.strip().lower()

    if method in ["smart"]:
        return simplify_smart(k, depth)

    elif method in ["nonincreasing", "non-increasing"]:
        return simplify_non_increasing(k)

    elif method in ["reducing", "decreaesing"]:
        return simplify_crossing_reducing(k)

    else:
        raise NotImplementedError(f"Simplification method {method} not yet implemented")


def simplify_parallel(diagrams, depth=1, method="smart"):
    with multiprocessing.Pool(processes=6) as pool:
        result = pool.starmap(simplify, ((d, depth, method) for d in diagrams))
    return result

def simultaneously_simplify_diagrams_parallel(list_of_diagrams, depth, processes):
    with multiprocessing.Pool(processes=processes) as pool:
        result = pool.starmap(simultaneously_simplify_diagrams,
                              ((diagrams,  depth, False, None) for diagrams in list_of_diagrams)
                              )
    return result

if __name__ == "__main__":
    import knotpy as kp
    from time import time
    pd = "abcd efgh bdei cijk kjhg a f & abcd efgh bihc idfe a g & abcd efgh bdij ceki jkhg a f & abcd efgh acif ibjk hgkj d e & abcd efgh ijdc klam gelk hmji b f & abcd efgh dcij bfki jkeg a h & abcd efgh bijc jkld lmhf kiem a g & abcd efgh eiba fcig d h & abcd efgh hadi jick fjkg b e & abcd efgh beic ijkd jgfk a h & abcd efgh ijdc fkaj hgik b e & abcd efgh ijba klid fkmg mjlh c e & abcd efgh iadj kljc fkmg emil b h & abcd efgh bdij kclm mlfe jikh a g"
    knots = [kp.from_condensed_pd_notation(s) for s in pd.split(" & ")]
    #b = kp.from_condensed_pd_notation("abcd efgh ijba hdjk flmg lkim c e")

    print("In:")
    for k in knots:
        print(k)
    print(f"({len(k)} knots)")

    print()
    t = time()
    ret = {simplify(k, depth=2) for k in knots}
#        simultaneously_simplify_group(knots, depth=1))
    print("time:", time()-t)
    print("Out:")
    for r in ret:
        print(r)
    print(f"({len(ret)} knots)")
    for r in ret:
        print(canonical(r))

