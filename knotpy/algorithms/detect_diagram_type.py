"""
Determine what knotted structure a planar diagram is.
"""
__all__ = ['is_knot'
           ]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

from collections import defaultdict

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node import Crossing, Vertex
from  knotpy.algorithms.orientation import oriented

def _split_nodes_by_type(k: PlanarDiagram) -> dict:
    """Return a dict, where keys are node types (Crossing, Vertex,...) and values are sets of nodes belonging to that
    class.
    :param k:
    :return:
    """
    result = defaultdict(set)
    for node in k.nodes:
        result[type(k.nodes[node])].add(node)
    return result



def is_knot(k: PlanarDiagram) -> bool:
    return all(type(node) is Crossing for node in k.nodes)


def is_knotoid(k: PlanarDiagram) -> bool:
    """Is the diagram amulti knotoid?"""
    node_sets= _split_nodes_by_type(k)
    return (len(node_sets[Crossing]) == len(k) - 2 and
            len(node_sets[Vertex]) == 2 and
            all(k.degree(node) == 1 for node in node_sets[Vertex]))


def is_linkoid(k: PlanarDiagram) -> bool:
    """Is the diagram a multi-linkoid?"""
    node_sets= _split_nodes_by_type(k)
    return (len(node_sets[Crossing]) + len(node_sets[Vertex]) == len(k) and
            len(node_sets[Vertex]) % 2 == 0 and
            all(k.degree(node) == 1 for node in node_sets[Vertex]))

def is_empty_diagram(k: PlanarDiagram) -> bool:
    return len(k) == 0


if __name__ == '__main__':
    from knotpy import from_pd_notation
    k = from_pd_notation("X[0,1,2,3],X[1,4,5,6],X[3,2,7,8],X[6,4,8,7],V[0],V[5]")
    print(k)
    print(_split_nodes_by_type(k))
    ok = oriented(k)
    print(ok)
    ok = oriented(k, minimal_orientation=True)
    print(ok)