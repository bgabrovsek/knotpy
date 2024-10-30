


def _make_smart_reidemeister_moves_iteratively_old(k, depth):
    """Try to simplify the diagram k in such a way, that we perform all possible R3 moves, followed by crossing
     decreasing moves, followed by crossing increasing moves, where the increasing moves are taken in such a way, that
     a new non-alternating 3-gon appears. The depth counts how many times crossing increasing moves are made in this
     process. If depth = 0, then only R3 and crossing decreasing moves are made.
     :param k: planar diagram
     :param depth: counts how many times crossing increasing moves are made
     :return: the list of all obtained diagrams during the process
    """
    DEBUG = False
    DEBUG_EVEN_MORE = False  # also print diagrams at each level
    DEBUG_LEVEL_SIZE = True

    KEEP_ONLY_REDUCING_AFTER_R3 = True
    KEEP_ONLY_MINIMAL_CROSSING_AFTER_R3 = False
    KEEP_ONLY_MINIMAL_DIAGRAM_ON_FIRST_LEVEL = True

    """
    TTT 17.5
    FTT 17.38
    TFT infinity
    TFF 17.4
    """

    #if DEBUG: print(f"**** Simplifying {k} ****")

    levels = [{canonical(simplify_crossing_reducing(k))}]  # 0th level is the original diagram

    #if DEBUG: print(f"Level #0 diagrams: {len(levels[-1])} {Counter([len(l) for l in levels[-1]])} (init)")

    print("---")
    for depth_index in range(depth * 2 + 1):


        if DEBUG_LEVEL_SIZE: print(f"Depth {depth_index} {('inc' if (depth_index % 2) else 'R3')} size {len(levels[-1])}", end="", flush=True)

        if not (depth_index % 2):

            #if DEBUG: print(f"Level #{depth_index} diagrams: {len(levels[-1])} {Counter([len(l) for l in levels[-1]])} (before R3)")

            # on every odd move, add diagrams with all possible R3 moves from previous level
            new_level = set.union(*(reidemeister_3_space(k, 2) for k in levels[-1]))

            #if DEBUG: print(f"Level #{depth_index} diagrams: {len(new_level)} {Counter([len(l) for l in new_level])} (after R3)")
            #if DEBUG_EVEN_MORE: print("\n     ".join([str(k) for k in new_level]))

            # add also all simplified diagrams from current level

            new_level = {canonical(simplify_crossing_reducing(k)) for k in new_level} | (set() if KEEP_ONLY_REDUCING_AFTER_R3 else new_level)

            #if DEBUG: print(f"Level #{depth_index} diagrams: {len(new_level)} {Counter([len(l) for l in new_level])} (after reducing simplify)")
            #if DEBUG_EVEN_MORE: print("\n     ".join([str(k) for k in new_level]))

            #if DEBUG: print(f"Level #{depth_index} diagrams: {len(new_level)} {Counter([len(l) for l in new_level])} (after keep minimal simplify)")
        else:

            #if DEBUG: print(f"Level #{depth_index} diagrams: {len(levels[-1])} {Counter([len(l) for l in levels[-1]])} (before increasing)")

            # on even moves, add detour moves (crossing increasing moves, s.t. R3 can be performed on next iteration
            new_level = set(chain.from_iterable(
                    batch_make_reidemeister_moves(k, find_detour_moves(k), put_in_canonical_form=True)
                for k in levels[-1]))

            #if DEBUG: print(f"Level #{depth_index} diagrams: {len(new_level)} {Counter([len(l) for l in new_level])} (after increasing)")
            #if DEBUG_EVEN_MORE: print("\n     ".join([str(k) for k in new_level]))

        # remove diagrams from previous levels
        for prev_lvl in levels[:-1]:
            #if DEBUG: print(f"Level #{depth_index} diagrams: {len(new_level)} {Counter([len(l) for l in new_level])} (before remove previous levels)")
            new_level -= prev_lvl
            #if DEBUG: print(f"Level #{depth_index} diagrams: {len(new_level)} {Counter([len(l) for l in new_level])} (after remove previous levels)")

        # keep only minimal?
        if KEEP_ONLY_MINIMAL_CROSSING_AFTER_R3 and depth > 0 and not (depth_index % 2):
            minimal_crossings = min(len(k) for k in new_level)
            minimal_crossings_set = {k for k in new_level if len(k) <= minimal_crossings+1}  # VARIATION , remove +1
            new_level = minimal_crossings_set

        # on 1st move, just take the smallest diagram, then perform crossing increasing moves
        if KEEP_ONLY_MINIMAL_DIAGRAM_ON_FIRST_LEVEL and depth_index == 0 and new_level:
            #if DEBUG: print("Keeping only minimal levels")
            new_level = {min(new_level)}

        if new_level:
            #if DEBUG: print("adding", len(new_level))
            levels.append(new_level)

        if DEBUG_LEVEL_SIZE:
            print(" ->", len(new_level))

        #print(f" -> {len(levels[-1])}")

        # if DEBUG:
        #     print("Levels:", [len(l) for l in levels])


        # if no new results, break the loop, unless it is the fist iteration (original diagram does not have R3 moves)
        # if not levels[-1]:
        #     del levels[-1]
        #     if depth_index != 0:
        #         break

    return set(chain(*levels))


# def simultaneously_simplify_diagrams(diagrams, depth):
#
#     # simplify the diagrams
#     previous_diagrams = [{__canonical(simplify_crossing_reducing(k))} for k in diagrams]
#     current_diagrams = []
#
#     # step 0: just add R3 moves
#     for diagrams in previous_diagrams:
#         current_diagrams.append(_smart_reidemeister_search_single_level(diagrams, r3_only=True))
#         diagrams |= current_diagrams[-1]
#
#
#
#     for depth_index in range(depth):
#
#
#     # optionally include reduced diagrams
#     r3_space |= {__canonical(simplify_crossing_reducing(k)) for k in r3_space}


def reidemeister_3_space(k: PlanarDiagram, depth=None) -> set:
    """Iteratively make all possible R3 moves on a diagram. We do not put diagrams in canonical form.
    :param k: planar diagram
    :param depth:
    :return: list of diagrams after possible sequences of R3 moves
    """

    levels = [{k}]  # level 1 contains diagrams after one R3 move, level 2 contains diagrams after two R3 moves, ...
    depth_index = 0

    while levels[-1] and (depth is None or depth_index < depth):
        depth += 1
        levels.append(
            {
                canonical(reidemeister_3(k, location, inplace=False))
                for k in levels[-1]
                for location in find_reidemeister_3_triangle(k)
                if "_r3" not in k.attr or k.attr != {location.face[0].node, location.face[1].node, location.face[2].node}
            }
        )

        # add all diagrams after another R3 move in canonical form
        # for k in levels[-1]:
        #     for location in find_reidemeister_3_triangle(k):
        #         if "_r3" not in k.attr or k.attr != {location.face[0].node, location.face[1].node, location.face[2].node}:  # do not undo the previous R3 move
        #             new_level.add(canonical(reidemeister_3(k, location, inplace=False)))

        # remove diagrams that are already in lower levels
        for prev_lvl in levels:
            new_level -= prev_lvl

        levels.append(new_level)

    results = set(chain(*levels))
    # remove _r3 attributes, since they can be changed on next levels when different R3 moves are performed
    for k in results:
        if "_r3" in k.attr:
            del k.attr["_r3"]
    return results
from itertools import chain
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

from knotpy.utils.set_utils import MultiLevelSet
from knotpy.algorithms.canonical import canonical
from knotpy.notation.pd import to_pd_notation
from knotpy.utils.equivalence import EquivalenceRelation

USE_TANGLE_CANONICAL = False


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


def batch_make_reidemeister_moves(k: PlanarDiagram, iterable_of_moves):
    """Make a bunch of reidemeister moves.
    :param k:
    :param iterable_of_moves:
    :return:
    """
    return [make_reidemeister_move(k, location, inplace=False) for location in iterable_of_moves]


def reidemeister_3_space(k: PlanarDiagram, depth=None) -> set:
    """Iteratively make all possible R3 moves on a diagram. We do not put diagrams in canonical form.
    :param k: planar diagram
    :param depth:
    :return: list of diagrams after possible sequences of R3 moves
    """

    levels = [{k}]  # level 1 contains diagrams after one R3 move, level 2 contains diagrams after two R3 moves, ...
    depth_index = 0

    while levels[-1] and (depth is None or depth_index < depth):
        depth += 1
        levels.append(
            {
                canonical(reidemeister_3(k, location, inplace=False))
                for k in levels[-1]
                for location in find_reidemeister_3_triangle(k)
                if "_r3" not in k.attr or k.attr != {location.face[0].node, location.face[1].node, location.face[2].node}
            }
        )

        # add all diagrams after another R3 move in canonical form
        # for k in levels[-1]:
        #     for location in find_reidemeister_3_triangle(k):
        #         if "_r3" not in k.attr or k.attr != {location.face[0].node, location.face[1].node, location.face[2].node}:  # do not undo the previous R3 move
        #             new_level.add(canonical(reidemeister_3(k, location, inplace=False)))

        # remove diagrams that are already in lower levels
        for prev_lvl in levels:
            new_level -= prev_lvl

        levels.append(new_level)

    results = set(chain(*levels))
    # remove _r3 attributes, since they can be changed on next levels when different R3 moves are performed
    for k in results:
        if "_r3" in k.attr:
            del k.attr["_r3"]
    return results


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


def _minimal_crossing_diagrams(diagrams):
    """ from all diagrams, return those that have the minimal number of crossings"""
    if diagrams:
        minimal_crossings = min(len(__k) for __k in diagrams)
        return {__k for __k in diagrams if len(__k) == minimal_crossings}
    else:
        return set()

def _detour_space(diagrams):
    """Perform all R2 increasing moves, such that an R3 move can be made in the future."""
    return {k

        for k in diagrams[-1]
            for location in find_detour_moves(k)
    }

def _smart_reidemeister_search_single_level(diagrams, exclude_diagrams: set = frozenset(), r3_only=False):
    """Performs R3 and increasing R2 moves on the given diagrams. If exclude_diagrams is given, those are removed from
    the sets"""

    # part 1: R2 increasing moves

    if not r3_only:

        r2_space = set(chain.from_iterable(
            batch_make_reidemeister_moves(k, find_detour_moves(k), put_in_canonical_form=True)
            for k in diagrams[-1]))

        r2_space -= exclude_diagrams | diagrams
    else:
        r2_space = diagrams

    # part 2: R3 moves

    r3_space = r2_space | set.union(*(reidemeister_3_space(k, 2) for k in r2_space))  # make R3 moves

    # optionally include reduced diagrams
    r3_space |= {canonical(simplify_crossing_reducing(k)) for k in r3_space}

    r3_space -= diagrams | exclude_diagrams

    # optionally, keep only minimal diagrams
    r3_space = _minimal_crossing_diagrams(r3_space)

    return r3_space







def simultaneously_simplify_diagrams_new(diagrams, depth):
    """Try to simplify the diagram k in such a way, that we perform all possible R3 moves, followed by crossing
     decreasing moves, followed by crossing increasing moves, where the increasing moves are taken in such a way, that
     a new non-alternating 3-gon appears. The depth counts how many times crossing increasing moves are made in this
     process. If depth = 0, then only R3 and crossing decreasing moves are made.
     :param k: planar diagram
     :param depth: counts how many times crossing increasing moves are made
     :return: the list of all obtained diagrams during the process
    """
    DEBUG = False
    DEBUG_EVEN_MORE = False  # also print diagrams at each level
    DEBUG_LEVEL_SIZE = False

    KEEP_ONLY_REDUCING_AFTER_R3 = True
    KEEP_ONLY_MINIMAL_CROSSING_AFTER_R3 = False
    KEEP_ONLY_MINIMAL_DIAGRAM_ON_FIRST_LEVEL = True

    """
    TTT 17.5
    FTT 17.38
    TFT infinity
    TFF 17.4
    """

    diagram_levels = [[{canonical(simplify_crossing_reducing(k))}] for k in diagrams]  # 0th level is the original diagram

    if DEBUG_LEVEL_SIZE: print("---")
    all_depths = depth * 2 + 1
    for depth_index in range(depth * 2 + 1):

        for dind, dlevels in enumerate(diagram_levels):

            # s_dep = s = "*"*(depth_index+1) + "-" * (all_depths-depth_index-1)
            # s_lev = s = "*"*(dind+1) + "-" * (len(diagram_levels)-dind-1)
            # print(s_dep, "|", s_lev)


            if DEBUG_LEVEL_SIZE: print(f"Depth {depth_index} {('inc' if (depth_index % 2) else 'R3')} size {len(dlevels[-1])}", end="", flush=True)

            if not (depth_index % 2):

                # on every odd move, add diagrams with all possible R3 moves from previous level
                new_level = set.union(*(reidemeister_3_space(k, 2) for k in dlevels[-1]))

                # add also all simplified diagrams from current level

                new_level = {canonical(simplify_crossing_reducing(k)) for k in new_level} | (set() if KEEP_ONLY_REDUCING_AFTER_R3 else new_level)
            else:

                # on even moves, add detour moves (crossing increasing moves, s.t. R3 can be performed on next iteration
                new_level = set(chain.from_iterable(
                        batch_make_reidemeister_moves(k, find_detour_moves(k), put_in_canonical_form=True)
                    for k in dlevels[-1]))

            # remove diagrams from previous levels
            for prev_lvl in dlevels[:-1]:
                new_level -= prev_lvl

            # keep only minimal?
            if KEEP_ONLY_MINIMAL_CROSSING_AFTER_R3 and depth > 0 and not (depth_index % 2):
                minimal_crossings = min(len(k) for k in new_level)
                minimal_crossings_set = {k for k in new_level if len(k) <= minimal_crossings}  # VARIATION , remove +1
                new_level = minimal_crossings_set

            # on 1st move, just take the smallest diagram, then perform crossing increasing moves
            if KEEP_ONLY_MINIMAL_DIAGRAM_ON_FIRST_LEVEL and depth_index == 0 and new_level:
                new_level = {min(new_level)}

            if new_level:
                dlevels.append(new_level)

            if DEBUG_LEVEL_SIZE:
                print(" ->", len(new_level))

        flattened = [set(chain(*dl)) for dl in diagram_levels]
        num = len(flattened)
        e = EquivalenceRelation(range(num))
        for i in range(num):
            for j in range(i+1, num):
                if not flattened[i].isdisjoint(flattened[j]):
                    e[i] = j
        # join classes
        delete_ind = []
        number_of_diagrams = len(diagram_levels)
        for c in e.classes():
            if len(c) > 1:
                c = sorted(c)
                i = c[0]
                for j in c[1:]:
                    delete_ind.append(i)
                    for li, lj in zip(diagram_levels[i], diagram_levels[j]):
                        li |= lj
        for i in sorted(delete_ind, reverse=True):
            del diagram_levels[i]
        if number_of_diagrams != len(diagram_levels):
            print("**** Reduced", number_of_diagrams, "->", len(diagram_levels))


        if e.number_of_classes() == 1:
            return min(min(f) for f in flattened)

    return set(min(flattened[i]) for i in e.representatives())
    #for x in e.representatives():


    #return set(chain(*levels))


def _simplify_smart(k, depth):
    """Try to simplify the diagram k in such a way, that we perform all possible R3 moves, followed by crossing
    decreasing moves, followed by crossing increasing moves, where the increasing moves are taken in such a way, that
    a new non-alternating 3-gon appears. The depth counts how many times crossing increasing moves are made in this
    process. If depth = 0, then only R3 and crossing decreasing moves are made.
    :param k: planar diagram
    :param depth: counts how many times crossing increasing moves are made
    :return: simplified diagram, if it exists, otherwise returns k
    """

    print("SMART SIMPLIFY")

    diagrams = _make_smart_reidemeister_moves_iteratively(k, depth)

    print(Counter([len(k) for k in diagrams]))

    # find the minimal diagram
    k = min(canonical(k) for k in diagrams)
    k.attr.pop("_r3", None)  # remove hidden attribute
    print("best", k)

    return k


def simultaneously_simplify_diagrams(list_of_diagrams, depth=1):
    """Check if there are any common diagrams in list_of_diagrams after performing Reidemeister moves on the diagrams.
    :param list_of_diagrams: list of planar diagrams
    :param depth: what depth to perform the Reidemeister check (number of crossing increasing moves)
    :return: list of minimal representatives of the diagrams, the list is smaller if diagrams are found ambient isotopic
    """

    groups = [_make_smart_reidemeister_moves_iteratively(k, depth) for k in list_of_diagrams]
    return [min(g) for index, g in enumerate(groups) if all(g.isdisjoint(h) for h in groups[index + 1:])]


def _simplify_non_increasing(k):
    """Try to simplify the diagram k in such a way, that we perform all possible R3 moves, followed by crossing
    decreasing moves. This is repeated until no new diagrams appear during the process.
    :param k: planar diagram
    :return: simplified diagram, if exists, otherwise returns k
    """

    levels = [{canonical(k)}]

    while levels[-1]:
        # add diagrams after all possible R3 moves from previous level
        levels.append(set(chain.from_iterable(reidemeister_3_space(k) for k in levels[-1])))
        # add also all simplified diagrams from current level
        levels[-1].update([simplify_crossing_reducing(k) for k in levels[-1]])
        # remove diagrams from previous levels
        for prev_lvl in levels[:-1]:
            levels[-1] -= prev_lvl

    # find the minimal diagram
    minimal_number_of_nodes = [len(k) for lvl in levels for k in lvl]
    minimal_diagram = min(canonical(k) for lvl in levels for k in lvl if len(k) == minimal_number_of_nodes)
    minimal_diagram.attr.pop("_r3", None)
    return minimal_diagram

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
        return _simplify_smart(k, depth)

    elif method in ["nonincreasing", "non-increasing"]:
        return _simplify_non_increasing(k)

    elif method in ["reducing", "decreaesing"]:
        return simplify_crossing_reducing(k)

    else:
        raise NotImplementedError(f"Simplification method {method} not yet implemented")


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

