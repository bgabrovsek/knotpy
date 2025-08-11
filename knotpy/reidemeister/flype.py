# knotpy/reidemeister/flype.py
"""
Flype move detection and execution.

A **flype** is a local move on a knotted diagram that transforms a tangle
positioned near a twist region (crossing or half-twist) by rotating part of
the diagram 180° around an axis perpendicular to the projection plane.

This module provides:
- Detection of flype locations via arc cut sets and parity checks;
- A `flype` operation that rewires endpoints and flips the chosen subdiagram.

Notes
-----
- Logic is intentionally kept identical to your working version.
- No `typing` module imports are used (Python 3.10 unions are fine).
"""

from __future__ import annotations

import warnings
from random import choice
from itertools import product
from collections import Counter

from knotpy.classes.planardiagram import Diagram  # PlanarDiagram | OrientedPlanarDiagram
from knotpy.classes.node import Crossing
from knotpy.algorithms.cut_set import arc_cut_sets
from knotpy.algorithms.symmetry import flip
from knotpy._settings import settings


def _path_within_crossings(k: Diagram, nodes: list | set, endpoint):
    """Follow the strand of `endpoint` until we reach a node not in `nodes`.

    This iteratively traces the path starting from the provided endpoint, jumping
    through twins and across crossings (the “+2” next position on a crossing),
    but only as long as the next node remains within the given `nodes` set. The
    traversal terminates as soon as an external node is encountered or a
    non-crossing node is reached.

    Args:
        k (Diagram): The diagram.
        nodes (list | set): Allowed nodes for traversal. Traversal halts when a node
            outside this collection is reached.
        endpoint: Starting endpoint (must belong to one of `nodes`).

    Return:
        list: The list of node labels (in order) visited along the path.

    Raises:
        ValueError: If `endpoint.node` is not in `nodes`.
    """
    if endpoint.node not in nodes:
        raise ValueError("Endpoint not in nodes")

    # print(f"path from endpoint {endpoint} within nodes {nodes}")

    path = [endpoint]
    while True:
        jump = k.twin((path[-1].node, (path[-1].position + 2) % 4))
        if jump.node not in nodes:
            break
        path.append(jump)
        # Keep the exact semantics: only continue through *crossings* (not subclasses).
        if not type(k.nodes[jump.node]) is Crossing:
            break
    return [ep.node for ep in path]


def _is_integer_tangle_cut(k: Diagram, partition: set, endpoints):
    """Check if the tangle cut by `partition` is an integer tangle.

    Two endpoints produce an integer tangle if following their strands within
    the partition yields identical node paths.
    """
    return _path_within_crossings(k, partition, endpoints[0]) == _path_within_crossings(k, partition, endpoints[1])


def find_flypes(k: Diagram):
    """
    Find all flype positions. A flype is given by a list of four endpoints, where the endpoints form an arc-cut set.
    The first two endpoints are in the same crossing and the obtained tangle by cutting the arcs of the endpoints is
    not integer.

    A flype is a local move on a knotted diagram that transforms a tangle positioned near a twist region
    (crossing or half-twist) by rotating part of the diagram 180° around an axis perpendicular to the projection plane.

    Args:
        k: A planar or oriented planar diagram representing a knot diagram
           where potential flype positions need to be located.

    Return:
        iterator: Yields pairs `(partition, endpoints_quadruple)` representing valid flype locations.
    """
    if "FLYPE" not in settings.allowed_moves:
        return

    for arcs, partition_, ccw_endpoints_ in arc_cut_sets(
        k,
        order=4,
        minimum_partition_nodes=2,
        return_partition=True,
        return_ccw_ordered_endpoints=True,
    ):
        # If three endpoints are connected to one crossing, this is not a valid flype.
        if max(Counter(ep.node for eps in ccw_endpoints_ for ep in eps).values()) > 2:
            continue

        # Loop through both sides of the cut and four rotations of the cyclic order.
        for index, rotation in product(range(2), range(4)):
            partition = partition_[index]

            # Optionally restrict to flypes where the interior consists solely of crossings.
            if settings.flype_crossings_only and not all(isinstance(k.nodes[node], Crossing) for node in partition):
                continue

            ccw_endpoints = ccw_endpoints_[index][rotation:] + ccw_endpoints_[index][:rotation]
            ccw_endpoints_c = ccw_endpoints_[1 - index][rotation:] + ccw_endpoints_[1 - index][:rotation]

            # The first two endpoints must be from the same crossing (the “flype” crossing).
            if ccw_endpoints[0].node != ccw_endpoints[1].node or not isinstance(k.nodes[ccw_endpoints[0].node], Crossing):
                continue

            # Disallow if either side forms an integer tangle (checked as in the original logic).
            if _is_integer_tangle_cut(k, partition_[index], ccw_endpoints) or _is_integer_tangle_cut(k, partition_[1 - index], ccw_endpoints_c):
                continue

            yield partition, ccw_endpoints


def choose_flype(k, random: bool = False):
    """Return one flype."""
    if "FLYPE" not in settings.allowed_moves:
        return None

    if random:
        locations = tuple(find_flypes(k))
        return choice(locations) if locations else None
    else:
        return next(find_flypes(k), None)  # select 1st item


def flype(k: Diagram, partition_endpoints_pair: tuple, inplace: bool = False):
    """
    Perform a flype at the given location.

    The crossing determined by the first two endpoints is “flipped” to the other
    side of the tangle, and then the subdiagram in the chosen partition is
    flipped (180°) using `flip`.

    Args:
        k (Diagram): The diagram.
        partition_endpoints_pair (tuple): `(partition, endpoints_quadruple)` as yielded by `find_flypes`.
        inplace (bool): If True, modify `k` in place; otherwise operate on a copy.

    Return:
        Diagram: The diagram with the flype applied.
    """
    if "FLYPE" not in settings.allowed_moves:
        warnings.warn("A flype move is being performed, although it is disabled in the global KnotPy settings.")

    # print("Flype", partition_endpoints_pair, "on", k)

    partition, endpoints_quadruple = partition_endpoints_pair

    if endpoints_quadruple[0].node != endpoints_quadruple[1].node:
        raise ValueError("Endpoints should share the first crossings")

    if not inplace:
        k = k.copy()

    # Flip the crossing to the "other side" of the tangle.
    ep0, ep1, ep2, ep3 = endpoints_quadruple
    twin0, twin1, twin2, twin3 = k.twin(ep0), k.twin(ep1), k.twin(ep2), k.twin(ep3)
    next0 = k.nodes[ep0.node][(ep0.position + 2) % 4]
    next1 = k.nodes[ep1.node][(ep1.position + 2) % 4]
    twin_next0 = k.twin(next0)  # other side of the crossing
    twin_next1 = k.twin(next1)  # other side of the crossing

    # Remove the original crossing connections.
    k.set_arc((twin0, next0))
    k.set_arc((twin1, next1))

    # Reconnect endpoints to realize the flype.
    k.set_arc((twin_next0, twin3))
    k.set_arc((twin_next1, twin2))
    k.set_arc((ep1, ep2))
    k.set_arc((ep0, ep3))

    # Flip the chosen side of the diagram.
    # print("flipping partition", partition)
    k = flip(k, partition, inplace=True)

    return k


if __name__ == "__main__":
    # Intentional no-op: keep heavy/demo code out of import path.
    pass