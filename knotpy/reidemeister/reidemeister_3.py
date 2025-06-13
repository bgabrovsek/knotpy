from itertools import chain
from random import choice
import warnings

from knotpy.classes.node import Crossing
from knotpy._settings import settings


def find_reidemeister_3_triangle(k):
    """
    Finds all faces in the given knot diagram `k` that represent a valid
    Reidemeister III triangle.

    This function iterates over all faces of the knot diagram `k` and identifies
    those triangular faces that satisfy criteria for being valid Reidemeister III
    configurations. The validity is determined by checking the face's structure
    and the associated properties of the crossings in the knot diagram.

    Args:
        k: The knot diagram object containing faces and nodes. Each face is a
           sequence of endpoints, and endpoints reference nodes within the diagram.
           Nodes can either be crossings or other entities relevant in the knot diagram.

    Yields:
        list of Endpoint: The triangular face endpoints representing a valid
        Reidemeister III triangle. A face is yielded only if:
            - It contains exactly three nodes.
            - All three nodes are crossings.
            - The positional parity of the nodes does not all match.
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

def choose_reidemeister_3_triangle(k, random=False):
    """
    Returns a (random) face where a Reidemeister 3 move can be performed.

    This function identifies a face in a planar diagram `k` where a Reidemeister 3
    move can be executed. If `random` is set to `True`, the function selects a
    random triangular face from the potential candidates. Otherwise, it returns
    the first triangular face found.

    Args:
        k: The planar diagram on which to find a triangular face for
            performing a Reidemeister 3 move.
        random: Specifies whether to select a random face (True) or the first
            face found (False).

    Returns:
        The selected triangular face where a Reidemeister 3 move can be
        performed, or None if no such face exists.
    """

    if "R3" not in settings.allowed_moves:
        return None

    if random:
        locations = tuple(find_reidemeister_3_triangle(k))
        return choice(locations) if locations else None
    else:
        return next(find_reidemeister_3_triangle(k), None)  # select 1st item


def reidemeister_3(k, face, inplace=False):
    """
    Perform a Reidemeister III move on a non-alternating triangular region of a
    planar diagram. This function modifies the topology of the triangular region
    by updating endpoints of arcs and crossings accordingly. The operation can
    either be performed in place or on a copied instance of the planar diagram.

    Args:
        k: The planar diagram object representing the knot or link diagram.
        face: A ReidemeisterLocationThree object representing a non-alternating
            triangular region to apply the move. This is a tuple of three endpoints,
            where each endpoint is represented as a tuple containing the node and
            the position within that node.
        inplace: Whether to perform the operation in place on the current instance
            of the planar diagram (True) or to create and modify a copied instance
            (False). Defaults to False.

    Raises:
        ValueError: If the planar diagram is oriented since oriented Reidemeister
            III moves are not supported.

    Returns:
        The planar diagram after performing the Reidemeister III move. If `inplace`
        is False, a new planar diagram instance with the modification is returned;
        otherwise, the modified diagram is returned.
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

    # redirect endpoints on arcs inside the area
    new_inner_endpoints = {
        (node_a, (pos_a + 1) % 4): (node_b, (pos_b + 2) % 4),  # (node, position + 1) -> (next node, next position + 2)
        (node_a, (pos_a + 2) % 4): (node_c, (pos_c + 1) % 4),  # (node, position + 2) -> (previous node, previous position + 1)
        (node_b, (pos_b + 1) % 4): (node_c, (pos_c + 2) % 4),
        (node_b, (pos_b + 2) % 4): (node_a, (pos_a + 1) % 4),
        (node_c, (pos_c + 1) % 4): (node_a, (pos_a + 2) % 4),
        (node_c, (pos_c + 2) % 4): (node_b, (pos_b + 1) % 4),
    }
    #print("new inner", new_inner_endpoints)

    # redirect the endpoints of the crossings on to the triangle face, directed outside (away from the triangle)
    new_outer_endpoints = {
        (node_a, pos_a): tuple(k.nodes[node_c][(pos_c + 1) % 4]),  # (node, position) -> k.nodes[previous node][previous position - 1]
        (node_a, (pos_a - 1) % 4): tuple(k.nodes[node_b][(pos_b + 2) % 4]),  # (node, position - 1) -> k.nodes[next node][next position + 2]
        (node_b, pos_b): tuple(k.nodes[node_a][(pos_a + 1) % 4]),
        (node_b, (pos_b - 1) % 4): tuple(k.nodes[node_c][(pos_c + 2) % 4]),
        (node_c, pos_c): tuple(k.nodes[node_b][(pos_b + 1) % 4]),
        (node_c, (pos_c - 1) % 4): tuple(k.nodes[node_a][(pos_a + 2) % 4]),
    }
    #print("new outer", new_outer_endpoints)

    # "outer" endpoints change if they point to a crossing of the triangle face
    new_outer_endpoints.update(
        {src_ep: (new_inner_endpoints[dst_ep][0], (new_inner_endpoints[dst_ep][1] + 2) % 4)
         for src_ep, dst_ep in new_outer_endpoints.items() if dst_ep[0] in area_nodes}
    )

    # redirect endpoints that do not lie on the triangle (are incident to it)
    new_external_endpoints = {
        dst_ep: src_ep for src_ep, dst_ep in new_outer_endpoints.items() if dst_ep[0] not in area_nodes
    }



    # actually make the endpoint changes
    for src_ep, dst_ep in chain(new_inner_endpoints.items(), new_outer_endpoints.items(), new_external_endpoints.items()):
        k.set_endpoint(
            endpoint_for_setting=src_ep,
            adjacent_endpoint=dst_ep,
            create_using=type(k.nodes[src_ep[0]][src_ep[1]]),  # use old type of endpoint
            **k.nodes[dst_ep[0]][dst_ep[1]].attr  # use old type of attributes
        )

    # mark the nodes where the R3 was made to the planar diagram (optional)
    # this is needed when performing multiple R3 moves, so we do not repeat (undo) the moves

    for r_node in area_nodes:
        k.nodes[r_node].attr["_r3"] = True

    # backtrack Reidemeister moves
    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R3 "

    return k
