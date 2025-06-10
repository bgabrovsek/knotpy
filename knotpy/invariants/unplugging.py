__all__ = ["unplugging"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


from collections import deque
from random import choice
from itertools import combinations

from knotpy.classes.planardiagram import PlanarDiagram


def _unplug(k: PlanarDiagram, node, unplug_endpoint_positions):
    """Unplug endpoints from the node.
    :param k: Planar diagram
    :param node: the node to unplug endpoints
    :param unplug_endpoint_positions: positions/indices to be unplugged
    :return:
    """

    unplug_endpoint_positions = sorted(unplug_endpoint_positions)
    while unplug_endpoint_positions:
        position = unplug_endpoint_positions.pop()  # remove (last) endpoint at index
        # create new leaf node
        new_node = name_for_new_node(k)
        k.add_node(node_for_adding=new_node, create_using=Vertex, degree=1)
        replug_endpoint(k, source_endpoint=(node, position), destination_endpoint=(new_node, 0))


def unplugging(k: PlanarDiagram):
    """Computes the "unplugging" invariant T.
    See Kauffman, L. H. (1989). Invariants of graphs in three-space. Transactions of the American Mathematical Society,
    311(2), 697-710.

    :param k: Spatial graph or related object with vertices
    :return: set of constituent knots
    """

    """ """

    stack = deque()
    stack.append(k.copy())  # put a shallow copy onto the stack
    constituent_knots = set()  # value (result) of the invariant

    while stack:
        k = stack.pop()
        vertices = [v for v in k.vertices if k.degree(v) > 2]
        if not vertices:
            constituent_knots.add(k)
            continue

        # choose a vertex and put all local replacements on the stack
        v = choice(vertices)  # choose a vertex, vertex[0] would be faster
        deg = k.degree(v)
        for p in combinations(range(deg), 2):
            # p=(i,j) are plugged nodes, i.e. keep v[i] and v[j] plugged, remove the rest of the endpoints
            unplug_k = k.copy()
            _unplug(unplug_k, node=v, unplug_endpoint_positions=set(range(deg)) - set(p))
            stack.append(unplug_k)

    return constituent_knots

