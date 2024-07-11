"""

"""

__all__ = ["edges", "number_of_edges", "parallel_arcs","bridges","loops", "kinks", "cut_edges", "cut_vertices",
           "is_knot", "is_planar_graph",
           "subdivide_endpoint", "subdivide_arc", "insert_arc"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'

import random
import string
from collections import Counter

from knotpy.classes.node import Crossing, VirtualCrossing, Terminal, Bond
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node.vertex import Vertex
from knotpy.algorithms.node_operations import name_for_new_node


def path_from_endpoint(k: PlanarDiagram, endpoint: Endpoint) -> list:
    """Return the path (edge/strand or part of an edge/strand) starting from the endpoint. A path stops at a vertex-like
    node or is a closed component. A path is an edge or part of an edge.
    :param k: planar diagram
    :param endpoint: starting endpoint
    :return: a list of endpoints continuing from the endpoint to a vertex-like node
    """

    if not isinstance(endpoint, Endpoint):
        raise TypeError(f"Endpoint {endpoint} should be of type Endpoint")

    if isinstance(endpoint, IngoingEndpoint):
        raise NotImplementedError("Path from ingoing endpoint not yet implemented")  # TODO: in this case, we should first jump over crossing

    path = []
    ep = endpoint

    while True:
        path.append(ep)
        path.append(twin_ep := k.twin(ep))  # jump to twin
        if isinstance(k.nodes[twin_ep.node], Crossing):
            ep = k.get_endpoint_from_pair((twin_ep.node, (twin_ep.position + 2) % 4))
        else:
            break

        if ep is endpoint:
            break

        # if isinstance(k.nodes[twin_ep.node], Crossing):
        #     ep = twin_ep[0], (twin_ep[1] + 2) % 4  # same node, opposite crossing
        # else:
        #     break
    return path


def edges(k: PlanarDiagram, **endpoint_attributes) -> list:


    """Return a list of (ordered) edges/strands of the diagram. An edge is an (ordered) list of endpoints of alternating
    endpoints, the first two pairs are twins, the third element is an adjacent endpoint over the crossing.
    The edge start from vertex-like nodes if they exist, otherwise from a crossing-like node. A crossing-like node is
    detected by a non-None return value of jump_over(0). The edge follow orientation if the diagram is oriented.
    :param k: PlanarDiagram instance
    :param endpoint_attributes: a filter of attributes of the endpoint. Only edges are returned that have the
    given attributes.
    :return: list of (ordered) strands

    Example:
    - edges(k) returns all edges of the spatial graph
    - edges(k, color=1) returns all edges that have color 1
    """
    # TODO: is this now a view?
    list_of_edges = []
    unused_endpoints = set(k.endpoints)

    terminals = [node for node in k.nodes
                 if isinstance(k.nodes[node], Vertex)
                 or isinstance(k.nodes[node], Terminal)
                 or isinstance(k.nodes[node], Bond)]

    def _endpoints_have_attribute(eps, attr):
        # TODO: make pythonic
        if attr:
            for ept in eps:
                for key, value in attr.items():
                    if key not in ept.attr:
                        return False
                    else:
                        if ept.attr[key] != value:
                            return False
        return True

    # first follow strands from the terminals
    for node in terminals:
        for ep in k.nodes[node]:
            #print(ep, type(ep))
            if ep in unused_endpoints and not isinstance(ep, IngoingEndpoint):  # skip ingoing to follow orientation
                strand = path_from_endpoint(k, k.twin(ep))
                strand_set = set(strand)
                if not strand_set.issubset(unused_endpoints):  # sanity check
                    raise ValueError(f"Endpoints {strand} should be unused")
                unused_endpoints -= strand_set  # remove them from unused

                if _endpoints_have_attribute(strand, endpoint_attributes):
                    list_of_edges.append(strand)

    #print(list_of_edges)

    # if there are still endpoints available, they come from closed components
    while unused_endpoints:
        strand = path_from_endpoint(k, next(iter(unused_endpoints)))
        strand_set = set(strand)
        if not strand_set.issubset(unused_endpoints):  # sanity check
            raise ValueError(f"Endpoints {strand} should be unused")
        unused_endpoints -= strand_set  # remove them from unused
        if _endpoints_have_attribute(strand, endpoint_attributes):
            list_of_edges.append(strand)

    return list_of_edges


def number_of_edges(k: PlanarDiagram) -> int:
    """Return the number of strands of the diagram.
    :param k:
    :return:
    """
    return len(edges(k))  # TODO: make faster using EquivalenceRelation


def parallel_arcs(k):
    """Return a set of tuples, each tuple consists of arcs that are parallel. The incident nodes can be any type
    (crossing, vertex,...)
    TODO: consider parallelism up to orientation
    :param k: the planar diagram
    :return: set of tuples that are parallel arcs
    """
    pass

def bridges(k):
    """Return a set of bridges of k. A bridge is an arc that once removed, splits the diagram into two disjoint parts.
    :param k: the planar diagram
    :return: set of bridges represented by an arc
    """
    return set(arc for r in k.faces for arc in k.arcs if arc.issubset(r))

def cut_edges(k):
    return bridges(k)

def subdivide_endpoint(k:PlanarDiagram, endpoint, **attr):
    """

    :param k:
    :param endpoint:
    :return: name of new node created
    """
    return subdivide_arc(k, [endpoint, k.twin(endpoint)], **attr)


def subdivide_arc(k:PlanarDiagram, arc, **attr):
    """

    :param k:
    :param arc:
    :return: name of new node created
    """
    endpoint_a, endpoint_b = arc


    if not isinstance(endpoint_a, Endpoint):
        endpoint_a = k.get_endpoint_from_pair(endpoint_a)
    if not isinstance(endpoint_b, Endpoint):
        endpoint_b = k.get_endpoint_from_pair(endpoint_b)

    new_node = name_for_new_node(k)
    k.add_node(node_for_adding=new_node, create_using=Vertex, degree=2, **attr)
    k.set_endpoint(endpoint_for_setting=(new_node, 0),
                   adjacent_endpoint=(endpoint_a.node, endpoint_a.position),
                   create_using=type(endpoint_a),
                   **endpoint_a.attr)
    k.set_endpoint(endpoint_for_setting=(endpoint_a.node, endpoint_a.position),
                   adjacent_endpoint=(new_node, 0),
                   create_using=type(endpoint_a).reverse_type())

    k.set_endpoint(endpoint_for_setting=(new_node, 1),
                   adjacent_endpoint=(endpoint_b.node, endpoint_b.position),
                   create_using=type(endpoint_b),
                   **endpoint_b.attr)
    k.set_endpoint(endpoint_for_setting=(endpoint_b.node, endpoint_b.position),
                   adjacent_endpoint=(new_node, 1),
                   create_using=type(endpoint_b).reverse_type())

    return new_node




def insert_arc(k: PlanarDiagram, node_a, position_a, node_b, position_b, **attr):
    """Insert an arc between node a and node b at positions position_a and position b, respectively.
    If the diagram is oriented, the arc goes from a to b.
    :param k:
    :param node_a:
    :param position_a:
    :param node_b:
    :param position_b:
    :param attr:
    :return:
    """
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

    perm = {i: (i if i < position_a else i + 1) for i in range(k.degree(node_a) - 1)}
    perm[k.degree(node_a) - 1] = position_a
    k.permute_node(node_a, perm)

    perm = {i: (i if i < position_b else i + 1) for i in range(k.degree(node_b) - 1)}
    perm[k.degree(node_b) - 1] = position_b
    k.permute_node(node_b, perm)

def articulation_nodes(k):
    """Return a list of articulation nodes or cut vertices. A vertex is a cut-vertex if its removal disconnects the
    graph."""

    nodes = set()
    for f in k.faces:
        # keep nodes that repeat twice or more in a face
        counts = Counter(ep.node for ep in f)
        nodes |= {node for node, count in counts.items() if count >= 2}

    return nodes


def cut_vertices(k):
    return articulation_nodes(k)

def loops(k):
    """Return a set of loops of k. A loop is an arc that connects the node to itself, but the node is not a crossing.
    See also kinks().
    :param k: the planar diagram
    :return: set of arcs that are loops
    """
    return set(arc for arc in k.arcs if
               len({ep.node for ep in arc}) == 1
               and all(not isinstance(k.nodes[ep.node], Crossing) for ep in arc))

def is_kink(k: PlanarDiagram, endpoint: Endpoint):
    """
    :param k:
    :param endpoint:
    :return:
    """
    if not isinstance(k.nodes[endpoint.node], Crossing):
        return False
    #print("is kink", k, endpoint)
    return k.nodes[endpoint.node][(endpoint.position - 1) % 4] == endpoint


def kinks(k, of_crossing=None):
    """Return a set of loops of k. A loop is defined at a crossing, such that as the endpoint (that defines the length 1
    face of the kink) in which, if we travel in ccw direction, we hit the same node.
    #an arc that connects the node to itself at a crossing. See also kinks().
    :param k: the planar diagram
    :param of_crossing:
    :return: set of bridges represented by an arc
    """
    #TODO we do not need to loop though all endpoints, just those of crossings
    return set(ep for ep in (k.endpoints if of_crossing is None else k.nodes[of_crossing]) if is_kink(k, ep))


    #if of_crossing is None:
    #    return
    #else
    # if of_crossing is None:
    #     return set(ep for ep in k.endpoints
    #                if isinstance(k.nodes[ep.node][ep.pos], Crossing) and k.nodes[ep.node][(ep.position - 1) % 4].node == ep.node)
    #     # return set(arc for arc in k.arcs if
    #     #            len({ep.node for ep in arc}) == 1
    #     #            and all(isinstance(k.nodes[ep.node], Crossing) for ep in arc))
    # else:
    #     #print(set(ep for ep in k.nodes[of_crossing]))
    #     return set(ep for ep in k.nodes[of_crossing] if ep.node == of_crossing == k.nodes[ep.node][(ep.position - 1) % 4].node)
    #     # return set(arc for arc in k.arcs[of_crossing] if
    #     #            len({ep.node for ep in arc}) == 1
    #     #            and all(isinstance(k.nodes[ep.node], Crossing) for ep in arc))


def kink_region_iterator(k, of_node=None):
    """An iterator (generator) over regions of kinks/loops. The regions are singleton lists containing the endpoint.
    See also regions().
    :param k: planar diagram object
    :param of_node: if of_node is not None, only the kinks attached to the node will be given
    :return: an iterator (generator) over kink regions.
    """

    for node in k.crossings if of_node is None else (of_node,):  # loop through all crossings if of_node is not given
        for ep in k.nodes[node]:
            if ep == k.nodes[ep.node][(ep.position + 3) & 3]:  # is the endpoint and the ccw endpoint the same?
                yield [ep]

def is_planar_graph(k):
    """Are are nodes vertices?
    :param k:
    :return:
    """
    return all(type(k.nodes[node]) is Vertex for node in k.nodes)



def is_knot(k):
    """Are all nodes crossings?
    :param k:
    :return:
    """
    return all(type(k.nodes[node]) is Crossing for node in k.nodes)



if __name__ == '__main__':
   # k = from_pd_notation("V[0,1,2],V[3,4,1],X[2,4,5,6],X[7,8,9,5],X[8,10,6,9],X[3,0,10,7]", create_using=SpatialGraph)
    pass