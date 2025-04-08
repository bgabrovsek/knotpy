"""
Link components represent distinct closed loops in a link diagram.
For example, a trefoil knot has one component, while the Hopf link has two.
"""

__all__ = ['number_of_link_components', "link_components"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

from itertools import combinations

import knotpy as kp
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.utils.disjoint_union_set import DisjointSetUnion


def number_of_link_components(k: PlanarDiagram):
    """Return the number of link components in a planar diagram.

    This function determines the number of connected components (link
    components) in a given planar diagram representation of a link.
    For example, a trefoil knot has 1 component, while the Hopf link
    consists of 2 components.

    Args:
        k: The input planar diagram representing the link, from which
           the number of components will be derived.

    Returns:
        int: The number of link components present in the given planar
        diagram.
    """

    return len(list(link_components_endpoints(k)))


def link_components_endpoints(k: PlanarDiagram):
    """
    Return a list of sets of endpoints belonging to the same link component.

    This function takes a planar diagram representing a knot or link and determines the groups of endpoints that belong
    to the same connected link components. Each endpoint is grouped based on equivalence relations derived from the arcs
    and node connections in the planar diagram.

    Args:
        k (PlanarDiagram): The planar diagram object that contains arcs, nodes, and endpoints associated with a
            knot or link structure.

    Returns:
        list[set]: A list of sets where each set contains unordered endpoints that are determined to belong to the
            same link component.
    """

    dsu = DisjointSetUnion(k.endpoints)

    # endpoints from arcs are on the same component
    for ep1, ep2 in k.arcs:
        dsu[ep1] = ep2

    # endpoints from crossings/vertices
    for node in k.nodes:
        if isinstance(k.nodes[node], kp.Crossing):
            dsu[k.nodes[node][0]] = k.nodes[node][2]
            dsu[k.nodes[node][1]] = k.nodes[node][3]
        else:
            # assume that everything that is not a crossing is a connected
            for ep0, ep1 in combinations(k.nodes[node], r=2):
                dsu[ep0] = ep1

    return list(dsu)


def link_components(k: PlanarDiagram) -> set:
    """
    Determine the distinct link components in a planar diagram.

    Link components are individual, closed, connected parts of a link structure,
    such as in knot theory. This function identifies which parts of the diagram
    belong to the same connected component.

    :param k: An input planar diagram representing a link.
    :return: A set representing the link components.
    """
    raise NotImplementedError()


if __name__ == "__main__":

    from knotpy.notation.native import from_knotpy_notation
    k = from_knotpy_notation("('SpatialGraph', {'name': 't0_1(0)'}, [('Vertex', 'a', (('Endpoint', 'b', 0, {'color': 1}), ('Endpoint', 'b', 1, {})), {}), ('Vertex', 'b', (('Endpoint', 'a', 0, {'color': 1}), ('Endpoint', 'a', 1, {'attr': {}})), {}), ('Vertex', 'c', (('Endpoint', 'd', 0, {}),), {}), ('Vertex', 'd', (('Endpoint', 'c', 0, {}),), {})])")
    print(k)

    print(number_of_link_components(k))
    print(link_components_endpoints(k))