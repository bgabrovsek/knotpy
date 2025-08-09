# knotpy/algorithms/subdivide.py

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node import Vertex
from knotpy.classes.endpoint import Endpoint
from knotpy.algorithms.naming import unique_new_node_name


def subdivide_arc(
    k: PlanarDiagram,
    arc,  # typically: frozenset[{(node, pos), (node, pos)}] but tuples/lists also work
    new_node_name: str | None = None,
    **attr,
) -> str:
    """Subdivide an arc by inserting a new 2-valent vertex.

    If ``arc`` is not a set (e.g., tuple/list), the new node is inserted between
    the two endpoints given. Order does not matter.

    Args:
        k: Planar diagram to modify (in place).
        arc: Two endpoints defining the arc to subdivide. Usually a
            ``frozenset`` of two endpoints, but tuples/lists also work.
            Each endpoint can be a pair ``(node, position)`` or an ``Endpoint``.
        new_node_name: Optional explicit name for the new node.
        **attr: Extra attributes to apply to the newly created endpoints.

    Returns:
        The name of the newly created node.
    """
    endpoint_a, endpoint_b = arc

    endpoint_a = k.endpoint_from_pair(endpoint_a)
    endpoint_b = k.endpoint_from_pair(endpoint_b)

    a_attr = endpoint_a.attr | attr
    b_attr = endpoint_b.attr | attr

    if new_node_name is None:
        new_node_name = unique_new_node_name(k)

    k.add_node(node_for_adding=new_node_name, create_using=Vertex, degree=2)

    # Connect new node position 0 to endpoint_a; update both directions
    k.set_endpoint(
        endpoint_for_setting=(new_node_name, 0),
        adjacent_endpoint=(endpoint_a.node, endpoint_a.position),
        create_using=type(endpoint_a),
        **b_attr,
    )
    k.set_endpoint(
        endpoint_for_setting=(endpoint_a.node, endpoint_a.position),
        adjacent_endpoint=(new_node_name, 0),
        create_using=type(endpoint_b),
        **a_attr,
    )

    # Connect new node position 1 to endpoint_b; update both directions
    k.set_endpoint(
        endpoint_for_setting=(new_node_name, 1),
        adjacent_endpoint=(endpoint_b.node, endpoint_b.position),
        create_using=type(endpoint_b),
        **b_attr,
    )
    k.set_endpoint(
        endpoint_for_setting=(endpoint_b.node, endpoint_b.position),
        adjacent_endpoint=(new_node_name, 1),
        create_using=type(endpoint_a),
        **a_attr,
    )

    return new_node_name


def subdivide_endpoint(k: PlanarDiagram, endpoint: Endpoint | tuple, **attr) -> str:
    """Subdivide an endpoint by inserting a new 2-valent vertex on its incident arc.

    The created node will have the given ``endpoint`` at position 0, and its twin at
    position 1 (via a call to :func:`subdivide_arc`).

    Args:
        k: Planar diagram to modify (in place).
        endpoint: An ``Endpoint`` instance or a pair ``(node, position)``.
        **attr: Extra attributes to apply to the newly created endpoints.

    Returns:
        The name of the newly created node.
    """
    return subdivide_arc(k, [endpoint, k.twin(endpoint)], new_node_name=None, **attr)


def subdivide_endpoint_by_crossing(
    k: PlanarDiagram,
    endpoint: Endpoint | tuple,
    crossing_position: int,
    **attr,
) -> str:
    """Insert a new crossing on the arc incident to ``endpoint``.

    The new crossing connects at ``crossing_position`` and its opposite position
    (``+2 mod 4``) to the twin. This is a specialized subdivision producing a 4-valent
    crossing instead of a 2-valent vertex.

    Args:
        k: Planar diagram to modify (in place).
        endpoint: An ``Endpoint`` instance or a pair ``(node, position)``.
        crossing_position: Position (0..3), normalized mod 4, where the endpoint is attached.
        **attr: Attributes for the new crossing.

    Returns:
        The name of the newly created crossing node.
    """
    endpoint = k.endpoint_from_pair(endpoint)
    twin_endpoint = k.twin(endpoint)

    new_node_name = unique_new_node_name(k)
    crossing_position = crossing_position % 4

    k.add_crossing(crossing_for_adding=new_node_name, **attr)

    # Connect crossing_position with endpoint; and its opposite with twin
    k.set_endpoint(
        endpoint_for_setting=(new_node_name, crossing_position),
        adjacent_endpoint=(endpoint.node, endpoint.position),
        create_using=type(twin_endpoint),
        **twin_endpoint.attr,
    )
    k.set_endpoint(
        endpoint_for_setting=(endpoint.node, endpoint.position),
        adjacent_endpoint=(new_node_name, crossing_position),
        create_using=type(endpoint),
        **endpoint.attr,
    )

    k.set_endpoint(
        endpoint_for_setting=(new_node_name, (crossing_position + 2) % 4),
        adjacent_endpoint=(twin_endpoint.node, twin_endpoint.position),
        create_using=type(twin_endpoint),
        **twin_endpoint.attr,
    )
    k.set_endpoint(
        endpoint_for_setting=(twin_endpoint.node, twin_endpoint.position),
        adjacent_endpoint=(new_node_name, (crossing_position + 2) % 4),
        create_using=type(endpoint),
        **endpoint.attr,
    )

    return new_node_name


def subdivide_arcs_around_node(k: PlanarDiagram, node) -> list[str]:
    """Subdivide all arcs incident to ``node`` (in place).

    For each incident endpoint at ``node``, insert a new 2-valent vertex on that arc.

    Args:
        k: Planar diagram to modify (in place).
        node: Node label whose incident arcs will be subdivided.

    Returns:
        A list of newly created node names, one per incident arc.
    """
    return [subdivide_endpoint(k, endpoint=ep) for ep in k.nodes[node]]


if __name__ == "__main__":
    pass