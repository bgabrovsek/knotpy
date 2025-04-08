"""Algorithms with orientation."""
import itertools as it

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
import knotpy.algorithms.disjoint_sum as components
from knotpy.algorithms.topology import edges
from knotpy.algorithms.canonical import canonical

def _orient_with_edges(k: PlanarDiagram, edges: list):
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


def all_orientations(k: PlanarDiagram) -> list:
    """

    :param k:
    :return:
    """
    all_edges = list(edges(k))
    orient = list(it.product((True, False), repeat=len(all_edges)))  # not needed to be a list
    #print(orient)
    return [
        _orient_with_edges(k=k, edges=edge_orientations)
        for edge_orientations in ([e if _ else e[::-1] for e, _ in zip(all_edges, o)] for o in orient)
    ]

def oriented(k: PlanarDiagram, minimal_orientation=False):
    """Orient the diagram (choose a random orientation). If minimal_orientation is True, then return the minimal diagram
    out of all possibilities of orientations (this is much slower),
    :param k:
    :param minimal_orientation: if True, computes one orientation, otherwise computes the minimal orientation
    :return:
    """
    if minimal_orientation:
        return min(canonical(o) for o in all_orientations(k))
    else:
        return _orient_with_edges(k=k, edges=edges(k))


def unoriented(k:OrientedPlanarDiagram) -> PlanarDiagram:
    o = k.copy(copy_using=PlanarDiagram)
    return o

if __name__ == "__main__":

    from knotpy.catalog.example import trefoil_knot
    k = trefoil_knot()
    print(k)

    ok = all_orientations(k)
    for o in ok:
        print("   ", o)
        uo = unoriented(o)
        print("   ", u)

    # k_oriented = oriented(k)
    # print(k_oriented)
    #
    # print()
    # for m in all_orientations(k):
    #     print(m)