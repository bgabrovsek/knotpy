# knotpy/reidemeister/detour.py
"""
Detour moves.

A detour move is a move where a strand passes through multiple other strands.
This module provides helpers that *locate* useful detour opportunities by
looking for configurations that can be realized immediately via a sequence of
Reidemeister moves (R1/R2/R3 or R4 slides), and a small dispatcher that
executes the corresponding move.

Notes
-----
- We preserve your original logic and comments closely.
- Returned locations are suitable for `reidemeister_2_poke` or `reidemeister_4_slide`,
  depending on the pattern found.
"""

from __future__ import annotations

from knotpy._settings import settings
from knotpy.classes.planardiagram import Diagram  # PlanarDiagram | OrientedPlanarDiagram
from knotpy.classes.node import Crossing
from knotpy.classes.endpoint import Endpoint
from knotpy.reidemeister.reidemeister_2 import reidemeister_2_poke
from knotpy.reidemeister.reidemeister_4 import (
    find_reidemeister_4_slide,
    reidemeister_4_slide,
)


def detour_find_reidemeister_1_add_kinks_bigon(k: Diagram):
    """Find positions for R1 moves next to an **alternating** 2-region (bigon).

    After such an R1 move, a non-alternating triangle (3-gon) is created, so
    that a subsequent R3 move can be performed.

    This scans all 2-faces whose two endpoints are crossings and have the same
    position parity (both over or both under). For each such bigon, it yields
    the twin endpoints together with the required kink sign.

    Args:
        k (Diagram): Diagram to analyze.

    Return:
        iterator: Yields pairs ``(endpoint, sign)`` where ``sign`` is ``+1`` or
        ``-1`` depending on the local parity configuration.

    Notes:
        - Could be optimized to only add a kink where we have two overstrands,
          so there is a possibility to reduce it (we cannot reduce alternating diagrams).
    """
    if "R1" not in settings.allowed_moves:
        return

    # loop through all faces and create R1 moves where the bigons have same position parity
    for face in k.faces:
        if (
            len(face) == 2
            and all(isinstance(k.nodes[ep.node], Crossing) for ep in face)
            and face[0].position % 2 == face[1].position % 2
        ):
            yield k.twin(face[0]), (-1 if face[0].position % 2 else 1)
            yield k.twin(face[1]), (-1 if face[1].position % 2 else 1)


def detour_find_reidemeister_2_pokes_n_gon(k: Diagram):
    """Find positions of R2 pokes inside a region that create a **non-alternating** triangle.

    After the R2 move, a non-alternating 3-gon should appear so we can perform an R3 move.

    Args:
        k (Diagram): Diagram to analyze.

    Return:
        iterator: Yields ordered endpoint pairs ``(under_ep, over_ep)`` suitable
        for `reidemeister_2_poke`.

    Details:
        - We iterate all faces. If any endpoint’s node in the face is not a crossing,
          skip (the intended patterns here are all-crossing boundaries).
        - If the face is a triangle and fully alternating (all three parities equal),
          or if the face has length ≥ 4, we consider local triples around the cycle
          and produce one or two (under, over) poke options depending on local parity.
    """
    if "R2" not in settings.allowed_moves:
        return

    # loop through all faces with length > 3 and create R3 moves
    for face in k.faces:
        if any(type(k.nodes[ep.node]) is not Crossing for ep in face):
            # TODO maybe the ones where we make R2 can only be crossings
            continue

        if ((len(face) == 3 and (face[0].position % 2 == face[1].position % 2 == face[2].position % 2))
                or len(face) >= 4):
            for i in range(len(face)):
                ep_a, ep_b, ep_c = face[i], face[(i + 1) % len(face)], face[(i + 2) % len(face)]

                if (ep_a.position % 2) != (ep_b.position % 2):
                    # we have an over/under strand between a and b, so any poke is ok
                    # both pokes (order matters: (under, over) and its swap)
                    # TODO: check if over/under order is correct
                    yield ep_a, ep_c
                    yield ep_c, ep_a
                elif ep_a.position % 2 == ep_b.position % 2 == 1:
                    yield ep_c, ep_a  # c is under, a is over
                elif ep_a.position % 2 == ep_b.position % 2 == 0:
                    yield ep_a, ep_b  # a is under, b is over


def find_detour_moves(k: Diagram):
    """Find all detour moves for a diagram.

    This aggregates candidate locations for:
      - R2 pokes inside faces that could create a non-alternating triangle, and
      - R4 slides (restricted to those that increase crossings, per the original intent).

    Args:
        k (Diagram): Diagram to analyze.

    Return:
        iterator: Yields move “locations”, i.e. arguments that can be passed to
        a specific move function:
          - For R2 pokes: ordered endpoint pairs ``(Endpoint, Endpoint)``.
          - For R4 slides: pairs ``(vertex, positions_list)`` returned
            by `find_reidemeister_4_slide`.
    """
    # Do not use R1 increasing moves for simplification
    # Add kinks
    # if "R1" in settings.allowed_moves and settings.r1_increase_simplification:
    #     for ep_sign in detour_find_reidemeister_1_add_kinks_bigon(k):
    #         yield ep_sign

    # Add R2 pokes
    if "R2" in settings.allowed_moves:
        for face in detour_find_reidemeister_2_pokes_n_gon(k):
            yield face

    if "R4" in settings.allowed_moves:
        for v_pos in find_reidemeister_4_slide(k, change="increasing"):
            yield v_pos

    # TODO: can twisting the knotted graph via R5 yield an essential configuration?


def detour_move(k: Diagram, location, inplace: bool = False):
    """Make the detour move at the given location.

    Dispatch:
      - If `location` is a pair of `Endpoint`s → perform R2 poke.
      - If `location` is `(vertex, positions_list)` → perform R4 slide.

    Args:
        k (Diagram): Diagram to modify (copied if `inplace=False`).
        location: A move location yielded by `find_detour_moves` (see Dispatch above).
        inplace (bool): If True, mutate `k`; otherwise work on a copy.

    Return:
        Diagram: The diagram after applying the requested detour move.
    """
    # Is the move an R2 poke?
    if (
        isinstance(location, tuple)
        and len(location) == 2
        and isinstance(location[0], Endpoint)
        and isinstance(location[1], Endpoint)
    ):
        return reidemeister_2_poke(k, location, inplace=inplace)

    # Is the move an R4 slide? (location = (vertex, positions_list))
    if (
        isinstance(location, tuple)
        and len(location) == 2
        and isinstance(location[1], list)
    ):
        return reidemeister_4_slide(k, location, inplace=inplace)

    # If location is of an unsupported shape, just return k unchanged.
    return k