from queue import Queue
from copy import deepcopy

from knotpy.algorithms.node_algorithms import degree_sequence

__all__ = ['canonical']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


# canonical methods

def canonical(g, in_place=False):
    """Puts itself in unique canonical form.
    The diagram start with an endpoint on of a minimal degree vertex, it continues to an adjacent endpoints and
    distributes the ordering from there on using breadth first search using CCW order of visited nodes.
    At the moment, it is only implemented if the graph is connected.
    TODO: In case of degree 2 vertices the canonical form might not be unique.
    :param in_place:
    :return: None
    """

    _debug = False

    minimal_degree = min(degree_sequence(g))
    nodes_with_minimal_degree = [v for v in g._node_attr if g.degree(v) == minimal_degree]
    # TO-DO: optimize by viewing also 2nd degree (number of neighbour's neighbours)

    # endpoints of minimal nodes
    starting_endpoints = [(v, pos) for v in nodes_with_minimal_degree for pos in range(minimal_degree)]

    minimal_graph = None

    if _debug: print("starting endpoints", starting_endpoints)

    for ep_start in starting_endpoints:
        if _debug: print("starting with", ep_start)

        node_reindex_dict = dict()  # also holds as a "visited node" set
        endpoint_queue = Queue()
        endpoint_queue.put(ep_start)

        while not endpoint_queue.empty():
            v, pos = ep = endpoint_queue.get()
            if _debug: print("popping endpoint", ep)
            if v not in node_reindex_dict:  # new node visited
                node_reindex_dict[v] = len(node_reindex_dict)  # rename the node to next available integer
                v_deg = g.degree(v)
                # put all adjacent endpoints in queue in ccw order
                for relative_pos in range(1, v_deg):
                    endpoint_queue.put((v, (pos + relative_pos) % v_deg))

            # go to the adjacent endpoint and add it to the queue
            adj_v, adj_pos = adj_ep = g._adj[v][pos]
            if adj_v not in node_reindex_dict:
                endpoint_queue.put(adj_ep)

        if _debug: print(node_reindex_dict)
        if len(node_reindex_dict) != len(g):
            raise ValueError("Cannot put da non-connected graph into canonical form.")

        new_graph = deepcopy(g)
        new_graph.rename_nodes(node_reindex_dict)

        # if g.number_of_arcs == 5: print("> ", new_graph)

        for v in range(g.number_of_nodes):  # new_graph._adj:

            new_graph._canonically_rotate_node(v)

        # if g.number_of_arcs == 5: print("> ")

        if minimal_graph is None or new_graph < minimal_graph:
            minimal_graph = new_graph

    if in_place:
        # copy all data from minimal_graph
        g._node_attr = minimal_graph._node_attr
        g._endpoint_attr = minimal_graph._endpoint_attr
        g._adj = minimal_graph._adj
    else:
        return minimal_graph


if __name__ == "__main__":
    pass