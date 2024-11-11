"""
Default (native) KnotPy notation with all diagram information stored. It is similar to EM notation.

Notation example (without attributes):

SpatialGraph
Crossing a [('b',0),('b',2),('b',1),('v',0)]
Crossing b [('a',0),('a',2),('a',1),('u',0)]
Vertex u [('b',3)]
Vertex v [('a',3)]

Notation example (with attributes):

SpatialGraph {'name':'x1','color':'red'}
Crossing a [('b',0,{'color':'Orange'}),('b',2,{'color':'Orange'}),('b',1,{'color':'Orange'}),('v',0,{'color':'Orange'})] {'color':'blue'}
Crossing b [('a',0,{'color':'Orange'}),('a',2,{'color':'Orange'}),('a',1,{'color':'Orange'}),('u',0,{'color':'Orange'})] {'color':'blue'}
Vertex u [('b',3,{'color':'Orange'})] {}
Vertex v [('a',3,{'color':'Orange'})] {}

See "Ewing, B. & Millett, K. C. in The mathematical heritage of CF Gauss 225–266 (World Scientific, 1991)".
"""

__all__ = ["to_knotpy_notation", "from_knotpy_notation"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek"

from typing import Tuple, Any, List, Generator

import knotpy as kp
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.notation.pd import from_pd_notation
from knotpy.classes import Vertex, Crossing


def _node_knot_notation(k: PlanarDiagram, node):
    """Return string representing a node.
    :param k: knot diagram
    :param node: which node to convert
    :param attributes: add additional data (attributes)
    :return: str
    """

    # node type and name
    node_type = type(k.nodes[node]).__name__
    node_name = node
    node_adj = tuple((type(ep).__name__,ep.node, ep.position, ep.attr) for ep in k.nodes[node])
    node_attr = k.nodes[node].attr
    return node_type, node_name, node_adj, node_attr


def to_knotpy_notation(k):
    """Returns KnotPy notation of planar diagram (native python structures list, tuples, dicts,... encoding the whole
    diagram)
    Example:"SpatialGraph {'name':'x1','color':'red'}
    Vertex a [('b',0,{'color':'Orange'})] {}
    Vertex b [('a',0,{'color':'Orange'})] {}"
    """

    knot_type = type(k).__name__
    knot_nodes = [_node_knot_notation(k, node) for node in k.nodes]
    knot_attr = k.attr
    return str((knot_type, knot_attr, knot_nodes, ))


def from_knotpy_notation(text) -> PlanarDiagram:
    data = eval(text)
    knot_type, knot_attr, knot_nodes = data

    k = eval("kp." + knot_type)()  # create the diagram
    k.attr.update(knot_attr)  # update the attributes TODO: we can add attributes oin the construction

    for node_tuple in knot_nodes:
        node_type, node_name, node_adj, node_attr = node_tuple
        node_degree = len(node_adj)
        k.add_node(node_for_adding=node_name,
                   create_using=eval("kp." + node_type),
                   degree=node_degree)
        k.nodes[node_name].attr.update(node_attr)  # TODO: we can add attributes in the constructor
        # print("nodear", node_adj)
        # for xx in node_adj:
        #     print("   ",xx)

        for i, (ep_type, ep_node, ep_pos, ep_attr) in enumerate(node_adj):
            k.nodes[node_name][i] = eval("kp." + ep_type)(ep_node, ep_pos, **ep_attr)

    return k



if __name__ == "__main__":
    g = from_pd_notation("V[0,1,2],V[3,4,1],X[2,4,5,6],X[7,8,9,5],X[8,10,6,9],X[3,0,10,7]")#, create_using=SpatialGraph)
    g.name = "my graph"
    print(g)

    g.nodes["a"].attr["color"] = 3
    g.nodes["a"][0].attr["color"] = 8
    print(g)
    print("\n")
    n = to_knotpy_notation(g)
    print(n)
    print("\n")
    #
    h = from_knotpy_notation(n)
    print(h)
    print("\n")

    s = "('PlanarDiagram', {'name': '+t3_1#-3_1(1).2'}, [('Vertex', 'a', (('IngoingEndpoint', 'c', 2, {}), ('OutgoingEndpoint', 'b', 1, {'color': 1}), ('OutgoingEndpoint', 'd', 0, {})), {}), ('Vertex', 'b', (('IngoingEndpoint', 'd', 1, {}), ('IngoingEndpoint', 'a', 1, {'color': 1}), ('OutgoingEndpoint', 'g', 0, {})), {}), ('Crossing', 'c', (('IngoingEndpoint', 'f', 3, {}), ('IngoingEndpoint', 'f', 2, {}), ('OutgoingEndpoint', 'a', 0, {}), ('OutgoingEndpoint', 'e', 0, {})), {}), ('Crossing', 'd', (('IngoingEndpoint', 'a', 2, {}), ('OutgoingEndpoint', 'b', 0, {}), ('OutgoingEndpoint', 'g', 3, {}), ('IngoingEndpoint', 'h', 2, {})), {}), ('Crossing', 'e', (('IngoingEndpoint', 'c', 3, {}), ('IngoingEndpoint', 'h', 1, {}), ('OutgoingEndpoint', 'f', 1, {}), ('OutgoingEndpoint', 'f', 0, {})), {}), ('Crossing', 'f', (('IngoingEndpoint', 'e', 3, {}), ('IngoingEndpoint', 'e', 2, {}), ('OutgoingEndpoint', 'c', 1, {}), ('OutgoingEndpoint', 'c', 0, {})), {}), ('Crossing', 'g', (('IngoingEndpoint', 'b', 2, {}), ('OutgoingEndpoint', 'h', 0, {}), ('OutgoingEndpoint', 'h', 3, {}), ('IngoingEndpoint', 'd', 2, {})), {}), ('Crossing', 'h', (('IngoingEndpoint', 'g', 1, {}), ('OutgoingEndpoint', 'e', 1, {}), ('OutgoingEndpoint', 'd', 3, {}), ('IngoingEndpoint', 'g', 2, {})), {})])"
    k = from_knotpy_notation(s)
    print(k)