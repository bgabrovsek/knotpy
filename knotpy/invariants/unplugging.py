__all__ = ["unplugging"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


from collections import deque
from random import choice
from itertools import combinations

from knotpy.classes.spatialgraph import SpatialGraph
from knotpy.algorithms.node_operations import unplug

def unplugging(k: SpatialGraph):
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
            unplug(unplug_k, node=v, unplug_endpoint_positions=set(range(deg)) - set(p))
            stack.append(unplug_k)

    return constituent_knots

