"""Algorithms with orientation."""
import itertools as it

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
import knotpy.algorithms.components as components
import knotpy.algorithms.structure as structure


def _orient_with_edges(k: PlanarDiagram, edges: list):
    """Orient the diagram so that edges are positively ordered, i.e. the orientations follows the endpoints
    edge[0], edge[1], ..."""

    new_k = k.to_oriented_class()(**k.attr)
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
    edges = list(structure.edges(k))
    orient = list(it.product((True, False), repeat=len(edges)))  # not needed to be a list
    print(orient)
    return [
        _orient_with_edges(k=k, edges=edge_orientations)
        for edge_orientations in ([e if _ else e[::-1] for e, _ in zip(edges, o)] for o in orient)
    ]



if __name__ == "__main__":

    from knotpy.generate.example import trefoil_knot
    k = trefoil_knot()
    print(k)

    k_oriented = oriented(k)
    print(k_oriented)

    print()
    for m in all_orientations(k):
        print(m)