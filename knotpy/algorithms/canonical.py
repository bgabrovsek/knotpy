from copy import deepcopy
from queue import Queue

from knotpy.algorithms.node_algorithms import degree_sequence
from knotpy.classes.planardiagram import PlanarDiagram

__all__ = ['canonical']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


# canonical methods

def canonical(k: PlanarDiagram):
    """Puts the diagram k in a unique canonical form. The diagram start with an endpoint on of a minimal degree vertex,
    it continues to an adjacent endpoints and distributes the ordering from there on using breadth first search using
    CCW order of visited nodes. At the moment, it is only implemented if the graph is connected.
    TODO: In case of degree 2 vertices the canonical form might not be unique.
    :param k: the input (knot/graph/...) diagram
    :return: None
    """

    _debug = True

    minimal_degree = min(degree_sequence(k))
    nodes_with_minimal_degree = [node for node in k.nodes if k.degree(node) == minimal_degree]
    # TODO: optimize by viewing also 2nd degree (number of neighbour's neighbours)
    # TODO: also take minimal Node type

    if _debug: print("minimal degree nodes", nodes_with_minimal_degree)

    # endpoints of minimal nodes
    starting_endpoints = [(node, pos) for node in nodes_with_minimal_degree for pos in range(minimal_degree)]

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
                node_relabel[v] = len(node_relabel)  # rename the node to next available integer
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
            raise ValueError("Cannot put da non-connected graph into canonical form.")

        new_graph = deepcopy(k)
        new_graph.relabel_nodes(node_relabel)

        # if g.number_of_arcs == 5: print("> ", new_graph)

        #### ####
        #for v in range(k.number_of_nodes):  # new_graph._adj:
        #    new_graph._canonically_rotate_node(v)

        # if g.number_of_arcs == 5: print("> ")

        if minimal_graph is None or new_graph < minimal_graph:
            minimal_graph = new_graph
    #
    # if in_place:
    #     # copy all data from minimal_graph
    #     g._node_attr = minimal_graph._node_attr
    #     g._endpoint_attr = minimal_graph._endpoint_attr
    #     g._adj = minimal_graph._adj
    # else:
    return minimal_graph


if __name__ == "__main__":
    from knotpy import from_plantri_notation
    k = from_plantri_notation("edcb,cdea,dba,ebca,bda")
    print(k)
    c = canonical(k)
    print(c)
    pass
