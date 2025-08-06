"""
Algorithms that deal with orientation.
"""

__all__ = ["orient", "unorient", "all_orientations"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

import itertools as it

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.algorithms.topology import edges

def orient_edges(k: PlanarDiagram, edges: list):
    """Orient the diagram so that edges are positively ordered, i.e. the orientations follows the endpoints
    edge[0], edge[1], ..."""

    new_k = OrientedPlanarDiagram(**k.attr)
    for node in k.nodes:
        new_k.add_node(node_for_adding=node,
                       create_using=type(k.nodes[node]),
                       degree=k.nodes[node].degree(),
                       **k.nodes[node].attr)

    for edge in edges:
        for ep, twin_ep in zip(edge[::2], edge[1::2]):
            new_k.set_endpoint(endpoint_for_setting=ep,
                               adjacent_endpoint=twin_ep,
                               create_using=OutgoingEndpoint,
                               **k.nodes[ep.node].attr
                               )
            new_k.set_endpoint(endpoint_for_setting=twin_ep,
                               adjacent_endpoint=ep,
                               create_using=IngoingEndpoint,
                               **k.nodes[ep.node].attr
                               )
    return new_k


def all_orientations(k: PlanarDiagram, up_to_reversal=False) -> list[OrientedPlanarDiagram]:
    """
    Return all possible orientations of a given unoriented PlanarDiagram. If the diagram is invertible, both orientations are still returned.

    Parameters:
        k (PlanarDiagram): The PlanarDiagram for which all possible orientations are generated.

    Returns:
        list: A list of oriented planar diagrams.
    """

    if k.is_oriented():
        k = unorient(k)

    base_name = str(k.name).strip().strip('+-') if k.name is not None else None

    all_edges = sorted(edges(k))
    if up_to_reversal:
        orient = [(True,) + rest for rest in it.product((True, False), repeat=len(all_edges) - 1)]  # not needed to be a list
    else:
        orient = list(it.product((True, False), repeat=len(all_edges)))  # not needed to be a list

    result = [
        orient_edges(k=k, edges=edge_orientations)
        for edge_orientations in ([e if _ else e[::-1] for e, _ in zip(all_edges, o)] for o in orient)
    ]

    # add signs to the end of the string
    if k.name is not None:
        for k, o in zip(result, orient):
            if k.name:
                k.name = str(k.name) + "".join(["+" if _ else "-" for _ in o])

    return result

def orient(k: PlanarDiagram):
    """
    Orient the given unoriented planar. The returned orientation is random.
    Parameters:
        k (PlanarDiagram)
            The planar diagram to be oriented.

    Returns:
        PlanarDiagram
            The oriented planar diagram based on the specified configuration.
    """

    return orient_edges(k=k, edges=edges(k))


def unorient(k:OrientedPlanarDiagram | PlanarDiagram) -> PlanarDiagram:
    return k.copy(copy_using=PlanarDiagram)


if __name__ == "__main__":
    pass