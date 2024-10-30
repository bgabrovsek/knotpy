from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.canonical import canonical
from knotpy.reidemeister._abstract_reidemeister_location import ReidemeisterLocation
from knotpy.reidemeister.reidemeister_1 import (ReidemeisterLocationAddKink, ReidemeisterLocationRemoveKink,
                                                reidemeister_1_remove_kink, reidemeister_1_add_kink,
                                                choose_reidemeister_1_remove_kink, choose_reidemeister_1_add_kink,
                                                find_reidemeister_1_add_kink, find_reidemeister_1_remove_kink)
from knotpy.reidemeister.reidemeister_2 import (ReidemeisterLocationPoke, ReidemeisterLocationUnpoke,
                                                reidemeister_2_unpoke, reidemeister_2_poke,
                                                choose_reidemeister_2_unpoke, choose_reidemeister_2_poke,
                                                find_reidemeister_2_poke, find_reidemeister_2_unpoke)
from knotpy.reidemeister.reidemeister_3 import (ReidemeisterLocationThree, reidemeister_3,
                                                choose_reidemeister_3_triangle,
                                                find_reidemeister_3_triangle)


from random import randint, choice


def find_all_reidemeister_moves(k, moves=None):
    available_find_moves = {
        reidemeister_1_add_kink: find_reidemeister_1_add_kink,
        reidemeister_1_remove_kink: find_reidemeister_1_remove_kink,
        reidemeister_2_poke: find_reidemeister_2_poke,
        reidemeister_2_unpoke: find_reidemeister_2_unpoke,
        reidemeister_3: find_reidemeister_3_triangle,
    }
    moves = moves or list(available_find_moves)
    find_f = [available_find_moves[x] for x in moves]

    return [location for f in find_f for location in f(k)]  # flatten


def make_all_reidemeister_moves(k, moves=None, depth=1) -> set:
    result = [{k}, ]

    for depth_index in range(depth):
        result.append(set())
        for k in result[depth_index]:  # loop through all previous depths
            result[depth_index+1] |= {make_reidemeister_move(k, location) for location in find_all_reidemeister_moves(k, moves)}

    return {_ for s in result for _ in s}  # flatten


def random_reidemeister_moves(k, moves=None, count=1):
    """
    :param k:
    :param moves:
    :param count:
    :return:
    """

    available_choice_moves = {
        reidemeister_1_add_kink: choose_reidemeister_1_add_kink,
        reidemeister_1_remove_kink: choose_reidemeister_1_remove_kink,
        reidemeister_2_poke: choose_reidemeister_2_poke,
        reidemeister_2_unpoke: choose_reidemeister_2_unpoke,
        reidemeister_3: choose_reidemeister_3_triangle,
    }

    if moves is None:
        moves = list(available_choice_moves)

    result = [k]
    repeated = 0
    while len(result) < count + 1:
        repeated += 1
        if repeated > count * 3:
            raise ValueError("Cannot find Reidemeister moves")

        knot = choice(result)

        location = available_choice_moves[choice(moves)](knot)
        if location is not None:
            result.append(make_reidemeister_move(knot, location, inplace=False))
    return result

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



