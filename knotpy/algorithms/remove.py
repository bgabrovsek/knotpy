# knotpy/algorithms/remove.py

"""
Utilities for removing structure from planar diagrams:
- empty nodes
- a specific arc
- all loops
- unknots
- bivalent (degree-2) vertices
"""

__all__ = [
    "remove_empty_nodes",
    "remove_arc",
    "remove_loops",
    "remove_unknots",
    "remove_bivalent_vertex",
    "remove_bivalent_vertices",
]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.topology import loops
from knotpy.algorithms.topology import _is_vertex_an_unknot  # used intentionally


def remove_empty_nodes(k: PlanarDiagram, inplace: bool = True) -> PlanarDiagram:
    """Remove all nodes with degree 0.

    Args:
        k: Diagram to clean.
        inplace: If False, operate on a copy.

    Returns:
        The mutated diagram (or the new copy if ``inplace=False``).
    """
    if not inplace:
        k = k.copy()

    for n in list(k.nodes):
        if not k.nodes[n]:
            k.remove_node(n)
    return k


def remove_arc(k: PlanarDiagram, arc_for_removing: frozenset, inplace: bool = True) -> PlanarDiagram:
    """Remove a single arc.

    Args:
        k: Diagram to modify.
        arc_for_removing: The arc to remove (conventionally a ``frozenset`` of two endpoints).
        inplace: If False, operate on a copy.

    Returns:
        The mutated diagram (or the new copy if ``inplace=False``).
    """
    if not inplace:
        k = k.copy()

    # Clear human name if present (canonical naming may change after removal)
    if "name" in k.attr:
        del k.attr["name"]

    k.remove_arc(arc_for_removing=arc_for_removing)
    return k


def remove_loops(k: PlanarDiagram) -> int:
    """Remove all loops (arcs whose endpoints share the same node).

    Operates in place.

    Args:
        k: Diagram to modify.

    Returns:
        The number of removed loops.
    """
    count = 0
    # Repeatedly query loops; remove one by one
    while (ls := loops(k)):
        k.remove_arc(ls[0])
        count += 1

    if "name" in k.attr:
        del k.attr["name"]

    return count


def remove_unknots(k: PlanarDiagram, max_unknots: int | None = None) -> int:
    """Remove disjoint unknots (degree-2 looped vertices) from the diagram.

    Args:
        k: Diagram to modify (in place).
        max_unknots: If provided, remove at most this many unknots.

    Returns:
        Number of removed unknots.
    """
    vertices = [v for v in k.vertices if _is_vertex_an_unknot(k, v)]
    if max_unknots is not None:
        vertices = vertices[:max_unknots]

    for v in vertices:
        k.remove_node(v, remove_incident_endpoints=True)

    return len(vertices)


def remove_bivalent_vertex(k: PlanarDiagram, node, keep_if_unknot: bool = True) -> None:
    """Remove a degree-2 vertex by splicing its incident edges.

    If both incident arcs form a trivial loop at the same vertex and
    ``keep_if_unknot`` is True, the vertex is kept.

    Args:
        k: Diagram to modify (in place).
        node: The degree-2 vertex to remove.
        keep_if_unknot: Preserve the vertex if it is the center of an unknot.

    Raises:
        ValueError: If ``node`` is not degree-2.
    """
    if k.degree(node) != 2:
        raise ValueError(f"Node {node} is not a bivalent vertex.")

    ep_a, ep_b = k.nodes[node]

    # keep trivial loop (optional)
    if keep_if_unknot and ep_a.node == ep_b.node == node:
        return

    # splice
    k.set_endpoint(ep_a, ep_b)
    k.set_endpoint(ep_b, ep_a)
    k.remove_node(node, remove_incident_endpoints=False)


def remove_bivalent_vertices(k: PlanarDiagram, match_attributes: bool = False) -> int:
    """Remove all degree-2 vertices by splicing their incident edges.

    Args:
        k: Diagram to modify (in place).
        match_attributes: If True, only remove a bivalent vertex when the
            four adjacent/incident endpoints have matching attributes in pairs
            (i.e., compatible to splice). If False, remove regardless of attrs.

    Returns:
        The number of removed bivalent vertices.

    Notes:
        - Loops are never spliced here.
        - For oriented diagrams, vertices whose two outward endpoints have the
          same direction are skipped (incoherent pairing).
    """
    if not hasattr(k, "vertices"):
        raise TypeError(f"Cannot remove bivalent vertices from type {type(k)}.")

    removed = 0
    candidates = {node for node in k.vertices if len(k.nodes[node]) == 2}

    while candidates:
        node = candidates.pop()

        # incident endpoints at node
        b0 = k.endpoint_from_pair((node, 0))
        a0 = k.twin(b0)
        b1 = k.endpoint_from_pair((node, 1))
        a1 = k.twin(b1)

        # keep loops intact
        if b0.node == a0.node or b1.node == a1.node:
            continue

        # oriented: skip incoherent pairing
        if k.is_oriented() and (type(a0) is type(a1)):
            continue

        # attribute compatibility gate (only remove if they match when requested)
        if match_attributes and not (b0.attr == a0.attr == b1.attr == a1.attr):
            continue

        # splice a0 <-> a1
        k.nodes[a0.node][a0.position] = a1
        k.nodes[a1.node][a1.position] = a0
        k.remove_node(node_for_removing=node, remove_incident_endpoints=False)
        removed += 1

    return removed


if __name__ == "__main__":
    pass