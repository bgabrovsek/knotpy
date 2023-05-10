"""Simple algorithms/functions regarding nodes."""

import string

#from knotpy.generate.simple import house_graph


__all__ = ['degree_sequence', 'name_for_new_node', "add_node_to"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


def add_node_to(k, node, node_type, degree=None):
    """
    :param k: planar diagram instance for adding a node
    :param node_type: type of node "X", "V", ...
    :param degree: degree of the node (optional)
    :return:
    """
    if node_type == "X" or node_type == "x":
        if (degree or 4) != 4:
            raise ValueError(f"Cannot add a crossing with degree {degree}")
        k.add_crossing(node)
    else:
        raise ValueError(f"Unknown node type {repr(node_type)}")

def degree_sequence(g):
    return sorted(g.degree().values())


def name_for_new_node(K):
    """Returns a natural next available node name for the graph/knot K."""
    # all ints or mixed int/str
    if any(isinstance(key, int) for key in K.nodes):
        return max(node for node in g.nodes if isinstance(node, int)) + 1

    # only single letters
    if all(isinstance(key, str) and len(key) == 1 and ('a' <= key <= 'z' or 'A' <= key < 'Z') for key in K.nodes):
        node = max(K.nodes, key=str.swapcase)
        return chr(ord(node) + 1) if node != "z" else 'A'

    return 0



if __name__ == "__main__":
    g = house_graph()
    print(degree_sequence(g))

