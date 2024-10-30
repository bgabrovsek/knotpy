from copy import deepcopy
from queue import Queue
from typing import Union
import string
import multiprocessing
from knotpy.algorithms.node_operations import degree_sequence
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.endpoint import Endpoint
from knotpy.classes.node import Crossing, Vertex
from knotpy.algorithms.node_operations import permute_node
from knotpy.algorithms.disjoint_sum import number_of_disjoint_components, to_disjoint_sum
from knotpy.classes.composite import DisjointSum, ConnectedSum
from knotpy.utils.dict_utils import inverse_multi_dict
from knotpy.sanity import sanity_check
__all__ = ['canonical', "canonical_parallel"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


_CHECK_SANITY = True
# canonical methods


_ascii_letters = string.ascii_lowercase + string.ascii_uppercase


def canonical(k: Union[PlanarDiagram, DisjointSum, ConnectedSum]):

    if isinstance(k, PlanarDiagram):
        if k.is_oriented():
            raise NotImplementedError("Canonical form of oriented diagrams not supported")
        else:
            return _canonical_unoriented(k)
    elif isinstance(k, DisjointSum) or isinstance(k, ConnectedSum):
        return _canonical_composite(k)
    else:
        raise TypeError(f"Cannot put a {type(k)} instance into canonical from.")


def _node_neighbours_sequence(k:PlanarDiagram, node):
    """Counts number of new neighbours from node at distance 1, distance 2, ..."""
    used_nodes = {node}
    levels = [{node}]
    while levels[-1]:
        levels.append({ep.node for prev_node in levels[-1] for ep in k.nodes[prev_node] if ep.node not in used_nodes})
        used_nodes |= levels[-1]
    return tuple(len(w) for w in levels[1:-1])  # first is just the node, last is empy


def _minimal_degree_nodes(k:PlanarDiagram):
    """Return all the nodes that have the minimal degree of the diagram."""
    minimal_degree = min(k.degree(node) for node in k.nodes)
    return [node for node in k.nodes if k.degree(node) == minimal_degree]


def _min_value_keys(d:dict):
    """return keys that have minimal values."""
    min_value = min(d.values())
    return [key for key in d if d[key] == min_value]


def _under_endpoints_of_node(k, node):
    """Return a tuple of endpoints that are under endpoints in case of crossings and all endpoints in case of vertices"""
    return [(node, 0), (node, 2)] if isinstance(k.nodes[node], Crossing) else [(node, pos) for pos in range(k.degree(node))]


def _ccw_expand_node_names(k:PlanarDiagram, endpoint, node_names):
    """Starting from the node in the endpoint in the direction of the endpoints, start labelling nodes in ccw direction.
    Labels with integers.
    :param: labels: list of (ordered) labels"""
    node_relabel = dict()  # also holds as a "visited node" set
    endpoint_queue = Queue()
    endpoint_queue.put(endpoint)

    while not endpoint_queue.empty():
        v, pos = endpoint_queue.get()

        if v not in node_relabel:  # new node visited
            node_relabel[v] = node_names[len(node_relabel)]  # rename the node to next available integer
            v_deg = k.degree(v)
            # put all adjacent endpoints in queue in ccw order
            for relative_pos in range(1, v_deg):
                endpoint_queue.put((v, (pos + relative_pos) % v_deg))

        # go to the adjacent endpoint and add it to the queue
        adj_v, adj_pos = k.nodes[v][pos]
        if adj_v not in node_relabel:
            endpoint_queue.put((adj_v, adj_pos))
    return node_relabel


def _canonical_unoriented(k: PlanarDiagram):
    """Puts the diagram k in a unique canonical form. The diagram start with an endpoint on of a minimal degree vertex,
    it continues to an adjacent endpoints and distributes the ordering from there on using breadth first search using
    CCW order of visited nodes. At the moment, it is only implemented if the graph is connected.
    :param k: the input (knot/graph/...) diagram
    :param use_letters_for_nodes: if True, the diagram's nodes will be a, b, c,... otherwise they will be 0, 1, 2, ...
    :return: None
    """
    # TODO: In case of degree 2 vertices the canonical form might not be unique.

    if len(k) == 0:
        return k.copy()

    # node names
    letters = _ascii_letters if len(k) <= len(_ascii_letters) else list(range(len(k)))

    # disjoint sum
    if number_of_disjoint_components(k) >= 2:
        ds = to_disjoint_sum(k)
        # remove _r3 tags from the components that do not have _r3 point
        for _ in ds:
            if "_r3" in _.attr:
                if not _.attr["_r3"].issubset(_.nodes):
                    del _.attr["_r3"]

        return canonical(ds)

    # start expanding enumeration of nodes with nodes that are "minimal"
    minimal_nodes = _minimal_degree_nodes(k)
    minimal_nodes = _min_value_keys({node: _node_neighbours_sequence(k, node) for node in minimal_nodes})

    # create a list of endpoints of minimal nodes
    starting_endpoints = [ep for node in minimal_nodes for ep in _under_endpoints_of_node(k, node)]

    minimal_diagram = None

    # start expanding enumeration from endpoints for each "minimal" node (under) endpoint
    for ep_start in starting_endpoints:
        node_relabel = _ccw_expand_node_names(k, ep_start, letters)

        #print("node relabel", k, node_relabel)
        if len(node_relabel) != len(k):
            raise ValueError("Cannot put a non-connected graph into canonical form.")

        #print("k", k)
        new_graph = k.copy()  # copy method is faster than built-in deepcopy
        #print("ng", new_graph)
        if "_r3" in k.attr:
            new_graph.attr["_r3"] = {node_relabel[node] for node in k.attr["_r3"]}

        # do the relabelling
        #new_graph.relabel_nodes(node_relabel)
        #print("relabel", node_relabel)

        new_graph._nodes = {node_relabel[node]:
                                Crossing([Endpoint(node_relabel[ep.node], ep.position) for ep in node_inst._inc]) if type(node_inst) is Crossing
                                else Vertex([Endpoint(node_relabel[node_inst._inc[position].node], node_inst._inc[position].position) for position in range(len(node_inst))], degree=len(node_inst))
                            for node, node_inst in k._nodes.items()}

        #print("ng", new_graph)
        _canonically_permute_nodes(new_graph)


        if minimal_diagram is None or new_graph < minimal_diagram:
            minimal_diagram = new_graph

    # TODO: should we add inplace support?

    return minimal_diagram


def _canonical_composite(k: Union[DisjointSum, ConnectedSum]):
    """Return the canonical form of a disjoint sum or connected sum."""
    return type(k)(*sorted(canonical(_) for _ in k), **k.attr)


def _canonically_permute_nodes(k: PlanarDiagram):
    """
    Uniquely permutes the nodes in-place (smallest neighbour is first)
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

            #print("node", node, {i: (i - index) % degree for i in range(degree)})
            permute_node(k, node, {i: (i - index) % degree for i in range(degree)})

        """
        p = {0: 0, 1: 2, 2: 3, 3: 1} (or p = [0,2,3,1]),
        and if node has endpoints [a, b, c, d] (ccw) then the new endpoints will be [a, d, b, c].
        """


def canonical_parallel(diagrams):
    with multiprocessing.Pool() as pool:
        result = pool.map(canonical, diagrams)
    return result

if __name__ == "__main__":
    degree = 4
    neighbours = ["b", "a", "a", "c"]
    cyclic_permutations = [neighbours[i:] + neighbours[:i] for i in range(degree)]
    index = cyclic_permutations.index(min(cyclic_permutations))
    print(neighbours, min(cyclic_permutations), index, {i: (i - index) % degree for i in range(degree)})

    exit()
    from knotpy import from_plantri_notation
    k = from_plantri_notation("edcb,cdea,dba,ebca,bda")
    print(k)
    c = canonical_unoriented(k)
    print(c)
    pass
