from random import choice
from itertools import chain

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.endpoint import Endpoint
from knotpy.utils.set_utils import LeveledSet
from knotpy.algorithms.canonical import canonical
from knotpy.reidemeister.reidemeister_1 import (reidemeister_1_remove_kink, reidemeister_1_add_kink,
                                                choose_reidemeister_1_remove_kink, choose_reidemeister_1_add_kink,
                                                find_reidemeister_1_add_kink, find_reidemeister_1_remove_kink)
from knotpy.reidemeister.reidemeister_2 import (reidemeister_2_unpoke, reidemeister_2_poke,
                                                choose_reidemeister_2_unpoke, choose_reidemeister_2_poke,
                                                find_reidemeister_2_poke, find_reidemeister_2_unpoke)
from knotpy.reidemeister.reidemeister_3 import (reidemeister_3,
                                                choose_reidemeister_3_triangle,
                                                find_reidemeister_3_triangle)


def find_all_reidemeister_moves(k):
    """
    Finds all possible Reidemeister moves for a given knot diagram.

    This generator function identifies and yields all valid locations for Reidemeister
    moves that can be applied to the knot diagram `k`. The moves include:
    Reidemeister 1 (both removing and adding a kink), Reidemeister 2 (both poking
    and unpoking operations), and Reidemeister 3 (triangle moves).

    Args:
        k: The knot diagram to perform the Reidemeister moves on. The type of
            `k` is determined by the implementation of the relevant Reidemeister
            move functions.

    Yields:
        location: Represents the location of a specific type of Reidemeister
            move that can be applied to the given knot diagram `k`.

    """
    for location in chain(
        find_reidemeister_1_remove_kink(k),
        find_reidemeister_1_add_kink(k),
        find_reidemeister_2_unpoke(k),
        find_reidemeister_2_poke(k),
        find_reidemeister_3_triangle(k),
    ):
        yield location


def make_all_reidemeister_moves(k, depth=1) -> set:
    """
    Applies all possible Reidemeister moves to a knot diagram iteratively up to a specified
    depth and returns a flattened set of resulting diagrams.

    Args:
        k: Knot diagram or representation on which Reidemeister moves will be applied.
        depth: The number of levels or iterations to apply the Reidemeister moves. Defaults to 1.

    Returns:
        set: A flattened set containing all unique knot diagrams generated after applying
            Reidemeister moves up to the given depth.
    """

    ls = LeveledSet(k)

    for i in range(depth):
        ls.new_level()
        for k in ls[-2]:
            for location in find_all_reidemeister_moves(k):
                ls.add(canonical(make_reidemeister_move(k, location)))

    return set(ls)  # flatten


def choose_random_reidemeister_moves(k, count=1):
    """
    Generates a sequence of random Reidemeister moves on a given knot.

    This function selects random moves from the specified Reidemeister moves
    and applies them to the provided knot. A list containing the knot and
    all intermediate knots after the moves are made is returned. If a valid
    move cannot be found after a defined number of attempts, an error is raised.

    Args:
        k: The knot representation on which the Reidemeister moves
            will be applied.
        moves: A list of Reidemeister move functions to choose from. If not
            provided, all available types of moves will be used.
        count: The number of Reidemeister moves to perform.

    Raises:
        ValueError: If the desired number of Reidemeister moves cannot
            be found after a reasonable number of attempts.

    Returns:
        list: A list of knot representations where each represents the knot
            after a successive Reidemeister move.
    """


    available_find_functions = [
        choose_reidemeister_1_add_kink,
        choose_reidemeister_1_remove_kink,
        choose_reidemeister_2_poke,
        choose_reidemeister_2_unpoke,
        choose_reidemeister_3_triangle,
    ]

    sample = []  # result
    while len(sample) < count:
        if not available_find_functions:
            break
        f = choice(available_find_functions)  # randomly choose a random reidemeister move choose function
        location = f(k)
        if location is not None:
            sample.append(location)
        else:
            available_find_functions.remove(f)

    return sample


def make_reidemeister_move(k: PlanarDiagram, location, inplace=False):
    """
    Makes a Reidemeister move of the specified type on the given planar diagram.

    The function identifies the type of Reidemeister move based on the input
    `location`. The type of move can include Reidemeister 1 (adding or removing
    a kink), Reidemeister 2 (poke or unpoke), or Reidemeister 3. The operation
    is performed on the input planar diagram `k`. The modification can be either
    in-place or return a new modified diagram based on the value of the `inplace`
    parameter.

    Args:
        k (PlanarDiagram): The planar diagram on which the Reidemeister move
            is to be executed.
        location (Union[set, tuple, Endpoint]): Information specifying the
            type and location of the Reidemeister move. Can be:
            - A set of length 3 for R3 moves.
            - A set of length 2 for R2 unpoke moves.
            - An `Endpoint` for R1 unkink moves.
            - A tuple of length 2 containing `Endpoint` objects for R2 poke
              moves.
            - A tuple containing an `Endpoint` and an `int` for R1 make kink
              moves.
        inplace (bool): Indicates whether the operation should modify the input
            diagram `k` in-place. If False, a new modified diagram is returned.

    Returns:
        PlanarDiagram: The modified planar diagram after the specified
            Reidemeister move. If `inplace` is True, the same input diagram
            instance is returned.

    Raises:
        ValueError: If the `location` input does not correspond to a known type
            of Reidemeister move.
    """

    # Guess the Reidemeister move type.

    # A R3 move is given by a face of length 3
    if isinstance(location, tuple) and len(location) == 3:
        return reidemeister_3(k, location, inplace=inplace)

    # A R2 unpoke is given by a face of length 2
    elif isinstance(location, set) and len(location) == 2:
        return reidemeister_2_unpoke(k, location, inplace=inplace)

    # A R1 unkink is given by an Endpoint
    elif isinstance(location, Endpoint):
        return reidemeister_1_remove_kink(k, location, inplace=inplace)

    # A R2 poke is given by an ordered tuple of Endpoints
    elif isinstance(location, tuple) and len(location) == 2 and isinstance(location[0], Endpoint) and isinstance(location[1], Endpoint):
        return reidemeister_2_poke(k, location, inplace=inplace)

    # A R1 make kink is given by a tuple of (Endpoint, int)
    elif isinstance(location, tuple) and isinstance(location[0], Endpoint) and isinstance(location[1], int):
        return reidemeister_1_add_kink(k, location, inplace=inplace)

    else:
        raise ValueError(f"Unknown Reidemesiter move type {location}")

    #if we have a tuple

    # """Makes a Reidemeister move according to the type of location.
    # TODO: move this to reidemeister
    # :param k:
    # :param location:
    # :param inplace:
    # :return:
    # """
    # if type(location) is ReidemeisterLocationRemoveKink:
    #     return reidemeister_1_remove_kink(k=k, location=location, inplace=inplace)
    # elif type(location) is ReidemeisterLocationAddKink:
    #     return reidemeister_1_add_kink(k=k, location=location, inplace=inplace)
    # elif type(location) is ReidemeisterLocationUnpoke:
    #     return reidemeister_2_unpoke(k=k, location=location, inplace=inplace)
    # elif type(location) is ReidemeisterLocationPoke:
    #     return reidemeister_2_poke(k=k, location=location, inplace=inplace)
    # elif type(location) is ReidemeisterLocationThree:
    #     return reidemeister_3(k=k, location=location, inplace=inplace)
    # else:
    #     raise ValueError(f"Unknown Reidemesiter location {location}")



