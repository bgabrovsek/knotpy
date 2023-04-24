"""Algorithms/functions regarding connected sums."""

__all__ = ['is_connected_sum', 'is_connected_sum_third_order']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

from itertools import combinations
from copy import deepcopy

from knotpy.classes.planarbase import PlanarBase
from knotpy.classes.planargraph import PlanarGraph
from knotpy.algorithms.components import connected_components_nodes
from knotpy.generate.simple import house_graph
def is_connected_sum(g: PlanarBase) -> bool:
    return len(connected_sum_arcs(g)) > 0  # TODO: optimize!


def connected_sum_arcs(g: PlanarGraph) -> list:
    """Returns a list of arc tuples that form a non-trivial connected sum.
    TODO: works slowly, improve using regions, not making copies.
    TODO: works only on PlanarGraph, make it work on PlanarBase (e.g. w/o creating copies)."""
    sum_arcs = []
    for arc_pair in combinations(g.arcs(), 2):
        h = deepcopy(g)
        h.remove_arcs(arc_pair)
        partitions = sorted(connected_components_nodes(h), key=lambda n: -len(n))
        partitions = [part for part in partitions if len(part) != 1]
        if len(partitions) > 1:
            sum_arcs.append(arc_pair)
    return sum_arcs

def is_connected_sum_third_order(g: PlanarBase) -> bool:
    return len(connected_sum_arcs_third_order(g)) > 0  # TODO: optimize!

def connected_sum_arcs_third_order(g: PlanarBase) -> list:
    """Returns a list of arc tuples that form a non-trivial connected sum.
       TODO: works slowly, improve using regions, not making copies.
       TODO: works only on PlanarGraph, make it work on PlanarBase (e.g. w/o creating copies)."""
    sum_arcs = []
    for arc_pair in combinations(g.arcs(), 3):
        h = deepcopy(g)
        h.remove_arcs(arc_pair)
        partitions = sorted(connected_components_nodes(h), key=lambda n: -len(n))
        partitions = [part for part in partitions if len(part) != 1]
        if len(partitions) > 1:
            sum_arcs.append(arc_pair)
    return sum_arcs


if __name__ == "__main__":
    g = house_graph()
    print(g)
    print(connected_sum_arcs_third_order(g))