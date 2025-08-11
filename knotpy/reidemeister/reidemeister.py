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
