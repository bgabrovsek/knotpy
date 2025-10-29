# knotpy/algorithms/topology.py

__all__ = [
    "is_unlink", "is_unknot", "number_of_unknots", "is_knot", "is_link",
    "is_planar_graph", "is_empty_diagram",
    "is_knotoid", "is_linkoid",
    "is_leaf", "leafs",
    "is_loop", "loops",
    "is_kink", "kinks", "kink_region_iterator",
    "bridges", "is_bridge",
    "edges", "overstrands",
    "is_adjacent", "is_incident", "open_arc"
]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek"

from collections import defaultdict

from knotpy.utils.disjoint_union_set import DisjointSetUnion
from knotpy.classes.endpoint import Endpoint, OutgoingEndpoint, IngoingEndpoint
from knotpy.algorithms.cut_set import _is_arc_cut_set
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram, Diagram
from knotpy.classes.node import Vertex, Crossing
from knotpy.algorithms.components_link import number_of_link_components
from knotpy.algorithms.naming import multiple_unique_new_node_names, unique_new_node_name



def _is_vertex_an_unknot(k: PlanarDiagram, vertex) -> bool:
    """Return True if `vertex` is a degree-2 vertex whose two ends form a loop to itself."""
    return len(k.nodes[vertex]) == 2 and k.nodes[vertex][0].node == k.nodes[vertex][1].node == vertex


def _split_nodes_by_type(k: PlanarDiagram) -> dict:
    """Group node names by their concrete node class."""
    grouped = defaultdict(set)
    for node in k.nodes:
        grouped[type(k.nodes[node])].add(node)
    return grouped


def is_unlink(k: PlanarDiagram) -> bool:
    """Return True if the diagram is empty or all nodes are unknots (isolated looped vertices)."""
    return len(k) == 0 or all(_is_vertex_an_unknot(k, v) for v in k.nodes)


def is_unknot(k: PlanarDiagram) -> bool:
    """Return True if the diagram is a single unknot component."""
    return len(k) == 1 and is_unlink(k)


def number_of_unknots(k: PlanarDiagram) -> int:
    """Return the number of degree-2 looped vertices (unknots)."""
    return sum(1 for v in k.vertices if _is_vertex_an_unknot(k, v))


def is_knot(k: PlanarDiagram) -> bool:
    """Return True if all nodes are crossings and the diagram has a single link component."""

    if is_unknot(k):
        return True
    return all(type(k.nodes[node]) is Crossing for node in k.nodes) and number_of_link_components(k) == 1


def is_link(k: PlanarDiagram) -> bool:
    """Return True if all nodes are crossings (possibly multiple components)."""
    return all(type(k.nodes[node]) is Crossing for node in k.nodes)


def is_planar_graph(k: PlanarDiagram) -> bool:
    """Return True if all nodes are vertices (no crossings)."""
    return all(type(k.nodes[node]) is Vertex for node in k.nodes)


def is_empty_diagram(k: PlanarDiagram) -> bool:
    """Return True if the diagram has no nodes."""
    return len(k) == 0


def is_knotoid(k: PlanarDiagram) -> bool:
    """Return True if the diagram is a (multi)-knotoid (exactly two degree-1 vertices, rest crossings)."""
    node_sets = _split_nodes_by_type(k)
    return (
        len(node_sets[Crossing]) == len(k) - 2
        and len(node_sets[Vertex]) == 2
        and all(k.degree(node) == 1 for node in node_sets[Vertex])
    )


def is_linkoid(k: PlanarDiagram) -> bool:
    """Return True if the diagram is a multi-linkoid (even number of leaf vertices; others crossings)."""
    node_sets = _split_nodes_by_type(k)
    return (
        len(node_sets[Crossing]) + len(node_sets[Vertex]) == len(k)
        and len(node_sets[Vertex]) % 2 == 0
        and all(k.degree(node) == 1 for node in node_sets[Vertex])
    )


def is_leaf(k: PlanarDiagram, node) -> bool:
    """Return True if `node` is a degree-1 vertex."""
    return k.degree(node) == 1 and isinstance(k.nodes[node], Vertex)


def leafs(k: PlanarDiagram) -> set:
    """Return the set of degree-1 vertices."""
    return {node for node in k.vertices if k.degree(node) == 1}


def is_loop(k: PlanarDiagram, arc_or_endpoint) -> bool:
    """Return True if an arc/endpoint forms a loop (an arc whose ends are on the same node which is a Vertex).

    Args:
        k: Diagram.
        arc_or_endpoint: Either a single `Endpoint` or a 2-endpoint container (arc).

    Notes:
        “Kink” is a special loop notion at crossings; see `is_kink`.
    """
    ep1, ep2 = (arc_or_endpoint, k.twin(arc_or_endpoint)) if isinstance(arc_or_endpoint, Endpoint) else arc_or_endpoint
    return isinstance(k.nodes[ep1.node], Vertex) and ep1.node == ep2.node


def loops(k: PlanarDiagram) -> list:
    """Return a list of arcs (each a 2-endpoint container) that are loops."""
    return [arc for arc in k.arcs if is_loop(k, arc)]


def is_kink(k: PlanarDiagram, endpoint: Endpoint) -> bool:
    """Return True if `endpoint` forms a kink at a crossing (CCW neighbor is itself)."""
    if not isinstance(k.nodes[endpoint.node], Crossing):
        return False
    return k.nodes[endpoint.node][(endpoint.position - 1) % 4] == endpoint


def kinks(k: PlanarDiagram, crossing=None) -> set:
    """Return the set of kink endpoints; optionally restrict to a given `crossing`."""
    if crossing is None:
        return {ep for ep in k.endpoints if is_kink(k, ep)}
    if type(k.nodes[crossing]) is not Crossing:
        raise ValueError(f"The node {crossing} is not a crossing")
    return {ep for ep in k.endpoints[crossing] if is_kink(k, ep)}


def kink_region_iterator(k: PlanarDiagram, of_node=None):
    """Yield singleton “regions” (lists with one endpoint) representing kinks at crossings.

    Args:
        k: Diagram.
        of_node: If given, only consider kinks attached to this node.
    """
    for node in (k.crossings if of_node is None else (of_node,)):
        for ep in k.nodes[node]:
            # Is ep equal to its CCW neighbor? (kink)
            if ep == k.nodes[ep.node][(ep.position + 3) & 3]:
                yield [ep]


def bridges(k: PlanarDiagram) -> set:
    """Return the set of bridges (arcs whose removal disconnects the diagram) using a fast face-based test.

    Note:
        This uses a face incidence heuristic (fast) which may not be valid for already disjoint diagrams.
        For a robust (but slower) cut-set test, use `_is_arc_cut_set`.
    """
    return {arc for r in k.faces for arc in k.arcs if arc.issubset(r)}


def is_bridge(k: PlanarDiagram, arc_or_endpoint) -> bool:
    """Return True if the given arc/endpoint is a bridge (a size-1 arc cut-set).

    Args:
        k: Diagram.
        arc_or_endpoint: Either an `Endpoint` (we test the arc with its twin) or a 2-endpoint container.

    Raises:
        TypeError: if input is neither an `Endpoint` nor a 2-endpoint container.
    """
    if isinstance(arc_or_endpoint, Endpoint):
        return _is_arc_cut_set(k, ((arc_or_endpoint, k.twin(arc_or_endpoint)),))
    elif isinstance(arc_or_endpoint, (set, frozenset, tuple, list)):
        return _is_arc_cut_set(k, (arc_or_endpoint,))
    else:
        raise TypeError("arc_or_endpoint must be an Endpoint or an arc (set/tuple/list of two Endpoints).")


def path_from_endpoint(k: PlanarDiagram, endpoint: Endpoint) -> list[Endpoint]:
    """Follow a strand starting at `endpoint` until reaching a vertex (or a cycle closes).

    For crossings, the path alternates “twin” and “across” at the crossing (position + 2).
    For vertices, the path stops after stepping to the twin.

    Args:
        k: Diagram.
        endpoint: Starting endpoint (must be `Endpoint`).

    Returns:
        Ordered list of endpoints along the strand (endpoint, twin, next, twin, ...).
    """
    if not isinstance(endpoint, Endpoint):
        raise TypeError(f"Endpoint {endpoint} should be of type Endpoint")

    path: list[Endpoint] = []
    ep: Endpoint = endpoint

    while True:
        path.append(ep)
        path.append(twin_ep := k.twin(ep))  # jump to twin
        if isinstance(k.nodes[twin_ep.node], Crossing):
            ep = k.endpoint_from_pair((twin_ep.node, (twin_ep.position + 2) % 4))
        else:
            break
        if ep is endpoint:
            break

    return path


def edges(k: PlanarDiagram, **endpoint_attributes) -> list[list[Endpoint]]:
    """Return ordered strands (“edges”) of the diagram.

    Each edge is a list of endpoints starting at a vertex (or forming a closed component)
    and proceeding through crossings as per `path_from_endpoint`. Endpoints can be
    filtered by attributes via keyword arguments (e.g., `color="red"`).

    Args:
        k: Diagram.
        **endpoint_attributes: Attribute filters that all endpoints in a strand must satisfy.

    Returns:
        List of strands, each a list of `Endpoint`.
    """
    list_of_edges: list[list[Endpoint]] = []
    unused_endpoints = set(k.endpoints)

    # terminal nodes (vertices); prefer to start from Outgoing/Ingoing endpoints if oriented
    terminals = [node for node in k.nodes if isinstance(k.nodes[node], Vertex)]

    def _endpoints_have_attribute(eps: list[Endpoint], attr: dict) -> bool:
        if not attr:
            return True
        for ept in eps:
            for key, value in attr.items():
                if key not in ept.attr or ept.attr[key] != value:
                    return False
        return True

    priority = {OutgoingEndpoint: 0, IngoingEndpoint: 1, Endpoint: 2}
    start_candidates = sorted(
        (ep for node in terminals for ep in k.nodes[node]),
        key=lambda x: priority.get(type(x), 3),
    )

    # Start with strands that originate at terminals
    for ep in start_candidates:
        if ep in unused_endpoints:
            strand = path_from_endpoint(k, k.twin(ep))
            strand_set = set(strand)
            if not strand_set.issubset(unused_endpoints):
                raise ValueError(f"Endpoints {strand} should be unused")
            unused_endpoints -= strand_set
            if _endpoints_have_attribute(strand, endpoint_attributes):
                list_of_edges.append(strand)

    # Remaining strands correspond to closed components
    while unused_endpoints:
        start = next(iter(unused_endpoints))
        strand = path_from_endpoint(k, start)
        strand_set = set(strand)
        if not strand_set.issubset(unused_endpoints):
            raise ValueError(f"Endpoints {strand} should be unused")
        unused_endpoints -= strand_set
        if _endpoints_have_attribute(strand, endpoint_attributes):
            list_of_edges.append(strand)

    return list_of_edges


def overstrands(k: Diagram):
    """Return a partition of endpoints into sets that belong to the same overstrand.

    Overstrand relation:
      - At each crossing, pair the two over-passing endpoints.
      - Along arcs, pair twins.

    Returns:
        A list of sets (each set is an overstrand’s endpoints).
    """
    dsu = DisjointSetUnion(k.endpoints)
    for c in k.crossings:
        eps = k.endpoints[c]
        dsu[eps[1]] = k.endpoint_from_pair(eps[3])
    for ep1, ep2 in k.arcs:
        dsu[ep1] = k.endpoint_from_pair(ep2)
    return dsu.classes()

def is_adjacent(k, obj1, obj2):
    """Return True if `obj1` and `obj2` are adjacent to each other in the diagram."""

    # node-node
    if obj1 in k.nodes and obj2 in k.nodes:
        return any(ep.node == obj2 for ep in k.nodes[obj1])

    # endpoint-endpoint
    if obj1 in k.endpoints and obj2 in k.endpoints:
        return obj1.node == obj2.node

    # arc-arc
    if obj1 in k.arcs and obj2 in k.arcs:
        print("yay")

    return False

def is_incident(k, obj1, obj2):
    """Return True if `obj1` and `obj2` are incident to each other in the diagram."""
    pass

def is_knot_like_knotoid(knot):
    _leafs = leafs(knot)
    leafs_faces = [face for face in knot.faces if any(leaf in [ep.node for ep in face] for leaf in _leafs)]
    return len(leafs_faces) == 1 and len(leafs_faces[0]) == 2

def open_arc(k: PlanarDiagram, arc, inplace=False):
    if not inplace:
        k = k.copy()
    ep1, ep2 = arc
    node1 = unique_new_node_name(k)
    k.add_node(node1, create_using=Vertex, degree=1)
    node2 = unique_new_node_name(k)
    k.add_node(node2, create_using=Vertex, degree=1)
    #print("endpoints", ep1, ep2)
    #print(type(ep1), type(ep2))

    k.set_endpoint(ep1, (node2, 0), create_using=type(ep2))
    k.set_endpoint((node2, 0), ep1, create_using=type(ep1))
    k.set_endpoint(ep2, (node1, 0), create_using=type(ep1))
    k.set_endpoint((node1, 0), ep2, create_using=type(ep2))

    return k

if __name__ == "__main__":
    pass