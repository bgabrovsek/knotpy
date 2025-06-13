"""
This module provides functions for manipulating and modifying planar diagrams,
which are representations of mathematical knots or graphs. It includes
functionality for inserting arcs between nodes and endpoints while maintaining
oriented or unoriented attributes in the given planar diagram structure. The
module is intended for use in knot theory or graph-based applications.
"""

__all__ = ["insert_arc", "insert_endpoint", "insert_new_leaf", "insert_loop"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node.vertex import Vertex
from knotpy.algorithms.naming import unique_new_node_name

def insert_arc(k: PlanarDiagram, arc:tuple, **attr) -> None:



    endpoint_a, endpoint_b = arc
    node_a, position_a = endpoint_a
    node_b, position_b = endpoint_b

    is_oriented = k.is_oriented()

    _insert_none_at_node_position(k, node_a, position_a)
    _insert_none_at_node_position(k, node_b, position_b)


    k.set_endpoint(
        endpoint_for_setting=(node_a, position_a),
        adjacent_endpoint=(node_b, position_b),
        create_using=IngoingEndpoint if is_oriented else Endpoint,
        **attr
    )


    k.set_endpoint(
        endpoint_for_setting=(node_b, position_b),
        adjacent_endpoint=(node_a, position_a),
        create_using=OutgoingEndpoint if is_oriented else Endpoint,
        **attr
    )


def insert_arc2(k: PlanarDiagram, arc:tuple, **attr) -> None:
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
    # TODO: this does not work



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

def insert_loop(k: PlanarDiagram, endpoint: tuple | Endpoint, **attr) -> None:

    node, pos = endpoint

    # make space for the endpoint in the incident list
    _insert_none_at_node_position(k, node, pos, count=2)

    k._nodes[node]._inc[pos] = Endpoint(node=node, position=pos + 1, **attr)  # todo: orientable case
    k._nodes[node]._inc[pos + 1] = Endpoint(node=node, position=pos, **attr)  # todo: orientable case


def insert_endpoint(k: PlanarDiagram, target_endpoint, adjacent_endpoint, **attr) -> None:
    """Insert an endpoint in place and shift the other endpoints counter-clockwise.
    Args:
        k (PlanarDiagram): The planar diagram where the endpoint is being inserted.
        target_endpoint (tuple): A tuple representing the target endpoint as `(node, position)`.
        adjacent_endpoint (tuple): A tuple representing the adjacent endpoint as `(node, position)`.
    
    Returns:
        None

    TODO: rewrite this entire function: subdivide edges around point, insert none at the end and then permute the edges using the permutation furnction
    this way no new logic needs to bu built (attributes...). it will all be much cleaner.
    """
    node, pos = target_endpoint

    # make space for the endpoint in the incident list
    _insert_none_at_node_position(k, node, pos)

    # if an endpoint is not given, create it
    if not isinstance(adjacent_endpoint, Endpoint):
        adjacent_endpoint = Endpoint(*adjacent_endpoint)  # todo: orientable case

    if not isinstance(k._nodes[node], Vertex):
        raise ValueError("Cannot insert an endpoint at a non-vertex crossing.")

    # actually place the endpoint
    # TODO: use k.set_endpoint
    k._nodes[node]._inc[pos] = adjacent_endpoint
    k._nodes[node]._inc[pos].attr.update(attr)

    # TODO: should we also adjust twin node? (no)


def _insert_none_at_node_position(k:PlanarDiagram, node, position, count=1):
    """Insert a 'None' at a node position. This is a temporary modification of a diagram and changes the diagram
    to a non-valid diagram. Works inplace."""
    node_inst = k.nodes[node]

    # changes to be made  # TODO: optimize
    changes = []
    for i, adj_ep in enumerate(node_inst[position:], start=position):
        ep_target = k.endpoint_from_pair((node, i))
        changes.append((adj_ep.node, adj_ep.position, i + count, type(ep_target), ep_target.attr))

    for adj_node, adj_pos, new_pos, ep_type, ep_attr in changes:
        k.nodes[adj_node][adj_pos] = ep_type(node=node, position=new_pos, **ep_attr)

    for i in range(count):
        k._nodes[node]._inc.insert(position + i, None)


def insert_new_leaf(k:PlanarDiagram, target_endpoint, new_node_name=None):

    if new_node_name is None:
        new_node_name = unique_new_node_name(k)
    node, pos = target_endpoint

    k.add_vertex(new_node_name)
    _insert_none_at_node_position(k, node, pos)
    k.set_arc((target_endpoint, (new_node_name, 0)))

    return  new_node_name


def parallelize_arc(k: PlanarDiagram, arc, **attr):

    #print("paralelize", k, "arc",  arc)
    ep_a, ep_b = arc
    node_a, pos_a = ep_a
    node_b, pos_b = ep_b

    if node_a == node_b:
        raise NotImplementedError("Parallelizing loops not implemented.")


    if not isinstance(k.nodes[node_a], Vertex) or not isinstance(k.nodes[node_b], Vertex):
        raise ValueError("Can only parallelize arcs between vertices.")


    #print("insert", ((node_a, pos_a+1), (node_b, pos_b)))
    insert_arc(k, ((node_a, pos_a+1), (node_b, pos_b)), **attr)
    #print("ok:", k)


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