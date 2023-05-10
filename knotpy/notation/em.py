"""
Modified EM (Ewing-Millett) notation.

The basic notation is given as a dictionary of nodes, where each node's value is a list of tuples in CCW order
representing the adjacent node and the position of the arc in the adjacent node.
This notation should be used as a default notation, since it is the most similar to the native class structure.

Example:

The graph

  C
 / \
A---B---D

is encoded by the notation {A:[(B,0),(C,1)], B:[(A,0),(D,0),(C,0)], C:[(B,2),(A,1)], D:[(B,1)]},
and the condensed notation is assuming lower case letters for nodes: "b0c1,a0d0c0,b2a1,b1".
In the case of knotted graphs, ...
In the case of oriented knots, ...


See "Ewing, B. & Millett, K. C. in The mathematical heritage of CF Gauss 225–266 (World Scientific, 1991)".
"""
import string
import re

import knotpy as kp
from knotpy.classes.old.planargraph import PlanarGraph
from knotpy.generate.simple import empty_knot


__all__ = ['to_em_notation', 'from_em_notation', 'to_condensed_em_notation', 'from_condensed_em_notation']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


def to_em_notation(g) -> dict:
    """Returns EM code of planar diagram."""
    return {node: [adj_ep for adj_ep in g.adj[node]] for node in g.nodes}


def from_em_notation(data, create_using=None):
    """
    :param data: dictionary of lists of tuples or a string that evaluates to this
    :param create_using: Graph Instance, Constructor or None
    :return: PlanarGraph object
    """

    if isinstance(data, str):
        pd = eval(data)

    g = PlanarGraph()
    for node in data:
        g.add_node(node, len(data[node]))
        for pos, adj_endpoint in enumerate(data[node]):
            g._set_endpoint((node, pos), adj_endpoint)
    return g


def to_condensed_em_notation(g, separator=",") -> str:
    """Return EM code of g as a condensed string.
    :raises ValueError: if the number of nodes is more than 52.
    :raises TypeError: if the nodes are mixed by type (e.g. int and string).
    """

    if len(g.nodes) > len(string.ascii_letters):
        raise ValueError(
            f"condensed EM notation is not defined for diagrams with more than {len(string.ascii_letters)} nodes")

    try:
        nodes = sorted(g.nodes)
    except TypeError as e:
        raise TypeError(f"Condensed EM notation requires the nodes to be of same type (int, str,...), ") from e

    node_dict = dict(zip(nodes, string.ascii_letters[:len(g.nodes)]))

    return separator.join(
        ["".join(node_dict[u] + str(u_pos) for u, u_pos in g.adj[v]) for v in nodes]
    )


def from_condensed_em_notation(data: str, separator=",", create_using=None):
    """Convert a condensed EM string to a planar diagram."""

    data = (" " if separator == " " else "").join(data.split())  # clean up string
    g = empty_graph(create_using=create_using)
    data = data.split(separator)
    for s, node in zip(data, string.ascii_letters[:len(data)]):
        adj_nodes = re.findall(r"[a-zA-Z]", s)
        adj_positions = re.findall(r"\d+", s)

        g.add_node(node_for_adding=node, degree=len(adj_nodes))

        for i, (v, v_pos) in enumerate(zip(adj_nodes, adj_positions)):
            g._set_endpoint((node, i), (v, v_pos))

    return g


if __name__ == '__main__':
    h = kp.generate.simple.house_graph()
    print("EM:", to_em_notation(h))
    print(from_em_notation({0: [(1, 0)], 1: [(0, 1)]}))
    print("Condensed EM:", to_condensed_em_notation(h))
    print(from_condensed_em_notation("b0e1,a0c0d0,b1d1,b2c1e0,d2a1"))
