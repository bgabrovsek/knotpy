from copy import deepcopy
from queue import Queue
import string

from knotpy.algorithms.node_operations import degree_sequence
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node import Crossing
from knotpy.algorithms.node_operations import permute_node
from knotpy.sanity import sanity_check
__all__ = ['canonical']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


_CHECK_SANITY = True
# canonical methods

def canonical(k: PlanarDiagram, use_letters_for_nodes=True):

    if _CHECK_SANITY:
        k_copy = k.copy()

    if k.is_oriented():
        raise NotImplementedError
    else:

        canonical_k = _canonical_unoriented(k, use_letters_for_nodes)

        if _CHECK_SANITY:
            try:
                sanity_check(canonical_k)
            except:
                print("Not sane after canonical.")
                print("In: ", k_copy)
                print("Out:", canonical_k)
                sanity_check(canonical_k)


        return _canonical_unoriented(k, use_letters_for_nodes)

def _canonical_unoriented(k: PlanarDiagram, use_letters_for_nodes=True):
    """Puts the diagram k in a unique canonical form. The diagram start with an endpoint on of a minimal degree vertex,
    it continues to an adjacent endpoints and distributes the ordering from there on using breadth first search using
    CCW order of visited nodes. At the moment, it is only implemented if the graph is connected.
    TODO: In case of degree 2 vertices the canonical form might not be unique.
    :param k: the input (knot/graph/...) diagram
    :param use_letters_for_nodes: if True, the diagram's nodes will be a, b, c,... otherwise they will be 0, 1, 2, ...
    :return: None
    """

    # should diagram

    _debug = False

    #print(" canonical", k)

    # node names
    letters = (string.ascii_lowercase + string.ascii_uppercase) if use_letters_for_nodes else list(range(len(k)))

    if len(k) == 0:  # empty knot
        return k.copy()

    minimal_degree = min(degree_sequence(k))
    nodes_with_minimal_degree = [node for node in k.nodes if k.degree(node) == minimal_degree]
    # TODO: optimize by viewing also 2nd degree (number of neighbour's neighbours)
    # TODO: also take minimal Node type
    # TODO: multiple disjoint components

    if _debug: print("minimal degree nodes", nodes_with_minimal_degree)

    # endpoints of minimal nodes
    starting_endpoints = list()
    for node in nodes_with_minimal_degree:
        if type(k.nodes[node]) is Crossing:
            starting_endpoints.append((node, 0))
            starting_endpoints.append((node, 2))
        else:
            starting_endpoints.extend([node, pos] for pos in range(minimal_degree))

    #starting_endpoints = [ep for node in nodes_with_minimal_degree for ep in k.endpoints[node]]
    #        [(v, pos) for v in nodes_with_minimal_degree for pos in range(minimal_degree)]
    if _debug: print("starting endpoints", starting_endpoints)

    minimal_graph = None

    for ep_start in starting_endpoints:
        if _debug: print("starting with", ep_start)

        node_relabel = dict()  # also holds as a "visited node" set
        endpoint_queue = Queue()
        endpoint_queue.put(ep_start)

        while not endpoint_queue.empty():
            v, pos = ep = endpoint_queue.get()
            if _debug: print("popping endpoint", ep)
            if v not in node_relabel:  # new node visited
                node_relabel[v] = letters[len(node_relabel)]  # rename the node to next available integer
                v_deg = k.degree(v)
                # put all adjacent endpoints in queue in ccw order
                for relative_pos in range(1, v_deg):
                    endpoint_queue.put((v, (pos + relative_pos) % v_deg))

            # go to the adjacent endpoint and add it to the queue
            adj_v, adj_pos = k.nodes[v][pos]
            if adj_v not in node_relabel:
                endpoint_queue.put((adj_v, adj_pos))

        if _debug: print(node_relabel)
        if len(node_relabel) != len(k):
            raise ValueError("Cannot put a non-connected graph into canonical form.")

        new_graph = deepcopy(k)
        if _debug: print("before relabeling", new_graph)
        new_graph.relabel_nodes(node_relabel)
        if _debug: print("after relabeling", new_graph)
        _canonically_permute_nodes(new_graph)
        if _debug: print("after permuting", new_graph)

        # if g.number_of_arcs == 5: print("> ", new_graph)

        #### ####
        #for v in range(k.number_of_nodes):  # new_graph._adj:
        #    new_graph._canonically_rotate_node(v)

        # if g.number_of_arcs == 5: print("> ")

        #print("   candidate:", new_graph)

        if minimal_graph is None or new_graph < minimal_graph:
            minimal_graph = new_graph
            #print("   minimal  :", new_graph)

    #
    # if in_place:
    #     # copy all data from minimal_graph
    #     g._node_attr = minimal_graph._node_attr
    #     g._endpoint_attr = minimal_graph._endpoint_attr
    #     g._adj = minimal_graph._adj
    # else:

    return minimal_graph


def _canonically_permute_nodes(k : PlanarDiagram):
    """
    Uniquely permutes the nodes in-place (smallest neighbour is first)
    :param k: planar diagram
    :return: None
    """
    if k.is_oriented():
        raise NotImplementedError()
    else:
        for node in sorted(k.nodes):  # probably sorted not needed, on second though, probably is needed

            # if len(k.nodes[node]) <= 1:  # no need to permute leafs
            #     continue

            degree = len(k.nodes[node])
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
