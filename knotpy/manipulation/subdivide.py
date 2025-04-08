from knotpy.classes.planardiagram import PlanarDiagram
from  knotpy.classes.node import Vertex
from knotpy.classes.endpoint import Endpoint
from knotpy.algorithms.naming import unique_new_node_name

# def split_arc_by_bivertex(k: PlanarDiagram, first_endpoint, second_endpoint):
#
#     # convert arguments to Endpoint instances (if not)
#     first_endpoint = k.endpoint_from_pair(first_endpoint)
#     second_endpoint = k.endpoint_from_pair(second_endpoint)
#
#     # split the arc by a temporary vertex
#     b_node = unique_temporary_new_node_name(k.nodes, "bi")  # bivalent node
#     k.add_vertex(b_node)
#     k.set_endpoint(("b_node", 0), first_endpoint, create_using=type(second_endpoint))
#     k.set_endpoint(("b_node", 1), second_endpoint, create_using=type(first_endpoint))
#
#     # add a temporary vertex the planar diagram
#     t_node = unique_temporary_new_node_name(k.nodes, "temp")
#     k.add_vertex(t_node)
#     raise DeprecationWarning("This function is deprecated, use subdivide_arc instead")
#
#




def subdivide_arc(k: PlanarDiagram, arc, new_node_name=None) -> str:
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

    if new_node_name is None:
        new_node_name = unique_new_node_name(k)

    k.add_node(node_for_adding=new_node_name, create_using=Vertex, degree=2)

    k.set_endpoint(endpoint_for_setting=(new_node_name, 0),
                   adjacent_endpoint=(endpoint_a.node, endpoint_a.position),
                   create_using=type(endpoint_b),
                   **endpoint_b.attr)
    k.set_endpoint(endpoint_for_setting=(endpoint_a.node, endpoint_a.position),
                   adjacent_endpoint=(new_node_name, 0),
                   create_using=type(endpoint_a),
                   **endpoint_a.attr)

    k.set_endpoint(endpoint_for_setting=(new_node_name, 1),
                   adjacent_endpoint=(endpoint_b.node, endpoint_b.position),
                   create_using=type(endpoint_b),
                   **endpoint_b.attr)
    k.set_endpoint(endpoint_for_setting=(endpoint_b.node, endpoint_b.position),
                   adjacent_endpoint=(new_node_name, 1),
                   create_using=type(endpoint_a),
                   **endpoint_a.attr)

    return new_node_name


def subdivide_endpoint(k: PlanarDiagram, endpoint: Endpoint, **attr) -> str:
    """
    Subdivides an endpoint by introducing a new node. The endpoint is at position 0 of the new node

    Args:
        k (PlanarDiagram): The planar diagram.
        endpoint (Endpoint): The endpoint where the subdivision occurs.
        attr (dict): Additional attributes for the new node.

    Returns:
        str: The name of the newly created node.
    """
    return subdivide_arc(k, [endpoint, k.twin(endpoint)], **attr)
