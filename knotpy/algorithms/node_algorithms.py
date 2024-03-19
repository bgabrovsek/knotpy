"""Simple algorithms/functions regarding nodes."""

import string
from collections import defaultdict

# from knotpy.generate.simple import house_graph

__all__ = ['degree_sequence', 'name_for_new_node', "add_node_to", "permute_node"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

def relabel_nodes(G, mapping):
    """Relabels nodes in place."""


def add_node_to(k, node_for_adding, node_type, degree=None):
    """
    :param k: planar diagram instance for adding a node
    :param node_for_adding:
    :param node_type: type of node "X", "V", ...
    :param degree: degree of the node (optional)
    :return:
    """
    if node_type == "X" or node_type == "x":
        if (degree or 4) != 4:
            raise ValueError(f"Cannot add a crossing with degree {degree}")
        k.add_crossing(node_for_adding)
    else:
        raise ValueError(f"Unknown node type {repr(node_type)}")


def degree_sequence(g):
    return tuple(sorted([len(g.nodes[node]) for node in g.nodes]))


# dictionary that stores True for all letters a-zA-Y and False for other hashable objects
_is_letter_but_not_Z = defaultdict(bool, {letter: True for letter in string.ascii_letters[:-1]})
_next_letter = defaultdict(bool, {string.ascii_letters[i]: string.ascii_letters[i + 1] for i in range(51)})


def name_for_new_node(k, default="a"):
    """Returns a natural next available node name for the graph/knot K. If all nodes are letters a-zA-Y, it returns the
    next available letter, otherwise returns the next available integer, or default if the knot is empty."""

    if not k.number_of_nodes:
        return default

    if all(_is_letter_but_not_Z[node] for node in k.nodes):
        return _next_letter[max(k.nodes, key=str.swapcase)]

    return max((node for node in k.nodes if isinstance(node, int)), default=0)


def name_for_next_node_generator(k, count=None, default="a"):
    """Returns a natural next available node name for the graph/knot K. If all nodes are letters a-zA-Y, it returns the
    next available letter, otherwise returns the next available integer, or default if the knot is empty."""

    if not count:
        return

    new_node = name_for_new_node(k)

    for _ in range(count-1):
        yield new_node
        if isinstance(new_node, int):
            new_node += 1
        else:
            new_node = _next_letter[new_node] if _is_letter_but_not_Z[new_node] else 0

def permute_node(k, node, p):
    """Permute the endpoints of the node of knot k. For example, if p = {0: 0, 1: 2, 2: 3, 3: 1} (or p = [0,2,2,1]),
    and if node has endpoints [a, b, c, d] (ccw) then the new endpoints will be [a, d, b, c].
    :param k: knot diagram
    :param node: node of which we permute its endpoints
    :param p: permutation given as a dict or list/tuple
    :return: None
    TODO: are there problems regarding endpoint attributes?
    TODO: check if it works for loops (probably does not)
    """


    # convert list/tuple permutation to dict
    if isinstance(p, list) or isinstance(p, tuple):
        p = dict(enumerate(p))

    #invp = inverse_dict(p)

    old_node_data = list(k.nodes[node])  # save old node ccw sequence since it can override
    for pos, ep in enumerate(old_node_data):
        #print("old_node_data[pos]", old_node_data[pos], type(old_node_data[pos]))
        # set endpoint from adjacent crossing
        #print(type(ep))
        k.set_endpoint(
            endpoint_for_setting=ep,
            adjacent_endpoint=(node, p[pos]),
            create_using=old_node_data[pos],  # copies the type and "old" attributes
            )
        # set endpoint from crossing
        k.nodes[node][p[pos]] = ep



if __name__ == "__main__":
    g = house_graph()
    print(degree_sequence(g))
