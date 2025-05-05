from knotpy.classes.planardiagram import PlanarDiagram
from  knotpy.classes.node import Vertex
from knotpy.classes.endpoint import Endpoint
from knotpy.algorithms.naming import unique_new_node_name






def subdivide_arc(k: PlanarDiagram, arc, new_node_name=None, **attr) -> str:
    """
    Subdivides an arc by introducing a new vertex along the arc. If arc is not a set, then the new node will be
    (arc[0], arc[1])


    Args:
        k (PlanarDiagram): The planar diagram.
        arc (list): A list containing two endpoints defining the arc to be subdivided.
        new_node_name:
        attr (dict): Additional attributes for the new node.

    Returns:
        str: The name of the newly created node.
    """
    endpoint_a, endpoint_b = arc

    endpoint_a = k.endpoint_from_pair(endpoint_a)
    endpoint_b = k.endpoint_from_pair(endpoint_b)

    a_attr = endpoint_a.attr | attr
    b_attr = endpoint_b.attr | attr

    if new_node_name is None:
        new_node_name = unique_new_node_name(k)

    k.add_node(node_for_adding=new_node_name, create_using=Vertex, degree=2)

    k.set_endpoint(endpoint_for_setting=(new_node_name, 0),
                   adjacent_endpoint=(endpoint_a.node, endpoint_a.position),
                   create_using=type(endpoint_b),
                   **b_attr)
    k.set_endpoint(endpoint_for_setting=(endpoint_a.node, endpoint_a.position),
                   adjacent_endpoint=(new_node_name, 0),
                   create_using=type(endpoint_a),
                   **a_attr)

    k.set_endpoint(endpoint_for_setting=(new_node_name, 1),
                   adjacent_endpoint=(endpoint_b.node, endpoint_b.position),
                   create_using=type(endpoint_b),
                   **b_attr)
    k.set_endpoint(endpoint_for_setting=(endpoint_b.node, endpoint_b.position),
                   adjacent_endpoint=(new_node_name, 1),
                   create_using=type(endpoint_a),
                   **a_attr)

    return new_node_name


def subdivide_endpoint(k: PlanarDiagram, endpoint, **attr) -> str:
    """
    Subdivides an endpoint by introducing a new node. The endpoint is at position 0 of the new node

    Args:
        k (PlanarDiagram): The planar diagram.
        endpoint (Endpoint): The endpoint where the subdivision occurs.
        attr (dict): Additional attributes for the new node.

    Returns:
        str: The name of the newly created node.
    """
    return subdivide_arc(k, [endpoint, k.twin(endpoint)], new_node_name=None, **attr)


def subdivide_endpoint_by_crossing(k: PlanarDiagram, endpoint, crossing_position, **attr) -> str:
    """
    Subdivides an endpoint by introducing a new node. The endpoint is at position 0 of the new node

    Args:
        k (PlanarDiagram): The planar diagram.
        endpoint (Endpoint): The endpoint where the subdivision occurs.
        attr (dict): Additional attributes for the new node.

    Returns:
        str: The name of the newly created node.
    """
    endpoint = k.endpoint_from_pair(endpoint)
    twin_endpoint = k.twin(endpoint)

    new_node_name = unique_new_node_name(k)
    crossing_position = crossing_position % 4

    k.add_crossing(crossing_for_adding=new_node_name, **attr)

    k.set_endpoint(endpoint_for_setting=(new_node_name, crossing_position),
                   adjacent_endpoint=(endpoint.node, endpoint.position),
                   create_using=type(twin_endpoint),
                   **twin_endpoint.attr)
    k.set_endpoint(endpoint_for_setting=(endpoint.node, endpoint.position),
                   adjacent_endpoint=(new_node_name, crossing_position),
                   create_using=type(endpoint),
                   **endpoint.attr)

    k.set_endpoint(endpoint_for_setting=(new_node_name, (crossing_position + 2) % 4),
                   adjacent_endpoint=(twin_endpoint.node, twin_endpoint.position),
                   create_using=type(twin_endpoint),
                   **twin_endpoint.attr)
    k.set_endpoint(endpoint_for_setting=(twin_endpoint.node, twin_endpoint.position),
                   adjacent_endpoint=(new_node_name, (crossing_position + 2) % 4),
                   create_using=type(endpoint),
                   **endpoint.attr)

    return new_node_name


def subdivide_arcs_around_node(k: PlanarDiagram, arc, inplace=True):
    raise NotImplementedError()
    pass
