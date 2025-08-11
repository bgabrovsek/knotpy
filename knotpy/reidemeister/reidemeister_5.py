# knotpy/reidemeister/reidemeister_5.py
from __future__ import annotations

from typing import Iterator, Optional, Tuple, Hashable

from random import choice
import warnings
from fractions import Fraction

from knotpy.classes.planardiagram import Diagram  # PlanarDiagram | OrientedPlanarDiagram
from knotpy.classes.node import Crossing, Vertex
from knotpy.algorithms.subdivide import (
    subdivide_endpoint_by_crossing,
    subdivide_endpoint,
)
from knotpy.algorithms.remove import remove_bivalent_vertex
from knotpy._settings import settings


def find_reidemeister_5_twists(k: Diagram) -> Iterator[tuple]:
    """Find all local **twist** locations (R5) at vertices.

    A twist is given by two adjacent endpoints from the same vertex: an **over**
    endpoint and an **under** endpoint with `|pos_under - pos_over| == 1` (indices
    taken modulo the vertex degree). For each adjacency at a vertex `v`, both
    orders `(under, over)` and `(over, under)` are yielded.

    Args:
        k (Diagram): The (oriented or unoriented) diagram.

    Return:
        Iterator[tuple]: Pairs `(ep_under, ep_over)` of adjacent endpoints at a vertex.

    Notes:
        - If ``settings.r5_only_trivalent`` is True, only trivalent vertices are considered.
        - Degree-2 vertices are supported (both directions yielded).
    """
    if "R5" not in settings.allowed_moves:
        return

    for v in k.vertices:
        deg = k.degree(v)

        if settings.r5_only_trivalent and deg != 3:
            continue

        if deg > 2:
            for pos in range(deg):
                yield k.endpoint_from_pair((v, pos)), k.endpoint_from_pair((v, (pos + 1) % deg))
                yield k.endpoint_from_pair((v, (pos + 1) % deg)), k.endpoint_from_pair((v, pos))
        elif deg == 2:
            yield k.endpoint_from_pair((v, 0)), k.endpoint_from_pair((v, 1))
            yield k.endpoint_from_pair((v, 1)), k.endpoint_from_pair((v, 0))


def choose_reidemeister_5_twist(k: Diagram, random: bool = False) -> Optional[tuple]:
    """
    Select a twist location (R5).

    Args:
        k (Diagram): The diagram.
        random (bool): If True choose a random valid twist; otherwise choose the first.

    Return:
        Optional[tuple]: A `(ep_under, ep_over)` pair, or ``None`` if not available.
    """
    if "R5" not in settings.allowed_moves:
        return None

    if random:
        locations = tuple(find_reidemeister_5_twists(k))
        return choice(locations) if locations else None
    else:
        return next(find_reidemeister_5_twists(k), None)


def find_reidemeister_5_untwists(k: Diagram) -> Iterator[tuple]:
    """Find all local **untwist** locations (R5) as alternating bigons.

    An untwist is given by a 2-face (bigon) consisting of one vertex endpoint and
    one crossing endpoint. The function yields `(vertex_endpoint, crossing_endpoint)`.

    Args:
        k (Diagram): The diagram.

    Return:
        Iterator[tuple]: Pairs `(vertex_endpoint, crossing_endpoint)` for R5 untwists.

    Notes:
        - If ``settings.r5_only_trivalent`` is True, only vertices of degree 3 are yielded.
    """
    if "R5" not in settings.allowed_moves:
        return

    for face in k.faces:
        if len(face) == 2:
            ep1, ep2 = face
            # Ensure (vertex_ep, crossing_ep) order.
            if isinstance(k.nodes[ep1.node], Crossing):
                ep2, ep1 = ep1, ep2

            if not isinstance(k.nodes[ep1.node], Vertex) or not isinstance(k.nodes[ep2.node], Crossing):
                continue

            if settings.r5_only_trivalent and k.degree(ep1.node) != 3:
                continue

            yield ep1, ep2


def choose_reidemeister_5_untwist(k: Diagram, random: bool = False) -> Optional[tuple]:
    """
    Select an untwist location (R5).

    Args:
        k (Diagram): The diagram.
        random (bool): If True choose a random valid untwist; otherwise choose the first.

    Return:
        Optional[tuple]: A `(vertex_endpoint, crossing_endpoint)` pair, or ``None``.
    """
    if "R5" not in settings.allowed_moves:
        return None

    if random:
        faces = tuple(find_reidemeister_5_untwists(k))
        return choice(faces) if faces else None
    else:
        return next(find_reidemeister_5_untwists(k), None)


def reidemeister_5_twist(k: Diagram, endpoints: tuple, inplace: bool = False) -> Diagram:
    """
    Perform a local **twist** (R5) at a vertex.

    The twist inserts a crossing adjacent to the *under* endpoint and threads the
    *over* strand across it, possibly adjusting the framing by ±1/2.

    Args:
        k (Diagram): The diagram.
        endpoints (tuple): `(ep_under, ep_over)` adjacent at the same vertex.
        inplace (bool): If True modify `k` in place; otherwise return a copy.

    Return:
        Diagram: The diagram with the R5 twist applied.
    """
    if "R5" not in settings.allowed_moves:
        warnings.warn("An R5 twist move is being performed, although it is disabled in the global KnotPy settings.")

    ep_under, ep_over = endpoints

    if not inplace:
        k = k.copy()

    # Add the "twist" crossing beside the under-arc.
    crossing = subdivide_endpoint_by_crossing(k, ep_under, 0)

    over_twin = k.twin(ep_over)

    # Insert over-arcs (positions 1 and 3 depend on CCW/CW relation to the under-arc)
    if (ep_under.position + 1) % k.degree(ep_under.node) == ep_over.position:
        k.set_endpoint(over_twin, (crossing, 3))
        k.set_endpoint((crossing, 3), over_twin)
        k.set_endpoint(ep_over, (crossing, 1))
        k.set_endpoint((crossing, 1), ep_over)
        # adjust framing
        if k.is_framed():
            k.framing = k.framing - Fraction(1, 2)
    else:
        k.set_endpoint(over_twin, (crossing, 1))
        k.set_endpoint((crossing, 1), over_twin)
        k.set_endpoint(ep_over, (crossing, 3))
        k.set_endpoint((crossing, 3), ep_over)
        if k.is_framed():
            k.framing = k.framing + Fraction(1, 2)

    # switch the endpoints at the vertex (swap the two adjacent incident arcs)
    ep_under_twin = k.twin(ep_under)
    ep_over_twin = k.twin(ep_over)
    k.set_endpoint(ep_under, ep_over_twin)
    k.set_endpoint(ep_over_twin, ep_under)
    k.set_endpoint(ep_over, ep_under_twin)
    k.set_endpoint(ep_under_twin, ep_over)

    # backtrack Reidemeister moves
    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R5+"

    return k


def reidemeister_5_untwist(k: Diagram, face: tuple, inplace: bool = False) -> Diagram:
    """
    Reidemeister move 5 **untwist** operation on a given diagram.

    This removes a local twist represented by a bigon face (2-region) consisting of
    one vertex endpoint and one crossing endpoint.

    Args:
        k (Diagram): The diagram.
        face (tuple): `(vertex_endpoint, crossing_endpoint)` that bound the 2-face.
        inplace (bool): If True modify `k` in place; otherwise return a copy.

    Return:
        Diagram: The diagram with the R5 untwist applied.

    Notes:
        - Framing is adjusted by ±1/2 depending on the parity of the removed crossing side.
        - Endpoint attributes/types on reconnections are preserved by delegating to
          `set_endpoint` with the original types/attributes.
    """
    # TODO: attributes (fine-grained propagation) if needed in the future.

    if "R5" not in settings.allowed_moves:
        warnings.warn("An R5 untwist move is being performed, although it is disabled in the global KnotPy settings.")

    if not inplace:
        k = k.copy()

    # vertex endpoint and crossing endpoint (CCW around the bigon)
    v1_ep, c2_ep = face
    # twins of the endpoints (the other two corners of the bigon, CCW)
    v2_ep, c1_ep = k.nodes[c2_ep.node][c2_ep.position], k.nodes[v1_ep.node][v1_ep.position]

    # split incident endpoints on both sides of the crossing corners
    y1_ep = k.endpoint_from_pair((c1_ep.node, (c1_ep.position + 2) % 4))
    y2_ep = k.endpoint_from_pair((c2_ep.node, (c2_ep.position + 2) % 4))

    b_node_1 = subdivide_endpoint(k, y1_ep)
    b_node_2 = subdivide_endpoint(k, y2_ep)

    # reconnect across the bigon
    x1_ep = k.nodes[c2_ep.node][(c2_ep.position + 2) % 4]  # connects to v1_ep
    x2_ep = k.nodes[c1_ep.node][(c1_ep.position + 2) % 4]  # connects to v2_ep

    k.set_endpoint(endpoint_for_setting=v1_ep, adjacent_endpoint=x1_ep)
    k.set_endpoint(endpoint_for_setting=x1_ep, adjacent_endpoint=v1_ep)
    k.set_endpoint(endpoint_for_setting=v2_ep, adjacent_endpoint=x2_ep)
    k.set_endpoint(endpoint_for_setting=x2_ep, adjacent_endpoint=v2_ep)

    remove_bivalent_vertex(k, b_node_1)
    remove_bivalent_vertex(k, b_node_2)

    # remove the crossing corner of the bigon
    k.remove_node(c2_ep.node, remove_incident_endpoints=False)

    # adjust framing: removing a positive/negative half-twist
    if k.is_framed():
        k.framing = k.framing + (Fraction(-1, 2) if c2_ep.position % 2 else Fraction(1, 2))

    # backtrack Reidemeister moves
    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R5-"

    return k


if __name__ == "__main__":
    # Local demonstration / quick manual tests. Heavy imports stay here to avoid slowing down library import time.
    from knotpy.notation.pd import from_pd_notation  # noqa: F401
    from knotpy.notation.native import from_knotpy_notation  # noqa: F401
    from knotpy.algorithms.sanity import sanity_check  # noqa: F401

    # test framing
    code = "a=V(c1 c0 b0) b=V(a2 b2 b1) c=X(a1 a0 c3 c2)"
    k = from_knotpy_notation(code)
    for e in find_reidemeister_5_untwists(k):
        print(e)
        k_2 = reidemeister_5_untwist(k, e, inplace=False)
        print(k_2)
        break

    k = from_pd_notation("[[0,1,2],[2,3,5],[7,8,6],[0,13,12],[11,7,12,13],[1,6,8,9],[3,9,4,10],[10,4,11,5]]")
    for e in find_reidemeister_5_twists(k):
        print(e)
        k_2 = reidemeister_5_twist(k, e, inplace=False)
        print(k_2)
        break

    sanity_check(k)
    print(k)