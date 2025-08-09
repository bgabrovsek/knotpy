# knotpy/algorithms/subdivide.py

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node import Vertex
from knotpy.classes.endpoint import Endpoint
from knotpy.algorithms.naming import unique_new_node_name


def subdivide_arc(k: PlanarDiagram, arc: frozenset, new_node_name: str | None = None, **attr) -> str:
    """Subdivide an arc by inserting a new 2-valent vertex on it.

    Although the type hint is ``frozenset`` (your project-wide convention for arcs),
    this function also accepts any 2-item iterable of endpoints at runtime.

    Args:
        k: The planar diagram to modify (in place).
        arc: The arc to subdivide, typically a ``frozenset`` of two endpoints.
        new_node_name: Optional name for the new vertex. If ``None``, a unique name is generated.
        **attr: Attributes to add on the *new* arc endpoints created by this subdivision.

    Returns:
        The name of the newly created vertex.
    """
    try:
        endpoint_a, endpoint_b = tuple(arc)
    except Exception as e:
        raise ValueError(f"`arc` must contain exactly two endpoints; got: {arc!r}") from e

    # Normalize to Endpoint objects
    ep_a = k.endpoint_from_pair(endpoint_a)
    ep_b = k.endpoint_from_pair(endpoint_b)

    # Merge attributes for each side (keep existing endpoint attrs, apply overrides from **attr)
    a_attr = ep_a.attr | attr
    b_attr = ep_b.attr | attr

    if new_node_name is None:
        new_node_name = unique_new_node_name(k)

    # Create the new 2-valent vertex
    k.add_node(node_for_adding=new_node_name, create_using=Vertex, degree=2)

    # Wire side A <-> new node(0)
    k.set_endpoint(
        endpoint_for_setting=(new_node_name, 0),
        adjacent_endpoint=(ep_a.node, ep_a.position),
        create_using=type(ep_a),
        **b_attr,
    )
    k.set_endpoint(
        endpoint_for_setting=(ep_a.node, ep_a.position),
        adjacent_endpoint=(new_node_name, 0),
        create_using=type(ep_b),
        **a_attr,
    )

    # Wire side B <-> new node(1)
    k.set_endpoint(
        endpoint_for_setting=(new_node_name, 1),
        adjacent_endpoint=(ep_b.node, ep_b.position),
        create_using=type(ep_b),
        **b_attr,
    )
    k.set_endpoint(
        endpoint_for_setting=(ep_b.node, ep_b.position),
        adjacent_endpoint=(new_node_name, 1),
        create_using=type(ep_a),
        **a_attr,
    )

    return new_node_name


def subdivide_endpoint(k: PlanarDiagram, endpoint: tuple | Endpoint, **attr) -> str:
    """Subdivide the arc incident to a given endpoint by inserting a new vertex.

    The endpoint becomes position 0 of the new vertex; its twin becomes position 1.

    Args:
        k: The planar diagram to modify (in place).
        endpoint: The endpoint (``(node, pos)`` or ``Endpoint``) where the arc should be split.
        **attr: Attributes to apply on the new endpoints created by the subdivision.

    Returns:
        The name of the newly created vertex.
    """
    ep = k.endpoint_from_pair(endpoint)
    twin = k.twin(ep)
    # Use frozenset in call to match project-wide arc convention
    return subdivide_arc(k, frozenset({ep, twin}), new_node_name=None, **attr)


def subdivide_endpoint_by_crossing(
    k: PlanarDiagram, endpoint: tuple | Endpoint, crossing_position: int, **attr
) -> str:
    """Insert a new crossing on the arc of a given endpoint, attaching at a specified crossing slot.

    The new crossing has the given ``crossing_position`` (0..3) connected to the provided endpoint,
    and the opposite position (``+2 mod 4``) connected to its twin.

    Args:
        k: The planar diagram to modify (in place).
        endpoint: The endpoint (``(node, pos)`` or ``Endpoint``) whose arc will receive the new crossing.
        crossing_position: Desired position (0..3). Values are reduced mod 4.
        **attr: Attributes applied to the new crossing.

    Returns:
        The name of the newly created crossing node.
    """
    ep = k.endpoint_from_pair(endpoint)
    twin = k.twin(ep)

    new_node_name = unique_new_node_name(k)
    pos = crossing_position % 4

    k.add_crossing(crossing_for_adding=new_node_name, **attr)

    # Connect crossing at `pos` to ep
    k.set_endpoint(
        endpoint_for_setting=(new_node_name, pos),
        adjacent_endpoint=(ep.node, ep.position),
        create_using=type(twin),
        **twin.attr,
    )
    k.set_endpoint(
        endpoint_for_setting=(ep.node, ep.position),
        adjacent_endpoint=(new_node_name, pos),
        create_using=type(ep),
        **ep.attr,
    )

    # Connect opposite position (pos+2) to twin
    opp = (pos + 2) % 4
    k.set_endpoint(
        endpoint_for_setting=(new_node_name, opp),
        adjacent_endpoint=(twin.node, twin.position),
        create_using=type(twin),
        **twin.attr,
    )
    k.set_endpoint(
        endpoint_for_setting=(twin.node, twin.position),
        adjacent_endpoint=(new_node_name, opp),
        create_using=type(ep),
        **ep.attr,
    )

    return new_node_name


def subdivide_arcs_around_node(k: PlanarDiagram, node) -> list[str]:
    """Subdivide every arc incident to a node by inserting a 2-valent vertex.

    Args:
        k: The planar diagram to modify (in place).
        node: The node whose incident arcs will be subdivided.

    Returns:
        A list of new vertex names, one for each incident arc.
    """
    return [subdivide_endpoint(k, endpoint=ep) for ep in k.nodes[node]]


if __name__ == "__main__":
    pass