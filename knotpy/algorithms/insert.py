# knotpy/algorithms/insert.py

"""
Insert and modify arcs/endpoints in a planar diagram.

These utilities let you:
- insert a new arc between two specified endpoint *positions* at nodes,
- insert a loop at a node position,
- insert a new leaf (degree-1 vertex) at an endpoint position,
- create a parallel arc next to an existing arc.

Notes:
- Functions operate in place.
- For arc insertions that depend on which endpoint is considered "side A"
  versus "side B", we use an ordered pair (tuple) for the arc rather than a
  frozenset to keep behavior deterministic.
"""

__all__ = ["insert_arc", "insert_endpoint", "insert_new_leaf", "insert_loop", "parallelize_arc"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node.vertex import Vertex
from knotpy.algorithms.naming import unique_new_node_name


def insert_arc(k: PlanarDiagram, arc: tuple[tuple, tuple], **attr) -> None:
    """Insert a new arc between two nodes at specified positions.

    The function first makes room at each node position (shifting later
    endpoints CCW), then wires the two new endpoints together.

    Args:
        k: Diagram to modify (in place).
        arc: ``((node_a, pos_a), (node_b, pos_b))`` — ordered pair of endpoints
            indicating *where* to insert the new arc.
        **attr: Attributes to store on the new endpoints.

    Raises:
        ValueError: If either target position is invalid for the node.

    Note:
        We intentionally use an ordered pair rather than a frozenset because the
        operation is asymmetric (we insert at specific positions on each side).
    """
    (node_a, position_a), (node_b, position_b) = arc

    is_oriented = k.is_oriented()

    _insert_none_at_node_position(k, node_a, position_a)
    _insert_none_at_node_position(k, node_b, position_b)

    k.set_endpoint(
        endpoint_for_setting=(node_a, position_a),
        adjacent_endpoint=(node_b, position_b),
        create_using=IngoingEndpoint if is_oriented else Endpoint,
        **attr,
    )
    k.set_endpoint(
        endpoint_for_setting=(node_b, position_b),
        adjacent_endpoint=(node_a, position_a),
        create_using=OutgoingEndpoint if is_oriented else Endpoint,
        **attr,
    )


def insert_loop(k: PlanarDiagram, endpoint: tuple | Endpoint, **attr) -> None:
    """Insert a loop at a node position.

    Creates two new opposite endpoints that connect to each other and lie in
    consecutive positions around the given node.

    Args:
        k: Diagram to modify (in place).
        endpoint: ``(node, pos)`` or an :class:`Endpoint`.
        **attr: Endpoint attributes to set on both half-edges.

    Raises:
        ValueError: If target node is not a vertex.
    """
    if isinstance(endpoint, Endpoint):
        node, pos = endpoint.node, endpoint.position
    else:
        node, pos = endpoint

    if not isinstance(k._nodes[node], Vertex):
        raise ValueError("insert_loop can only be used at a Vertex node.")

    # Make room for two new entries at (pos, pos+1)
    _insert_none_at_node_position(k, node, pos, count=2)

    # For unoriented diagrams these are both Endpoint; for oriented, consider
    # extending to Ingoing/Outgoing symmetry if/when needed.
    k._nodes[node]._inc[pos] = Endpoint(node=node, position=pos + 1, **attr)
    k._nodes[node]._inc[pos + 1] = Endpoint(node=node, position=pos, **attr)


def insert_endpoint(k: PlanarDiagram, target_endpoint: tuple, adjacent_endpoint: tuple | Endpoint, **attr) -> None:
    """Insert one endpoint into a node's incidence list (shifting others CCW).

    This is a low-level primitive. It *does not* automatically update the twin
    at the other node; it simply places the given adjacent endpoint object
    into the target position.

    Args:
        k: Diagram to modify (in place).
        target_endpoint: ``(node, pos)`` where to place the new endpoint.
        adjacent_endpoint: The endpoint object (or tuple convertible to one)
            to insert into the node's incidence list at ``(node, pos)``.
        **attr: Attributes merged into the endpoint at insertion.

    Raises:
        ValueError: If target node is not a vertex.
    """
    node, pos = target_endpoint

    # Make space for the endpoint in the incident list
    _insert_none_at_node_position(k, node, pos)

    # If an endpoint is not given, create one
    if not isinstance(adjacent_endpoint, Endpoint):
        adjacent_endpoint = Endpoint(*adjacent_endpoint)  # unoriented case

    if not isinstance(k._nodes[node], Vertex):
        raise ValueError("Cannot insert an endpoint at a non-vertex node.")

    # Place the endpoint and merge attributes
    k._nodes[node]._inc[pos] = adjacent_endpoint
    k._nodes[node]._inc[pos].attr.update(attr)


def insert_new_leaf(k: PlanarDiagram, target_endpoint: tuple, new_node_name: str | None = None) -> str:
    """Insert a new degree-1 vertex attached at the given endpoint position.

    Args:
        k: Diagram to modify (in place).
        target_endpoint: ``(node, pos)`` where the new leaf edge attaches.
        new_node_name: Optional explicit name; if omitted, a fresh name is created.

    Returns:
        The name of the newly created vertex.
    """
    if new_node_name is None:
        new_node_name = unique_new_node_name(k)

    node, pos = target_endpoint

    k.add_vertex(new_node_name)
    _insert_none_at_node_position(k, node, pos)
    k.set_arc((target_endpoint, (new_node_name, 0)))

    return new_node_name


def parallelize_arc(k: PlanarDiagram, arc: tuple[tuple, tuple], inplace=True, **attr) -> PlanarDiagram:
    """Insert a new arc parallel to an existing arc (on the first endpoint's side).

    The new arc is inserted at position ``pos_a + 1`` at the first endpoint and
    at ``pos_b`` at the second endpoint, effectively drawing a parallel strand.

    Args:
        k: Diagram to modify (in place).
        arc: ``((node_a, pos_a), (node_b, pos_b))`` – ordered existing arc endpoints.
        **attr: Attributes for the new arc endpoints.

    Raises:
        NotImplementedError: If the arc is a loop.
        ValueError: If either endpoint node is not a Vertex.
    """
    if not inplace:
        k = k.copy()

    (node_a, pos_a), (node_b, pos_b) = arc

    if node_a == node_b:
        raise NotImplementedError("Parallelizing loops is not implemented.")

    if not isinstance(k.nodes[node_a], Vertex) or not isinstance(k.nodes[node_b], Vertex):
        raise ValueError("Can only parallelize arcs between Vertex nodes.")

    # Insert a new arc adjacent to the first endpoint (at pos_a+1)
    insert_arc(k, ((node_a, pos_a + 1), (node_b, pos_b)), **attr)

    return k


def _insert_none_at_node_position(k: PlanarDiagram, node, position: int, count: int = 1) -> None:
    """Internal: insert ``count`` placeholders at a node position and shift others.

    This temporarily makes the diagram invalid while placeholders (``None``)
    exist, so callers must promptly fill those positions.

    Args:
        k: Diagram to modify.
        node: Node label.
        position: Insertion position.
        count: How many placeholders to insert.
    """
    node_inst = k.nodes[node]

    # Record all adjustments we need to make on the *other* endpoints first.
    changes: list[tuple] = []
    for i, adj_ep in enumerate(node_inst[position:], start=position):
        ep_target = k.endpoint_from_pair((node, i))
        changes.append((adj_ep.node, adj_ep.position, i + count, type(ep_target), ep_target.attr))

    # Apply the recorded changes: shift the partners so they still point to us
    for adj_node, adj_pos, new_pos, ep_type, ep_attr in changes:
        k.nodes[adj_node][adj_pos] = ep_type(node=node, position=new_pos, **ep_attr)

    # Finally insert ``None`` slots at this node
    for i in range(count):
        k._nodes[node]._inc.insert(position + i, None)


if __name__ == "__main__":
    pass