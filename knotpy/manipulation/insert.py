"""
This module provides functions for manipulating and modifying planar diagrams,
which are representations of mathematical knots or graphs. It includes
functionality for inserting arcs between nodes and endpoints while maintaining
oriented or unoriented attributes in the given planar diagram structure. The
module is intended for use in knot theory or graph-based applications.
"""

__all__ = ["insert_arc", "insert_endpoint", "insert_new_leaf"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node.vertex import Vertex
from knotpy.algorithms.naming import unique_new_node_name


def insert_arc(k: PlanarDiagram, arc:tuple, **attr) -> None:
    """
    Inserts an arc between two nodes at specified positions in place, adjusting
    their endpoint positions to accommodate the new arc.

    Args:
        k (PlanarDiagram): The planar diagram where the arc is being inserted.
        arc (tuple): A tuple containing two endpoints `(endpoint_a, endpoint_b)`
            where each endpoint is a tuple `(node, position)` specifying the
            node and position at which the arc should be connected.
        **attr: Additional attributes to apply to the arc.

    Raises:
        NotImplementedError: If an arc is attempted to be inserted within the
            same node (`node_a == node_b`).

    Returns:
        None
    """


    endpoint_a, endpoint_b = arc
    node_a, position_a = endpoint_a
    node_b, position_b = endpoint_b

    is_oriented = k.is_oriented()

    if node_a == node_b:
        raise NotImplementedError()

    k.set_endpoint(
        endpoint_for_setting=(node_a, k.degree(node_a)),
        adjacent_endpoint=(node_b, k.degree(node_b)),
        create_using=IngoingEndpoint if is_oriented else Endpoint,
        **attr
    )

    k.set_endpoint(
        endpoint_for_setting=(node_b, k.degree(node_b)),
        adjacent_endpoint=(node_a, k.degree(node_a)-1),
        create_using=OutgoingEndpoint if is_oriented else Endpoint,
        **attr
    )

    # Create a permutation dictionary for `node_a` to adjust the positions of
    # its endpoints. The dictionary maps existing positions to either the
    # same position (if it's less than `position_a`) or one position higher
    # to accommodate the insertion of the new arc. The last position is set
    # to `position_a` for the new arc.
    perm = {i: (i if i < position_a else i + 1) for i in range(k.degree(node_a) - 1)}
    perm[k.degree(node_a) - 1] = position_a
    k.permute_node(node_a, perm)

    # Similarly, create a permutation dictionary for `node_b` to adjust
    # its endpoint positions. The logic mirrors that of `node_a`, with
    # the last position assigned to `position_b` to accommodate the new arc.
    perm = {i: (i if i < position_b else i + 1) for i in range(k.degree(node_b) - 1)}
    perm[k.degree(node_b) - 1] = position_b
    k.permute_node(node_b, perm)

    # TODO: use insert_endpoint for inserting arcs


def insert_endpoint(k: PlanarDiagram, target_endpoint, adjacent_endpoint) -> None:
    """Insert an endpoint in place and shift the other endpoints counter-clockwise.
    Args:
        k (PlanarDiagram): The planar diagram where the endpoint is being inserted.
        target_endpoint (tuple): A tuple representing the target endpoint as `(node, position)`.
        adjacent_endpoint (tuple): A tuple representing the adjacent endpoint as `(node, position)`.
    
    Returns:
        None
    """

    target_type = type(target_endpoint) if isinstance(target_endpoint, Endpoint) else Endpoint
    if adjacent_endpoint is not None:
        adjacent_endpoint = k.endpoint_from_pair(adjacent_endpoint)

    node, pos = target_endpoint
    node_inst = k.nodes[node]

    if not isinstance(node_inst, Vertex):
        raise ValueError("Cannot insert an endpoint at a non-vertex crossing.")

    # changes to be made  # TODO: optimize
    changes = []
    for i, adj_ep in enumerate(node_inst[pos:], start=pos):
        ep_target = k.endpoint_from_pair((node, i))
        changes.append((adj_ep.node, adj_ep.position, i + 1, type(ep_target), ep_target.attr))

    for adj_node, adj_pos, new_pos, ep_type, ep_attr in changes:
        k.nodes[adj_node][adj_pos] = ep_type(node=node, position=new_pos, **ep_attr)

    # shift twin positions (THE CODE BELOW DOES NOT WORK, IT COMPLICATES ATTRIBUTES ON MULTIPLE (2 OR MORE) LOOPS IN THE NODE.)
    # for i, adj_ep in enumerate(node_inst[pos:], start=pos):
    #     ep_target = k.endpoint_from_pair((node, i))  # endpoint at target node for renumerating
    #     k.nodes[adj_ep.node][adj_ep.position] = type(ep_target)(node=node, position=i + 1, **ep_target.attr)  # set endpoint

    k._nodes[node]._inc.insert(pos, adjacent_endpoint)
    # TODO: should we also adjust twin node? (no)


def insert_new_leaf(k:PlanarDiagram, target_endpoint, new_node_name=None):

    if new_node_name is None:
        new_node_name = unique_new_node_name(k)

    k.add_vertex(new_node_name)
    insert_endpoint(k,target_endpoint=target_endpoint, adjacent_endpoint=None)
    k.set_arc((target_endpoint, (new_node_name, 0)))

    return  new_node_name






if __name__ == "__main__":

    k = PlanarDiagram()
    k.add_vertices_from("abc")
    k.set_arcs_from("a0b1,b0c1,c0a1")
    print(k)
    insert_new_leaf(k,("c",1), "M")
    print(k)


    k = PlanarDiagram()
    k.add_vertices_from("abc")
    k.set_arcs_from("a0b1,b0c1,c0a1")
    print(k)
    insert_arc(k,(("c",1),("b",1)))
    print(k)