"""
Putting a diagram into its canonical form.
"""

__all__ = ['canonical', 'canonical_generator']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

from collections.abc import Iterable
from queue import Queue
import string

from knotpy.algorithms.degree_sequence import neighbour_sequence
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node import Crossing, Vertex
from knotpy.manipulation.permute import permute_node
from knotpy.algorithms.disjoint_union import number_of_disjoint_components, disjoint_union_decomposition, disjoint_union
from knotpy.utils.func_utils import min_elements_by

_ascii_letters = string.ascii_lowercase + string.ascii_uppercase

def _under_endpoints_of_node(k: PlanarDiagram, node):
    """Return a tuple of endpoints that are under-endpoints in case of crossings and all endpoints in case of vertices."""
    return [(node, 0), (node, 2)] if isinstance(k.nodes[node], Crossing) else [(node, pos) for pos in range(k.degree(node))]


def _ccw_expand_node_names(k: PlanarDiagram, endpoint, node_names):
    """Label nodes in a planar diagram using a counterclockwise (CCW) traversal.

    This function starts from a given endpoint in the diagram and iteratively assigns integer labels to nodes in a
    counterclockwise direction. Nodes are traversed using a breadth-first search (BFS) approach.

    :param k: The planar diagram to process.
    :type k: PlanarDiagram
    :param endpoint: The starting endpoint for labeling.
    :type endpoint: tuple
    :param node_names: A list of ordered labels to assign to nodes.
    :type node_names: list[int]

    :return: A dictionary mapping original node identifiers to their new integer labels.
    :rtype: dict

    The function maintains a queue to ensure breadth-first traversal. It first visits a node, assigns it a label, and
    then explores its adjacent nodes in CCW order, enqueuing them for processing. The traversal continues until all
    reachable nodes are labeled.
    """
    node_relabel = dict()  # also holds as a "visited node" set
    node_first_position = dict()  # also holds as a "visited node" set
    endpoint_queue = Queue()
    endpoint_queue.put(endpoint)

    while not endpoint_queue.empty():
        v, pos = endpoint_queue.get()

        if v not in node_relabel:  # new node visited
            new_node_name = node_names[len(node_relabel)]
            node_relabel[v] = new_node_name  # rename the node to next available integer
            node_first_position[new_node_name] = pos
            v_deg = k.degree(v)

            # put all adjacent endpoints in queue in CCW order
            for relative_pos in range(1, v_deg):
                endpoint_queue.put((v, (pos + relative_pos) % v_deg))

        # go to the adjacent endpoint and add it to the queue
        adj_v, adj_pos = k.nodes[v][pos]

        if adj_v not in node_relabel:
            endpoint_queue.put((adj_v, adj_pos))
    return node_relabel, node_first_position


def canonical_generator(diagrams: Iterable):
    if not isinstance(diagrams, Iterable):
        raise TypeError("Input must be an iterable.")
    for _ in diagrams:
        yield canonical(_)

def canonical(k: PlanarDiagram | set | list | tuple | Iterable) -> PlanarDiagram | set | list | tuple:
    """
    Compute the canonical form of an unoriented planar diagram.

    This function processes an unoriented `PlanarDiagram` to determine its unique canonical form by iteratively
    relabeling the diagram’s nodes. The labeling begins at endpoints of vertices with the minimal degree and proceeds
    via breadth-first search (BFS) in a counterclockwise (CCW) order to achieve an ordered structure.

    Disjoint components of the planar diagram are handled separately, where they are individually canonicalized and
    then combined in their canonical order to produce the final result. The method ensures consistent ordering within
    each component and among components of the diagram.

    Warning:
        - For graphs containing degree-2 vertices, there may be ambiguities as the canonical form might not be unique.
        - If the input graph is disconnected, a `ValueError` is raised.

    Args:
        k (PlanarDiagram): The input planar diagram, such as a knot, graph, or other similar topological structure.

    Returns:
        PlanarDiagram: The canonical form of the input planar diagram, represented as a new `PlanarDiagram` instance.

    Raises:
        ValueError: If the graph is disconnected and cannot be transformed into a canonical form.
    """

    from knotpy.algorithms.naming import number_to_alpha

    # input is set/list/tuple
    if isinstance(k, (set, list, tuple)):
        return type(k)(canonical(_) for _ in k)

    if isinstance(k, Iterable):
        return [canonical(_) for _ in k]

    # input is unsupported
    if not isinstance(k, PlanarDiagram):
        raise TypeError(f"Cannot put a {type(k)} instance into canonical form.")

    # input is a planar diagram

    # TODO: In case of degree 2 vertices, the canonical form might not be unique.

    if len(k) == 0:
        return k.copy()

    # Generate node names: a,b,...,z,A,B,...,Z,aa,ab,...
    letters = _ascii_letters if len(k) <= len(_ascii_letters) else [number_to_alpha(i) for i in range(len(k))]

    # Handle disjoint components separately
    if number_of_disjoint_components(k) >= 2:
        # split, make each component canonical, sort and add together again
        old_name = k.name
        ds = disjoint_union(*sorted([canonical(c) for c in disjoint_union_decomposition(k)]))
        ds.name = old_name
        return ds

    # Identify minimal-degree nodes with minimal number of neighbours
    # TODO: one could get minimal endpoints
    minimal_nodes = min_elements_by(k.nodes, k.degree)
    minimal_nodes = min_elements_by(minimal_nodes, lambda _: neighbour_sequence(k, _))

    # Gather endpoints of minimal nodes
    starting_endpoints = [ep for node in minimal_nodes for ep in _under_endpoints_of_node(k, node)]

    minimal_diagram = None  # Store here current minimal diagram

    # Expand node enumeration from each minimal node's endpoint
    for ep_start in starting_endpoints:
        node_relabel, node_first_position = _ccw_expand_node_names(k, ep_start, letters)

        if len(node_relabel) != len(k):
            raise ValueError("Cannot put a non-connected graph into canonical form.")

        new_graph = k.copy()  # Copy method is faster than built-in deepcopy

        # Perform node relabeling
        new_graph._nodes = {
            node_relabel[node]:
                type(node_inst)(
                    [
                        type(ep)(node_relabel[ep.node], ep.position)
                        for ep in node_inst._inc
                    ]
                )
            for node, node_inst in k._nodes.items()
        }

        _canonically_permute_nodes_with_given_first_positions(new_graph, node_first_position)

        # Update minimal diagram if this one is lexicographically smaller
        if minimal_diagram is None or new_graph < minimal_diagram:
            minimal_diagram = new_graph

    # TODO: Consider adding support for in-place modification.

    return minimal_diagram


def _canonically_permute_nodes(k: PlanarDiagram):
    """Uniquely permutes the nodes in-place (smallest neighbour is first).
    :param k: planar diagram
    :return: None
    """
    if k.is_oriented():
        raise NotImplementedError()
    else:
        for node in sorted(k.nodes):  # probably sorted not needed, on second though, probably is needed

            degree = k.degree(node)
            neighbours = [ep.node for ep in k.nodes[node]]


            if isinstance(k.nodes[node], Crossing):
                index = 0 if neighbours < (neighbours[2:] + neighbours[:2]) else 2
            else:
                cyclic_permutations = [neighbours[i:] + neighbours[:i] for i in range(degree)]
                index = cyclic_permutations.index(min(cyclic_permutations))

            permute_node(k, node, {i: (i - index) % degree for i in range(degree)})

        """
        p = {0: 0, 1: 2, 2: 3, 3: 1} (or p = [0,2,3,1]),
        and if node has endpoints [a, b, c, d] (ccw) then the new endpoints will be [a, d, b, c].
        """


def _canonically_permute_nodes_with_given_first_positions(k: PlanarDiagram, node_first_position: dict):
    """Uniquely permutes the nodes in-place (smallest neighbour is first).
    :param k: planar diagram
    :return: None
    """
    for node in k.nodes:
        first_pos = node_first_position[node]

        if first_pos == 0 or (isinstance(k.nodes[node], Crossing) and first_pos == 3):
            # no need to permute node
            continue

        if isinstance(k.nodes[node], Crossing):
            permutation = [2, 3, 0, 1]  # probably faster with a list
        else:
            degree = k.degree(node)
            permutation = [(i - first_pos) % degree for i in range(degree)]

        #print(node, permutation)
        permute_node(k, node, permutation)


if __name__ == "__main__":
    pass