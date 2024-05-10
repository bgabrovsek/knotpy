
""""connected sum components" are the factors of a composite knot diagram.

 are connected components of a link, e.g. a knot has 1 link component, the Hopf link has 2 link
  components and the Borromean Link has 3 link components,

- "disjoint components": are the components that do not share a common node (crossing or vertex),

-

- "strand" a strand is either a closed component or a path between
"""

__all__ = ['number_of_link_components', "link_components"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

import warnings
from string import ascii_letters
from copy import deepcopy
from itertools import combinations, permutations

import knotpy as kp
from knotpy.algorithms.node_operations import name_for_new_node
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.utils.equivalence import EquivalenceRelation


def number_of_link_components(k: PlanarDiagram):
    """ Return the number of link components. E.g. a trefoil has 1 component, the Hopf link has 2.
    :param k: input planar diagram
    :return: number of link components
    """
    return len(link_components_endpoints(k))


def link_components_endpoints(k: PlanarDiagram):
    """ Return a list of sets of endpoints belonging to the same link component.
    :param k: planar diagram
    :return: a list of sets containing unordered endpoints belonging to the same components
    """

    er = EquivalenceRelation(k.endpoints)

    # endpoints from arcs are on the same component
    for ep1, ep2 in k.arcs:
        er[ep1] = ep2

    # endpoints from crossings/vertices
    for node in k.nodes:
        if isinstance(k.nodes[node], kp.Crossing):
            er[k.nodes[node][0]] = k.nodes[node][2]
            er[k.nodes[node][1]] = k.nodes[node][3]
        else:
            # assume that everything that is not a crossing is a connected
            for ep0, ep1 in combinations(k.nodes[node], r=2):
                er[ep0] = ep1

    return er.classes()


def link_components(k: PlanarDiagram) -> set:
    """Return
    :param k:
    :return:
    """
    pass





if __name__ == "__main__":

    from knotpy.notation.native import from_knotpy_notation
    k = from_knotpy_notation("('SpatialGraph', {'name': 't0_1(0)'}, [('Vertex', 'a', (('Endpoint', 'b', 0, {'color': 1}), ('Endpoint', 'b', 1, {})), {}), ('Vertex', 'b', (('Endpoint', 'a', 0, {'color': 1}), ('Endpoint', 'a', 1, {'attr': {}})), {}), ('Vertex', 'c', (('Endpoint', 'd', 0, {}),), {}), ('Vertex', 'd', (('Endpoint', 'c', 0, {}),), {})])")
    print(k)

    print(number_of_link_components(k))
    print(link_components_endpoints(k))