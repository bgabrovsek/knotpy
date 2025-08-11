# knotpy/reidemeister/reidemeister_3.py

from itertools import chain
from random import choice
import warnings

from knotpy.classes.node import Crossing
from knotpy.classes.planardiagram import Diagram  # alias: PlanarDiagram | OrientedPlanarDiagram
from knotpy._settings import settings


def find_reidemeister_3_triangle(k: Diagram):
    """
    Find all faces in the diagram `k` that represent a valid Reidemeister III triangle.

    Iterate over all faces of `k` and yield those triangular faces that satisfy the
    R3 criteria. A face is yielded only if:
      - It contains exactly three endpoints (a triangle),
      - The three endpoints touch three distinct nodes,
      - All three nodes are crossings,
      - The positional parity is not the same for all three endpoints.

    Args:
        k (Diagram): Diagram whose faces are examined.

    Yields:
        list: A length-3 list of endpoints forming an R3-eligible triangle.
    """
    # TODO: make faster by not iterating over all regions

    if "R3" not in settings.allowed_moves:
        return

    for face in k.faces:
        if len(face) != 3 or len({ep.node for ep in face}) != 3:
            continue

        if all(type(k.nodes[ep.node]) is Crossing for ep in face) and \
                not (face[0].position % 2 == face[1].position % 2 == face[2].position % 2):
            yield face


def choose_reidemeister_3_triangle(k: Diagram, random: bool = False):
    """
    Return a (random) face where a Reidemeister 3 move can be performed.

    Args:
        k (Diagram): Diagram to inspect.
        random (bool): If True, choose randomly among candidates; otherwise
            return the first found.

    Returns:
        list | None: A triangular face (length-3 list of endpoints) or None if none exists.
    """

    if "R3" not in settings.allowed_moves:
        return None

    if random:
        locations = tuple(find_reidemeister_3_triangle(k))
        return choice(locations) if locations else None
    else:
        return next(find_reidemeister_3_triangle(k), None)  # select 1st item


def reidemeister_3(k: Diagram, face: list, inplace: bool = False) -> Diagram:
    """
    Perform a Reidemeister III move on a non-alternating triangular region.

    Modify the topology of the triangular region by updating endpoints of arcs and
    crossings accordingly. Can operate in place or on a copy.

    Args:
        k (Diagram): Knot/link/graph diagram.
        face (list): A length-3 list of endpoints forming a non-alternating triangle.
        inplace (bool): If True, modify `k` in place; otherwise operate on a copy.

    Return:
        Diagram: The diagram with the R3 move applied.
    """

    if "R3" not in settings.allowed_moves:
        warnings.warn("An R3 move is being performed, although it is disabled in the global KnotPy settings.")

    if not inplace:
        k = k.copy()

    ep_a, ep_b, ep_c = face
    node_a, pos_a = ep_a
    node_b, pos_b = ep_b
    node_c, pos_c = ep_c
    area_nodes = {node_a, node_b, node_c}

    # Redirect endpoints on arcs inside the triangle.
    # (node, pos+1) goes forward around the triangle; (node, pos+2) goes backward.
    new_inner_endpoints = {
        (node_a, (pos_a + 1) % 4): (node_b, (pos_b + 2) % 4),
        (node_a, (pos_a + 2) % 4): (node_c, (pos_c + 1) % 4),
        (node_b, (pos_b + 1) % 4): (node_c, (pos_c + 2) % 4),
        (node_b, (pos_b + 2) % 4): (node_a, (pos_a + 1) % 4),
        (node_c, (pos_c + 1) % 4): (node_a, (pos_a + 2) % 4),
        (node_c, (pos_c + 2) % 4): (node_b, (pos_b + 1) % 4),
    }
    # Redirect endpoints on the triangle that point outward (away from the triangle).
    new_outer_endpoints = {
        (node_a, pos_a): tuple(k.nodes[node_c][(pos_c + 1) % 4]),
        (node_a, (pos_a - 1) % 4): tuple(k.nodes[node_b][(pos_b + 2) % 4]),
        (node_b, pos_b): tuple(k.nodes[node_a][(pos_a + 1) % 4]),
        (node_b, (pos_b - 1) % 4): tuple(k.nodes[node_c][(pos_c + 2) % 4]),
        (node_c, pos_c): tuple(k.nodes[node_b][(pos_b + 1) % 4]),
        (node_c, (pos_c - 1) % 4): tuple(k.nodes[node_a][(pos_a + 2) % 4]),
    }

    # “Outer” endpoints that point to a triangle crossing must be redirected via the new inner mapping.
    new_outer_endpoints.update(
        {
            src_ep: (new_inner_endpoints[dst_ep][0], (new_inner_endpoints[dst_ep][1] + 2) % 4)
            for src_ep, dst_ep in new_outer_endpoints.items()
            if dst_ep[0] in area_nodes
        }
    )

    # Endpoints outside the triangle that used to point to it must be updated to point back into it.
    new_external_endpoints = {
        dst_ep: src_ep
        for src_ep, dst_ep in new_outer_endpoints.items()
        if dst_ep[0] not in area_nodes
    }

    # Apply all endpoint rewires.
    for src_ep, dst_ep in chain(
        new_inner_endpoints.items(),
        new_outer_endpoints.items(),
        new_external_endpoints.items(),
    ):
        k.set_endpoint(
            endpoint_for_setting=src_ep,
            adjacent_endpoint=dst_ep,
            create_using=type(k.nodes[src_ep[0]][src_ep[1]]),  # preserve endpoint class
            **k.nodes[dst_ep[0]][dst_ep[1]].attr,              # preserve attributes
        )

    # Mark nodes touched by R3 so repeated passes can avoid undoing it (optional).
    for r_node in area_nodes:
        k.nodes[r_node].attr["_r3"] = True

    # Backtrack Reidemeister moves.
    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R3 "

    return k