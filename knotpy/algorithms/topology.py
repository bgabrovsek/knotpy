from collections import defaultdict

from knotpy.classes.endpoint import Endpoint, OutgoingEndpoint, IngoingEndpoint
from knotpy.algorithms.cut_set import is_arc_cut_set
from knotpy.algorithms.paths import path_from_endpoint
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node import Vertex, Crossing


def _split_nodes_by_type(k: PlanarDiagram) -> dict:
    """
    Categorizes the nodes in a planar diagram by their types.

    This function returns a dictionary where the keys represent node types
    (e.g., `Crossing`, `Vertex`, etc.) and the values are sets containing
    the nodes that belong to each respective type.

    Args:
        k (PlanarDiagram): The planar diagram whose nodes are to be categorized.

    Returns:
        dict: A dictionary with node types as keys and sets of corresponding nodes as values.
   """

    result = defaultdict(set)
    for node in k.nodes:
        result[type(k.nodes[node])].add(node)
    return result

def is_unknot(k: PlanarDiagram) -> bool:
    if len(k) == 1:
        node = next(iter(k.nodes))
        if isinstance(k.nodes[node], Vertex) and k.degree(node) == 2:
            return True
    return False



def is_knot(k: PlanarDiagram) -> bool:
    """
    Determines whether the given planar diagram represents a knot.

    A diagram is a knot if all its nodes are crossings.

    Args:
        k (PlanarDiagram): The planar diagram.

    Returns:
        bool: True if all nodes are crossings, False otherwise.
    """

    return all(type(k.nodes[node]) is Crossing for node in k.nodes)


def is_planar_graph(k: PlanarDiagram) -> bool:
    """
    Determines whether the given planar diagram represents a planar graph.

    Args:
        k (PlanarDiagram): The planar diagram.

    Returns:
        bool: True if all nodes are vertices, False otherwise.
    """
    return all(type(k.nodes[node]) is Vertex for node in k.nodes)


def is_empty_diagram(k: PlanarDiagram) -> bool:
    return len(k) == 0

def is_knotoid(k: PlanarDiagram) -> bool:
    """Is the diagram a (multi) knotoid?"""
    node_sets = _split_nodes_by_type(k)
    return (len(node_sets[Crossing]) == len(k) - 2 and
            len(node_sets[Vertex]) == 2 and
            all(k.degree(node) == 1 for node in node_sets[Vertex]))

def is_linkoid(k: PlanarDiagram) -> bool:
    """Is the diagram a multi-linkoid?"""
    node_sets = _split_nodes_by_type(k)
    return (len(node_sets[Crossing]) + len(node_sets[Vertex]) == len(k) and
            len(node_sets[Vertex]) % 2 == 0 and
            all(k.degree(node) == 1 for node in node_sets[Vertex]))


def is_loop(k: PlanarDiagram, arc_or_endpoint) -> bool:
    """
    Determine whether the given arc or endpoint forms a loop in the planar diagram.

    A loop is an arc that connects a node to itself. If given an endpoint, the function checks
    whether its twin belongs to the same node. If given an arc (set of two endpoints), it checks
    whether both endpoints belong to the same node.
    The difference between is_kink() is that kinks are defined at crossings and contain only the endpoint.

    Args:
        k (PlanarDiagram): The planar diagram.
        arc_or_endpoint (Union[Endpoint, set[Endpoint], frozenset[Endpoint]]):
            The endpoint or arc to check.

    Returns:
        bool: True if the arc or endpoint forms a loop, False otherwise.

    Raises:
        TypeError: If `arc_or_endpoint` is not an `Endpoint` or a set of endpoints.
    """

    ep1, ep2 = (arc_or_endpoint, k.twin(arc_or_endpoint)) if isinstance(arc_or_endpoint, Endpoint) else arc_or_endpoint
    return isinstance(k.nodes[ep1.node], Vertex) and ep1.node == ep2.node


def loops(k: PlanarDiagram) -> list:
    """
    Returns a set of arcs that form loops in the planar diagram.

    A loop is an arc that connects a node to itself, provided the node is not a vertex.
    An arc is a tuple of two endpoints.

    Args:
        k (PlanarDiagram): The planar diagram.

    Returns:
        set: A set of arcs that are loops.
    """
    return [arc for arc in k.arcs if is_loop(k, arc)]
    # return set(arc for arc in k.arcs if
    #            len({ep.node for ep in arc}) == 1
    #            and all(not isinstance(k.nodes[ep.node], Crossing) for ep in arc))


def is_kink(k: PlanarDiagram, endpoint: Endpoint) -> bool:
    """
    Determines whether an endpoint forms a kink in the planar diagram.

    Args:
        k (PlanarDiagram): The planar diagram.
        endpoint (Endpoint): The endpoint being checked.

    Returns:
        bool: True if the endpoint forms a kink, False otherwise.
    """
    if not isinstance(k.nodes[endpoint.node], Crossing):
        return False
    #print("is kink", k, endpoint)
    return k.nodes[endpoint.node][(endpoint.position - 1) % 4] == endpoint


def kinks(k: PlanarDiagram, crossing=None) -> set:
    """
    Returns the set of kinks in the planar diagram. A kink is given as an endpoint that defines a face.
    Note that the twin of a kink is not a kink.

    A kink is a loop at a crossing where traversal in a counterclockwise direction returns to the same node.

    Args:
        k (PlanarDiagram): The planar diagram.
        crossing: If provided, only kinks attached to the specified crossing will be considered.

    Returns:
        set: A set of kinks.
    """

    if crossing is None:
        return set(ep for ep in k.endpoints if is_kink(k, ep))
    else:
        if type(k.nodes[crossing]) != Crossing:
            # perhaps we could just return an empty set instead of throwing an error?
            raise ValueError(f"The node {crossing} is not a crossing")

        return set(ep for ep in k.endpoints[crossing] if is_kink(k, ep))


def kink_region_iterator(k: PlanarDiagram, of_node=None):
    """
    An iterator (generator) over regions of kinks/loops.

    The regions are singleton lists containing the endpoint. See also regions().

    Args:
        k (PlanarDiagram): planar diagram object
        of_node: if of_node is not None, only the kinks attached to the node will be given.

    Returns:
        iterator: an iterator (generator) over kink regions.
    """
    for node in k.crossings if of_node is None else (of_node,):  # loop through all crossings if of_node is not given
        for ep in k.nodes[node]:
            if ep == k.nodes[ep.node][(ep.position + 3) & 3]:  # is the endpoint and the ccw endpoint the same?
                yield [ep]


def bridges(k: PlanarDiagram) -> set:
    """
    Return the set of bridges in the planar diagram. A bridge is an arc whose removal disconnects the diagram into two disjoint components.

    Args:
        k (PlanarDiagram): The planar diagram.

    Returns:
        set: A set of bridges represented as arcs.
    """
    #return set(arc for arc in k.arcs if is_arc_cut_set(k, [arc]))
    # testing faces is much faster than cut-sets, buy might not work for disjoint diagrams
    return set(arc for r in k.faces for arc in k.arcs if arc.issubset(r))


def is_bridge(k: PlanarDiagram, arc_or_endpoint) -> bool:
    """
    Determine whether the given arc or endpoint is a bridge in the planar diagram.

    A bridge is an arc whose removal disconnects the diagram into two disjoint components.
    This function checks if the provided `arc_or_endpoint` forms a cut set.

    Args:
        k (PlanarDiagram): The planar diagram.
        arc_or_endpoint (Union[Endpoint, set[Endpoint], frozenset[Endpoint]]):
            The arc (set of two endpoints) or a single endpoint to check.

    Returns:
        bool: True if the arc or endpoint is a bridge, False otherwise.

    Raises:
        TypeError: If `arc_or_endpoint` is not an `Endpoint` or a set of endpoints.

    Notes:
        - If an `Endpoint` is provided, its twin is included in the check.
        - If a set of endpoints is provided, the function evaluates whether their removal disconnects the diagram.
    """

    if isinstance(arc_or_endpoint, Endpoint):
        return is_arc_cut_set(k, (arc_or_endpoint, k.twin(arc_or_endpoint)))

    elif isinstance(arc_or_endpoint, (set, frozenset, tuple, list)):
        return is_arc_cut_set(k, (arc_or_endpoint,))

    else:
        raise TypeError("arc_or_endpoint must be an Endpoint or an arc (set of two Endpoints).")


def edges(k: PlanarDiagram, **endpoint_attributes) -> list:
    """
    Return a list of ordered edges/strands of a knotted graph or a knot, or link.
    An edge is a list of endpoints that starts at a vertex (not a crossing) and ends at a vertex.
    In case there are closed components, the edges represent the closed component starting and ending at a crossing.

    An edge is represented as an ordered list of endpoints, where the first two pairs are twin endpoints,
    and the third element is an adjacent endpoint over a crossing.

    Args:
        k (PlanarDiagram): The planar diagram.
        endpoint_attributes (dict): A dictionary of attribute filters for endpoints.

    Returns:
        list: A list of ordered strands that represent the edges of the diagram.
    """

    list_of_edges = []
    unused_endpoints = set(k.endpoints)

    # start edges with terminals
    terminals = [node for node in k.nodes
                 if isinstance(k.nodes[node], Vertex)]

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

    priority = {OutgoingEndpoint: 0, IngoingEndpoint: 1, Endpoint: 2}
    start_endpoint_candidates = sorted([ep for node in terminals for ep in k.nodes[node]], key=lambda x: priority[type(x)])

    # first follow strands from the terminals
    for ep in start_endpoint_candidates:
        #print(ep, type(ep))
        if ep in unused_endpoints:  # skip ingoing to follow orientation
            strand = path_from_endpoint(k, k.twin(ep))
            strand_set = set(strand)
            if not strand_set.issubset(unused_endpoints):  # sanity check
                raise ValueError(f"Endpoints {strand} should be unused")
            unused_endpoints -= strand_set  # remove them from unused

            if _endpoints_have_attribute(strand, endpoint_attributes):
                list_of_edges.append(strand)

    # if there are still endpoints available, they come from closed components

    while unused_endpoints:
        strand = path_from_endpoint(k, next(iter(unused_endpoints)))  # TODO: start from outgoing endpoint
        strand_set = set(strand)
        if not strand_set.issubset(unused_endpoints):  # sanity check
            raise ValueError(f"Endpoints {strand} should be unused")
        unused_endpoints -= strand_set  # remove them from unused
        if _endpoints_have_attribute(strand, endpoint_attributes):
            list_of_edges.append(strand)

    return list_of_edges
