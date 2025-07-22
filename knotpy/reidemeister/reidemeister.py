from collections.abc import Iterable
from random import shuffle

from knotpy._settings import settings
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.utils.set_utils import LeveledSet
from knotpy.reidemeister.reidemeister_1 import (reidemeister_1_remove_kink, reidemeister_1_add_kink,
                                                choose_reidemeister_1_remove_kink, choose_reidemeister_1_add_kink,
                                                find_reidemeister_1_add_kink, find_reidemeister_1_remove_kink)
from knotpy.reidemeister.reidemeister_2 import (reidemeister_2_unpoke, reidemeister_2_poke,
                                                choose_reidemeister_2_unpoke, choose_reidemeister_2_poke,
                                                find_reidemeister_2_poke, find_reidemeister_2_unpoke)
from knotpy.reidemeister.reidemeister_3 import (reidemeister_3, choose_reidemeister_3_triangle, find_reidemeister_3_triangle)
from knotpy.reidemeister.reidemeister_4 import (reidemeister_4_slide, choose_reidemeister_4_slide, find_reidemeister_4_slide)
from knotpy.reidemeister.reidemeister_5 import (reidemeister_5_twist, reidemeister_5_untwist,
                                                choose_reidemeister_5_untwist, choose_reidemeister_5_twist,
                                                find_reidemeister_5_twists, find_reidemeister_5_untwists)
from knotpy.reidemeister.flype import find_flypes, choose_flype, flype
from knotpy.reidemeister.detour import detour_move, find_detour_moves


def r1_remove_kink_generator(diagrams: PlanarDiagram | OrientedPlanarDiagram | Iterable):
    """Generate all R1 remove kinks and return new diagrams."""
    if isinstance(diagrams, PlanarDiagram):
        diagrams = (diagrams, )

    for k in diagrams:
        for ep in find_reidemeister_1_remove_kink(k):
            yield reidemeister_1_remove_kink(k, ep, inplace=False)


def r1_add_kink_generator(diagrams: PlanarDiagram | OrientedPlanarDiagram | Iterable):
    """Generate all R1 add kinks and return new diagrams."""
    if isinstance(diagrams, PlanarDiagram):
        diagrams = (diagrams, )
    for k in diagrams:
        for ep_sign in find_reidemeister_1_add_kink(k):
            yield reidemeister_1_add_kink(k, ep_sign, inplace=False)


def r2_poke_generator(diagrams: PlanarDiagram | OrientedPlanarDiagram | Iterable):
    """Generate all R2 poke moves and return new diagrams."""
    if isinstance(diagrams, PlanarDiagram):
        diagrams = (diagrams, )
    for k in diagrams:
        for eps in find_reidemeister_2_poke(k):
            yield reidemeister_2_poke(k, eps, inplace=False)


def r2_unpoke_generator(diagrams: PlanarDiagram | OrientedPlanarDiagram | Iterable):
    """Generate all R2 unpoke moves and return new diagrams."""
    if isinstance(diagrams, PlanarDiagram):
        diagrams = (diagrams, )
    for k in diagrams:
        for face in find_reidemeister_2_unpoke(k):
            yield reidemeister_2_unpoke(k, face, inplace=False)


def r3_generator(diagrams: PlanarDiagram | OrientedPlanarDiagram | Iterable):
    """Generate all R3 moves and return new diagrams."""
    if isinstance(diagrams, PlanarDiagram):
        diagrams = (diagrams, )
    for k in diagrams:
        for face in find_reidemeister_3_triangle(k):
            if any("_r3" not in k.nodes[ep.node].attr for ep in face):
                yield reidemeister_3(k, face, inplace=False)


def r4_generator(diagrams: PlanarDiagram | OrientedPlanarDiagram | Iterable, change="any"):
    """Generate all R4 preserving moves and return new diagrams."""
    if isinstance(diagrams, PlanarDiagram):
        diagrams = (diagrams, )
    for k in diagrams:
        for v_pos in find_reidemeister_4_slide(k, change):
            yield reidemeister_4_slide(k, v_pos, inplace=False)


def r5_untwist_generator(diagrams: PlanarDiagram | OrientedPlanarDiagram | Iterable):
    """Generate all R5 untwist moves and return new diagrams."""
    if isinstance(diagrams, PlanarDiagram):
        diagrams = (diagrams, )
    for k in  diagrams:
        for face in find_reidemeister_5_untwists(k):
            yield reidemeister_5_untwist(k, face, inplace=False)


def r5_twist_generator(diagrams: PlanarDiagram | OrientedPlanarDiagram | Iterable):
    """Generate all R5 twist moves and return new diagrams."""
    if isinstance(diagrams, PlanarDiagram):
        diagrams = (diagrams, )
    for k in diagrams:
        for eps in find_reidemeister_5_twists(k):
            yield reidemeister_5_twist(k, eps, inplace=False)


def detour_generator(diagrams: PlanarDiagram | OrientedPlanarDiagram | Iterable):
    """Generate all R5 twist moves and return new diagrams."""
    if isinstance(diagrams, PlanarDiagram):
        diagrams = (diagrams, )
    for k in diagrams:
        for location in find_detour_moves(k):
            yield detour_move(k, location, inplace=False)


def flype_generator(diagrams: PlanarDiagram | OrientedPlanarDiagram | Iterable):
    """Generate all flypes and returns new diagrams."""
    if isinstance(diagrams, PlanarDiagram):
        diagrams = (diagrams, )
    for k in diagrams:
        for pair in find_flypes(k):
            yield flype(k, pair, inplace=False)


def reidemeister_moves_generator(diagrams: PlanarDiagram | OrientedPlanarDiagram | Iterable):
    """Generate all Reidemeister moves and return new diagrams."""
    if isinstance(diagrams, PlanarDiagram):
        diagrams = (diagrams, )

    # Iterate over diagrams to avoid exhausting the generator.
    for k in diagrams:
        k = (k,)
        yield from r1_remove_kink_generator(k)
        yield from r1_add_kink_generator(k)
        yield from r2_unpoke_generator(k)
        yield from r2_poke_generator(k)
        yield from r3_generator(k)
        yield from r4_generator(k)
        yield from r5_untwist_generator(k)
        yield from r5_twist_generator(k)
        #yield from flype_generator(k)


def reidemeister_decreasing_moves_generator(diagrams: PlanarDiagram | OrientedPlanarDiagram | Iterable):
    """Generate all Reidemeister moves that increase the number of crissings and return new diagrams."""

    if isinstance(diagrams, PlanarDiagram):
        diagrams = (diagrams, )

    # Iterate over diagrams to avoid exhausting the generator.
    for k in diagrams:
        k = (k,)
        yield from r1_remove_kink_generator(k)
        yield from r2_unpoke_generator(k)
        yield from r4_generator(k, change="decrease")
        yield from r5_untwist_generator(k)



def reidemeister_increasing_moves_generator(diagrams: PlanarDiagram | OrientedPlanarDiagram | Iterable):
    """Generate all Reidemeister moves that increase the number of crissings and return new diagrams."""
    if isinstance(diagrams, PlanarDiagram):
        diagrams = (diagrams, )

    # Iterate over diagrams to avoid exhausting the generator.
    for k in diagrams:
        k = (k, )
        yield from r1_add_kink_generator(k)
        yield from r2_poke_generator(k)
        yield from r4_generator(k, change="increase")
        yield from r5_twist_generator(k)


def reidemeister_preserving_moves_generator(diagrams: PlanarDiagram | OrientedPlanarDiagram | Iterable):
    """Generate all Reidemeister moves that increase the number of crossings and return new diagrams."""
    if isinstance(diagrams, PlanarDiagram):
        diagrams = (diagrams, )

    d = set(diagrams)

    yield from r3_generator(d)
    yield from r4_generator(d, change="preserve")
    #yield from flype_generator(d)

    return None
    # Iterate over diagrams to avoid exhausting the generator.
    for k in diagrams:
        k = (k, )
        yield from r3_generator(k)
        yield from r4_generator(k, change="preserve")
        #yield from flype_generator(k)


def all_reidemeister_moves(diagrams: PlanarDiagram | OrientedPlanarDiagram | Iterable, depth=1) -> set:
    """ Make all possible Reidemeister moves on a diagram."""
    if isinstance(diagrams, PlanarDiagram):
        diagrams = (diagrams, )

    ls = LeveledSet(diagrams)
    for _depth in range(depth):
        ls.new_level(reidemeister_moves_generator(ls.iter_level(-1)))
    return set(ls)


def random_reidemeister_move(k: PlanarDiagram | OrientedPlanarDiagram, allow_increase=True, inplace=False):
    """
    Performs a random Reidemeister move on a given planar diagram.

    Args:
        k (PlanarDiagram | OrientedPlanarDiagram): The planar diagram on which to perform the Reidemeister move.
        allow_increase (str, optional): Allow to increase the number of crossings. Defaults to True.
        inplace (bool, optional): Determines whether the move alters the original diagram or creates a new instance. Defaults to False.

    Returns:
        PlanarDiagram | OrientedPlanarDiagram | None: The modified planar diagram after
            applying the move. Returns None if no applicable move is performed.

    Raises:
        ValueError: If an unknown move type is encountered.
    """

    move_choices = []
    if "R1" in settings.allowed_moves:
        move_choices += ["r1r","r1a"] if allow_increase else ["r1r"] # remove kink (unkink), add kink (kink)
    if "R2" in settings.allowed_moves:
        move_choices += ["r2u","r2p"] if allow_increase else ["r2u"]  # unpoke, poke
    if "R3" in settings.allowed_moves:
        move_choices += ["r3"]
    if "R4" in settings.allowed_moves:
        move_choices += ["r4"]
    if "R5" in settings.allowed_moves:
        move_choices += ["r5u","r5t"] if allow_increase else ["r5u"] # twist, untwist
    # if "FLYPE" in settings.allowed_moves:
    #     move_choices += ["f"]
    # TODO: do we need FLIP?

    shuffle(move_choices)

    for move in move_choices:
        match move:
            case "r1r":
                if ep := choose_reidemeister_1_remove_kink(k, random=True):
                    return reidemeister_1_remove_kink(k, ep, inplace=inplace)
            case "r1a":
                if ep_sign := choose_reidemeister_1_add_kink(k, random=True):
                    return reidemeister_1_add_kink(k, ep_sign, inplace=inplace)
            case "r2u":
                if face := choose_reidemeister_2_unpoke(k, random=True):
                    return reidemeister_2_unpoke(k, face, inplace=inplace)
            case "r2p":
                if face := choose_reidemeister_2_poke(k, random=True):
                    return reidemeister_2_poke(k, face, inplace=inplace)
            case "r3":
                if face := choose_reidemeister_3_triangle(k, random=True):
                    return reidemeister_3(k, face, inplace=inplace)
            case "r4":
                if v_pos := choose_reidemeister_4_slide(k, change="any" if allow_increase else "nonincreasing", random=True):
                    return reidemeister_4_slide(k, v_pos, inplace=inplace)
            case "r5u":
                if face := choose_reidemeister_5_untwist(k, random=True):
                    return reidemeister_5_untwist(k, face, inplace=inplace)
            case "r5t":
                if eps := choose_reidemeister_5_twist(k, random=True):
                    return reidemeister_5_twist(k, eps, inplace=inplace)
            # case "f":
            #     if part_ep := choose_flype(k, random=True):
            #         return flype(k, part_ep, inplace=inplace)
            case _:
                raise ValueError(f"Unknown move type {move}")

def randomize_diagram(k, number_of_moves=5, max_crossings_increase=2):
    max_nodes = len(k) + max_crossings_increase

    k = k.copy()

    for _ in range(number_of_moves):
        random_reidemeister_move(k, allow_increase=len(k) < max_nodes, inplace=True)

    return k




#
# def find_all_reidemeister_moves(k):
#     """
#     Finds all possible Reidemeister moves for a given knot diagram.
#
#     This generator function identifies and yields all valid locations for Reidemeister
#     moves that can be applied to the knot diagram `k`. The moves include:
#     Reidemeister 1 (both removing and adding a kink), Reidemeister 2 (both poking
#     and unpoking operations), and Reidemeister 3 (triangle moves).
#
#     Args:
#         k: The knot diagram to perform the Reidemeister moves on. The type of
#             `k` is determined by the implementation of the relevant Reidemeister
#             move functions.
#
#     Yields:
#         location: Represents the location of a specific type of Reidemeister
#             move that can be applied to the given knot diagram `k`.
#
#     """
#     for location in chain(
#         find_reidemeister_1_remove_kink(k),
#         find_reidemeister_1_add_kink(k),
#         find_reidemeister_2_unpoke(k),
#         find_reidemeister_2_poke(k),
#         find_reidemeister_3_triangle(k),
#     ):
#         yield location
#
#
# def make_all_reidemeister_moves(k, depth=1) -> set:
#     """
#     Applies all possible Reidemeister moves to a knot diagram iteratively up to a specified
#     depth and returns a flattened set of resulting diagrams.
#
#     Args:
#         k: Knot diagram or representation on which Reidemeister moves will be applied.
#         depth: The number of levels or iterations to apply the Reidemeister moves. Defaults to 1.
#
#     Returns:
#         set: A flattened set containing all unique knot diagrams generated after applying
#             Reidemeister moves up to the given depth.
#     """
#
#     ls = LeveledSet(k)
#
#     for i in range(depth):
#         ls.new_level()
#         for k in ls[-2]:
#             for location in find_all_reidemeister_moves(k):
#                 ls.add(canonical(make_reidemeister_move(k, location)))
#
#     return set(ls)  # flatten
#
#
# def choose_random_reidemeister_moves(k, count=1):
#     """
#     Generates a sequence of random Reidemeister moves on a given knot.
#
#     This function selects random moves from the specified Reidemeister moves
#     and applies them to the provided knot. A list containing the knot and
#     all intermediate knots after the moves are made is returned. If a valid
#     move cannot be found after a defined number of attempts, an error is raised.
#
#     Args:
#         k: The knot representation on which the Reidemeister moves
#             will be applied.
#         moves: A list of Reidemeister move functions to choose from. If not
#             provided, all available types of moves will be used.
#         count: The number of Reidemeister moves to perform.
#
#     Raises:
#         ValueError: If the desired number of Reidemeister moves cannot
#             be found after a reasonable number of attempts.
#
#     Returns:
#         list: A list of knot representations where each represents the knot
#             after a successive Reidemeister move.
#     """
#
#
#     available_find_functions = [
#         choose_reidemeister_1_add_kink,
#         choose_reidemeister_1_remove_kink,
#         choose_reidemeister_2_poke,
#         choose_reidemeister_2_unpoke,
#         choose_reidemeister_3_triangle,
#     ]
#
#     sample = []  # result
#     while len(sample) < count:
#         if not available_find_functions:
#             break
#         f = choice(available_find_functions)  # randomly choose a random reidemeister move choose function
#         location = f(k)
#         if location is not None:
#             sample.append(location)
#         else:
#             available_find_functions.remove(f)
#
#     return sample
#
# def detect_move_type(location, detailed=False):
#
#     # A R3 move is given by a face of length 3
#     if isinstance(location, tuple) and len(location) == 3:
#         return "R3" if detailed else "R3"
#
#     # A R2 unpoke is given by a face of length 2
#     elif isinstance(location, set) and len(location) == 2:
#         return "R2unpoke" if detailed else "R2"
#
#     # A R1 unkink is given by an Endpoint
#     elif isinstance(location, Endpoint):
#         return "R1unkink" if detailed else "R1"
#
#     # A R2 poke is given by an ordered tuple of Endpoints
#     elif isinstance(location, tuple) and len(location) == 2 and isinstance(location[0], Endpoint) and isinstance(location[1], Endpoint):
#         return "R2poke" if detailed else "R2"
#
#     # A R1 make kink is given by a tuple of (Endpoint, int)
#     elif isinstance(location, tuple) and isinstance(location[0], Endpoint) and isinstance(location[1], int):
#         return "R1kink" if detailed else "R1"
#
#     elif isinstance(location, tuple) and len(location) == 2 and isinstance(location[1], list):
#         return "R4"
#
#     # TODO: R5
#
#
#
# def make_reidemeister_move(k: PlanarDiagram, location, inplace=False):
#     """
#     Makes a Reidemeister move of the specified type on the given planar diagram.
#
#     The function identifies the type of Reidemeister move based on the input
#     `location`. The type of move can include Reidemeister 1 (adding or removing
#     a kink), Reidemeister 2 (poke or unpoke), or Reidemeister 3. The operation
#     is performed on the input planar diagram `k`. The modification can be either
#     in-place or return a new modified diagram based on the value of the `inplace`
#     parameter.
#
#     Args:
#         k (PlanarDiagram): The planar diagram on which the Reidemeister move
#             is to be executed.
#         location (Union[set, tuple, Endpoint]): Information specifying the
#             type and location of the Reidemeister move. Can be:
#             - A set of length 3 for R3 moves.
#             - A set of length 2 for R2 unpoke moves.
#             - An `Endpoint` for R1 unkink moves.
#             - A tuple of length 2 containing `Endpoint` objects for R2 poke
#               moves.
#             - A tuple containing an `Endpoint` and an `int` for R1 make kink
#               moves.
#         inplace (bool): Indicates whether the operation should modify the input
#             diagram `k` in-place. If False, a new modified diagram is returned.
#
#     Returns:
#         PlanarDiagram: The modified planar diagram after the specified
#             Reidemeister move. If `inplace` is True, the same input diagram
#             instance is returned.
#
#     Raises:
#         ValueError: If the `location` input does not correspond to a known type
#             of Reidemeister move.
#     """
#
#     # Guess the Reidemeister move type.
#     reidemeister_move_type = detect_move_type(location, detailed=True)
#
#     # A R3 move is given by a face of length 3
#     if reidemeister_move_type == "R3":
#         return reidemeister_3(k, location, inplace=inplace)
#     elif reidemeister_move_type == "R2unpoke":
#         return reidemeister_2_unpoke(k, location, inplace=inplace)
#     elif reidemeister_move_type == "R1unkink":
#         return reidemeister_1_remove_kink(k, location, inplace=inplace)
#     elif reidemeister_move_type == "R2poke":
#         return reidemeister_2_poke(k, location, inplace=inplace)
#     elif reidemeister_move_type == "R1kink":
#         return reidemeister_1_add_kink(k, location, inplace=inplace)
#     else:
#         raise ValueError(f"Unknown Reidemeister move type {location}")
#
# def make_random_reidemeister_move(k, reidemeister_move_types=None, inplace=False):
#
#     _DEBUG = False
#
#     if reidemeister_move_types is None:
#         reidemeister_move_types = ["R3", "R2unpoke", "R1unkink", "R2poke", "R1kink", "R4any"]
#
#     reidemeister_move_types = list(reidemeister_move_types)
#     shuffle(reidemeister_move_types)
#
#     for move_type in reidemeister_move_types:
#
#         if move_type == "R3" and (location := choose_reidemeister_3_triangle(k, random=True)) is not None:
#             if _DEBUG: print("R3", location)
#             return reidemeister_3(k, location, inplace=inplace)
#
#         elif move_type == "R2unpoke" and (location := choose_reidemeister_2_unpoke(k, random=True)) is not None:
#             if _DEBUG: print("R2 unpoke", location)
#             return reidemeister_2_unpoke(k, location, inplace=inplace)
#
#         elif move_type == "R2poke" and (location := choose_reidemeister_2_poke(k, random=True)) is not None:
#             if _DEBUG: print("R2 poke", location)
#             return reidemeister_2_poke(k, location, inplace=inplace)
#
#         elif move_type == "R1kink" and (location := choose_reidemeister_1_add_kink(k, random=True)) is not None:
#             if _DEBUG: print("R1 kink", location)
#             return reidemeister_1_add_kink(k, location, inplace=inplace)
#
#         elif move_type == "R1unkink" and (location := choose_reidemeister_1_remove_kink(k, random=True)) is not None:
#             if _DEBUG: print("R1 unkink", location)
#             return reidemeister_1_remove_kink(k, location, inplace=inplace)
#
#         elif move_type == "R5untwist" and (location := choose_reidemeister_5_untwist(k, random=True)) is not None:
#             if _DEBUG: print("R5 untwist", location)
#             return reidemeister_5_untwist(k, location, inplace=inplace)
#
#         elif move_type == "R5twist" and (location := choose_reidemeister_5_twist(k, random=True)) is not None:
#             if _DEBUG: print("R5 twist", location)
#             return reidemeister_5_twist(k, location, inplace=inplace)
#
#         elif move_type[:2] == "R4" and (location := choose_reidemeister_4_slide(k, change=move_type[2:], random=True)) is not None:
#             if _DEBUG: print("R4", location)
#             return reidemeister_4_slide(k, location, inplace=inplace)
#
#
#     return k
#
#
# def randomize_diagram(k, crossing_increasing_moves=2):
#     """
#     Perform random Reidemeister moves on a given diagram.
#
#     This function modifies a diagram by applying random Reidemeister moves,
#     which are transformations used in knot theory to simplify or alter the
#     representation of a knot or link. The user can specify the type of moves
#     to include and the number of crossing-increasing moves to perform.
#
#     Parameters:
#         k: The initial diagram to be transformed.
#         crossing_increasing_moves (int): Optional; the number of crossing-increasing
#             moves to perform. Default is 2.
#
#     Raises:
#         ValueError: If crossing_increasing_moves is set to a value greater than 0 but
#             "R2" or "R1" moves are not included in settings.allowed_moves.
#
#     Returns:
#         The transformed diagram after applying the specified random Reidemeister moves.
#     """
#
#     from knotpy.reidemeister.space import crossing_preserving_space
#
#
#     k = k.copy()
#
#     if crossing_increasing_moves > 0 and ("R2" not in settings.allowed_moves or "R1" not in settings.allowed_moves):
#         raise ValueError("Cannot perform crossing increasing moves without R2 and R1 moves")
#
#     # make random R3 moves
#     if "R3" in settings.allowed_moves:
#         k = choice(list(crossing_preserving_space(k)))
#
#     #sanity_check(k)
#
#     # check if we can decrease a crossing or two
#     decreasing_moves_allowed = []
#     if "R1" in settings.allowed_moves: decreasing_moves_allowed.append("R1unkink")
#     if "R2" in settings.allowed_moves: decreasing_moves_allowed.append("R2unpoke")
#     if "R4" in settings.allowed_moves: decreasing_moves_allowed.append("R4nonincreasing")
#     if "R5" in settings.allowed_moves: decreasing_moves_allowed.append("R5untwist")
#
#     make_random_reidemeister_move(k, decreasing_moves_allowed, inplace=True)
#     #sanity_check(k)
#
#     if "R3" in settings.allowed_moves:
#         k = choice(list(crossing_preserving_space(k)))
#
#     # make increasing moves
#     while (crossing_increasing_moves := crossing_increasing_moves - 1) >= 0:
#
#         increasing_moves_allowed = []
#         if "R1" in settings.allowed_moves: increasing_moves_allowed.append("R1kink")
#         if "R2" in settings.allowed_moves: increasing_moves_allowed.append("R2poke")
#         if "R4" in settings.allowed_moves: increasing_moves_allowed.append("R4increase")
#         if "R5" in settings.allowed_moves: increasing_moves_allowed.append("R5twist")
#
#         #print(increasing_moves_allowed)
#         from knotpy import yamada_polynomial
#         #print("MRRM 0", k, "  ", yamada_polynomial(k), increasing_moves_allowed)
#
#         k = make_random_reidemeister_move(k, increasing_moves_allowed, inplace=False)
#         #make_random_reidemeister_move(k, increasing_moves_allowed, inplace=True)
#
#         #print("MRRM 1", k, "  ", yamada_polynomial(k))
#         #sanity_check(k)
#
#
#         if "R3" in settings.allowed_moves:
#             k = choice(list(crossing_preserving_space(k)))
#         #sanity_check(k)
#
#     return k
#
#
#     #if we have a tuple
#
#     # """Makes a Reidemeister move according to the type of location.
#     # TODO: move this to reidemeister
#     # :param k:
#     # :param location:
#     # :param inplace:
#     # :return:
#     # """
#     # if type(location) is ReidemeisterLocationRemoveKink:
#     #     return reidemeister_1_remove_kink(k=k, location=location, inplace=inplace)
#     # elif type(location) is ReidemeisterLocationAddKink:
#     #     return reidemeister_1_add_kink(k=k, location=location, inplace=inplace)
#     # elif type(location) is ReidemeisterLocationUnpoke:
#     #     return reidemeister_2_unpoke(k=k, location=location, inplace=inplace)
#     # elif type(location) is ReidemeisterLocationPoke:
#     #     return reidemeister_2_poke(k=k, location=location, inplace=inplace)
#     # elif type(location) is ReidemeisterLocationThree:
#     #     return reidemeister_3(k=k, location=location, inplace=inplace)
#     # else:
#     #     raise ValueError(f"Unknown Reidemesiter location {location}")
#
#
# if __name__ == "__main__":
#     from knotpy.notation.native import from_knotpy_notation
#     from knotpy.invariants import yamada_polynomial
#
#     """
#     MRRM 0 Diagram named +t3_1 a → V(b0 c0 d3), b → V(a0 d2 e3), c → X(a1 c2 c1 f0), d → X(f3 e0 b1 a2), e → X(d1 f2 f1 b2), f → X(c3 e2 e1 d0) (_sequence=R1)    A**11 + A**10 + A**9 - A**8 - 2*A**7 - 4*A**6 - 3*A**5 - 2*A**4 + A**2 + A + 1 ['R1kink', 'R2poke', 'R4increase', 'R5twist']
# R4 ('b', [1])
# MRRM 1 Diagram named +t3_1 a → V(j2 c0 j3), b → V(j0 f3 i0), c → X(a1 c2 c1 f0), e → X(i1 f2 f1 i2), f → X(c3 e2 e1 b1), i → X(b2 e0 e3 j1), j → X(b0 i3 a0 a2) (_sequence=R1R4)    -A**10 - 2*A**9 - 4*A**8 - 3*A**7 - 3*A**6 + A**4 + 2*A**3 + 2*A**2 + A + 1
#     """
#     k1 = from_knotpy_notation("a → V(b0 c0 d3), b → V(a0 d2 e3), c → X(a1 c2 c1 f0), d → X(f3 e0 b1 a2), e → X(d1 f2 f1 b2), f → X(c3 e2 e1 d0)")
#     k2 = from_knotpy_notation("a → V(j2 c0 j3), b → V(j0 f3 i0), c → X(a1 c2 c1 f0), e → X(i1 f2 f1 i2), f → X(c3 e2 e1 b1), i → X(b2 e0 e3 j1), j → X(b0 i3 a0 a2)")
#     print(yamada_polynomial(k1))
#     print(yamada_polynomial(k2))