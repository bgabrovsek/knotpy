from random import choice, shuffle
from itertools import chain
import re

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

_DEFAULT_ALLOWED_MOVES = {"R1", "R2", "R3"}
_POSSIBLE_ALLOWED_MOVES = {"R1", "R2", "R3", "FLIP"}

def _clean_allowed_moves(allowed_moves) -> set:
    """
    Validates the list of allowed Reidemeister moves.

    This function ensures that the allowed moves are properly formatted, and converted into
    a consistent form (uppercased, devoid of invalid characters, and validated against a predefined
    set of possible allowed moves). If the allowed moves are provided as a string, they are split
    into a set. If no allowed moves are provided, a default set of allowed moves is used.

    Parameters
    ----------
    allowed_moves : str | set | None
        The allowed moves to be cleaned and validated. This can be a comma-separated string,
        a set of moves, or None. None denotes that the default set of allowed moves should
        be used.

    Returns
    -------
    set
        A set of cleaned, validated, and formatted allowed moves.

    Raises
    ------
    ValueError
        If the resulting allowed moves contain items not present in the possible allowed moves.
    """

    # If no moves are given, set it at the default (R1, R2, R3)
    if allowed_moves is None:
        return set(_DEFAULT_ALLOWED_MOVES)

    # If string is given, parse from string
    if isinstance(allowed_moves, str):
        allowed_moves = set(allowed_moves.split(","))

    # Clean the set
    allowed_moves = {re.sub(r'[^A-Za-z0-9]', '', s).upper() for s in allowed_moves}
    allowed_moves = {s for s in allowed_moves if s}

    if not allowed_moves.issubset(_POSSIBLE_ALLOWED_MOVES):
        raise ValueError(f"Unknown (Reidemeister) modes {allowed_moves - _POSSIBLE_ALLOWED_MOVES}")

    return allowed_moves


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

def detect_move_type(location, detailed=False):

    # A R3 move is given by a face of length 3
    if isinstance(location, tuple) and len(location) == 3:
        return "R3" if detailed else "R3"

    # A R2 unpoke is given by a face of length 2
    elif isinstance(location, set) and len(location) == 2:
        return "R2unpoke" if detailed else "R2"

    # A R1 unkink is given by an Endpoint
    elif isinstance(location, Endpoint):
        return "R1unkink" if detailed else "R1"

    # A R2 poke is given by an ordered tuple of Endpoints
    elif isinstance(location, tuple) and len(location) == 2 and isinstance(location[0], Endpoint) and isinstance(location[1], Endpoint):
        return "R2poke" if detailed else "R2"

    # A R1 make kink is given by a tuple of (Endpoint, int)
    elif isinstance(location, tuple) and isinstance(location[0], Endpoint) and isinstance(location[1], int):
        return "R1kink" if detailed else "R1"



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
    reidemeister_move_type = detect_move_type(location, detailed=True)

    # A R3 move is given by a face of length 3
    if reidemeister_move_type == "R3":
        return reidemeister_3(k, location, inplace=inplace)
    elif reidemeister_move_type == "R2unpoke":
        return reidemeister_2_unpoke(k, location, inplace=inplace)
    elif reidemeister_move_type == "R1unkink":
        return reidemeister_1_remove_kink(k, location, inplace=inplace)
    elif reidemeister_move_type == "R2poke":
        return reidemeister_2_poke(k, location, inplace=inplace)
    elif reidemeister_move_type == "R1kink":
        return reidemeister_1_add_kink(k, location, inplace=inplace)
    else:
        raise ValueError(f"Unknown Reidemeister move type {location}")

def make_random_reidemeister_move(k, reidemeister_move_types=None, inplace=False):
    if reidemeister_move_types is None:
        reidemeister_move_types = ["R3", "R2unpoke", "R1unkink", "R2poke", "R1kink"]

    reidemeister_move_types = list(reidemeister_move_types)
    shuffle(reidemeister_move_types)

    for move_type in reidemeister_move_types:
        if move_type == "R3" and (location := choose_reidemeister_3_triangle(k, random=True)) is not None:
            return reidemeister_3(k, location, inplace=inplace)
        elif move_type == "R2unpoke" and (location := choose_reidemeister_2_unpoke(k, random=True)) is not None:
            return reidemeister_2_unpoke(k, location, inplace=inplace)
        elif move_type == "R2poke" and (location := choose_reidemeister_2_poke(k, random=True)) is not None:
            return reidemeister_2_poke(k, location, inplace=inplace)
        elif move_type == "R1kink" and (location := choose_reidemeister_1_add_kink(k, random=True)) is not None:
            return reidemeister_1_add_kink(k, location, inplace=inplace)
        elif move_type == "R1unkink" and (location := choose_reidemeister_1_remove_kink(k, random=True)) is not None:
            return reidemeister_1_remove_kink(k, location, inplace=inplace)

    return k


def randomize_diagram(k, crossing_increasing_moves=2, allowed_moves=None):
    """
    Perform random Reidemeister moves on a given diagram.

    This function modifies a diagram by applying random Reidemeister moves,
    which are transformations used in knot theory to simplify or alter the
    representation of a knot or link. The user can specify the type of moves
    to include and the number of crossing-increasing moves to perform.

    Parameters:
        k: The initial diagram to be transformed.
        crossing_increasing_moves (int): Optional; the number of crossing-increasing
            moves to perform. Default is 2.
        allowed_moves (list[str] or None): Optional; the list of allowed Reidemeister
            moves to perform on the diagram. Valid values include "R1", "R2", "R3".
            If None, all moves are allowed.

    Raises:
        ValueError: If crossing_increasing_moves is set to a value greater than 0 but
            "R2" or "R1" moves are not included in allowed_moves.

    Returns:
        The transformed diagram after applying the specified random Reidemeister moves.
    """

    from knotpy.reidemeister.space import reidemeister_3_space

    k = k.copy()

    allowed_moves = _clean_allowed_moves(allowed_moves)

    if crossing_increasing_moves > 0 and ("R2" not in allowed_moves or "R1" not in allowed_moves):
        raise ValueError("Cannot perform crossing increasing moves without R2 and R1 moves")

    # make random R3 moves
    if "R3" in allowed_moves:
        k = choice(list(reidemeister_3_space(k)))

    # check if we can decrease a crossing or two
    make_random_reidemeister_move(k, (["R1unkink"] if "R1" in allowed_moves else []) + (["R2unpoke"] if "R2" in allowed_moves else []) , inplace=True)

    if "R3" in allowed_moves:
        k = choice(list(reidemeister_3_space(k)))

    # make increasing moves
    while (crossing_increasing_moves := crossing_increasing_moves - 1) >= 0:

        make_random_reidemeister_move(k, (["R1kink"] if "R1" in allowed_moves else []) + (["R2poke"] if "R2" in allowed_moves else []), inplace=True)

        if "R3" in allowed_moves:
            k = choice(list(reidemeister_3_space(k)))

    return k


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



