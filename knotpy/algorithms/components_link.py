# knotpy/algorithms/component_link.py
"""
Link components represent distinct closed loops in a link diagram.

A trefoil knot has one component, while the Hopf link has two.
"""

from __future__ import annotations

__all__ = ["number_of_link_components", "link_components_endpoints"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek"

from itertools import combinations

from knotpy.classes.planardiagram import Diagram
from knotpy.classes.node import Crossing
from knotpy.utils.disjoint_union_set import DisjointSetUnion


def number_of_link_components(k: Diagram) -> int:
    """Return the number of link components in a planar diagram.

    For example, a trefoil knot has 1 component, while the Hopf link
    has 2 components.
    """
    return len(list(link_components_endpoints(k)))


def link_components_endpoints(k: Diagram) -> list[set]:
    """Return sets of endpoints belonging to the same link component.

    Endpoints are grouped into the same component if they are connected
    through arcs or at nodes in the diagram.
    """
    dsu = DisjointSetUnion(k.endpoints)

    # endpoints from arcs are on the same component
    for ep1, ep2 in k.arcs:
        dsu[ep1] = ep2

    # endpoints from crossings and other nodes
    for node, obj in k.nodes.items():
        if isinstance(obj, Crossing):
            dsu[obj[0]] = obj[2]
            dsu[obj[1]] = obj[3]
        else:
            for ep0, ep1 in combinations(obj, r=2):
                dsu[ep0] = ep1

    return list(dsu)

def enumerate_link_components(k: Diagram, keyword="component", start=0, inplace=False) -> Diagram:
    """Mark link components in a diagram."""

    if not inplace:
        k = k.copy()

    # canonically sort components
    lce = [tuple(sorted(s)) for s in link_components_endpoints(k)]
    lce = sorted(lce, key=lambda seq: (-len(seq), seq))
    for i, component in enumerate(lce, start=start):
        for ep in component:
            k.nodes[ep].attr[keyword] = i

    return k


if __name__ == "__main__":
    pass