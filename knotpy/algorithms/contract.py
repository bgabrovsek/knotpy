# knotpy/algorithms/contract.py

"""
Contracting an arc in a planar diagram.

This module provides a single operation that *contracts* a chosen arc by
merging its two endpoints into one vertex. The two endpoints must be given
as an **ordered pair**: the first endpoint is kept, and the second endpoint’s
vertex is removed (its other incident endpoints are pulled into the kept vertex).

Notes:
    - Only (unoriented) vertex–vertex arcs are supported.
    - The operation can be performed in-place or on a copy.

Example:
    >>> from knotpy.classes.planardiagram import PlanarDiagram
    >>> from knotpy.algorithms.contract import contract_arc
    >>> k = PlanarDiagram()
    >>> _ = k.set_arcs_from("x0a0,x1b0,x2c0,x4d0,x3y2,y0e0,y1f0,y3g0,y4h0")
    >>> # contract arc (keep ('y',2), remove ('x',3))
    >>> k2 = contract_arc(k, (('y', 2), ('x', 3)), inplace=False)
"""

__all__ = ["contract_arc"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node import Vertex
from knotpy.classes.endpoint import Endpoint, ensure_endpoint
from knotpy.algorithms.rewire import pull_and_plug_endpoint


def contract_arc(
    k: PlanarDiagram,
    arc_for_contracting: tuple[Endpoint | tuple, Endpoint | tuple],
    inplace: bool = True,
) -> PlanarDiagram:
    """Contract a specific arc by merging its endpoints into a single vertex.

    The arc is specified as an **ordered pair** of endpoints:
    the first endpoint is kept (its vertex remains),
    and the second endpoint's vertex is removed. All other incident endpoints
    of the removed vertex are reattached to the kept vertex, preserving cyclic
    order via ``pull_and_plug_endpoint``.

    This operation is only defined for vertex–vertex arcs (both endpoints must
    lie on vertices). Loops (both endpoints on the same vertex) are not contractible.

    Args:
        k:
            The planar diagram to modify.
        arc_for_contracting:
            Ordered pair ``(keep_endpoint, remove_endpoint)`` where each endpoint is
            either an :class:`~knotpy.classes.endpoint.Endpoint` or a ``(node, position)`` tuple.
        inplace:
            If ``True`` (default), mutate ``k``. If ``False``, return a modified copy.

    Returns:
        The diagram with the arc contracted (``k`` itself if ``inplace=True``).

    Raises:
        TypeError: If either endpoint is not on a vertex.
        ValueError: If the arc is a loop (both endpoints on the same vertex).
    """
    if not inplace:
        k = k.copy()

    # Drop a stored name if any (canonical forms typically ignore names)
    if "name" in k.attr:
        del k.attr["name"]

    # Normalize endpoints
    keep_like, drop_like = arc_for_contracting
    keep_ep: Endpoint = ensure_endpoint(k, keep_like)
    drop_ep: Endpoint = ensure_endpoint(k, drop_like)

    keep_node, keep_pos = keep_ep.node, keep_ep.position
    drop_node, drop_pos = drop_ep.node, drop_ep.position

    # Validate vertex–vertex and non-loop
    if not isinstance(k.nodes[keep_node], Vertex) or not isinstance(k.nodes[drop_node], Vertex):
        raise TypeError(
            f"Cannot contract arc: endpoints must lie on vertices "
            f"(got {type(k.nodes[keep_node]).__name__}, {type(k.nodes[drop_node]).__name__})."
        )
    if keep_node == drop_node:
        raise ValueError("Cannot contract a loop (both endpoints on the same vertex).")

    # Remove the arc itself
    k.remove_arc((keep_ep, drop_ep))

    # Pull all other endpoints incident to drop_node, one-by-one, into keep_node @ keep_pos.
    # We iterate by decreasing the index relative to drop_pos, letting the node shrink as we pull.
    drop_node_inst = k.nodes[drop_node]
    idx = drop_pos
    while drop_node_inst:  # while there remain incident endpoints
        idx -= 1
        src_pos = max(idx, -1) % len(drop_node_inst)
        pull_and_plug_endpoint(
            k,
            source_endpoint=(drop_node, src_pos),
            destination_endpoint=(keep_node, keep_pos),
        )
        # node object is updated by pull_and_plug_endpoint through k; refresh reference
        drop_node_inst = k.nodes.get(drop_node, None)
        if drop_node_inst is None:
            break

    # Finally remove the emptied node container (endpoints already unplugged)
    if drop_node in k.nodes:
        k.remove_node(drop_node, remove_incident_endpoints=False)

    return k


if __name__ == "__main__":
    pass

