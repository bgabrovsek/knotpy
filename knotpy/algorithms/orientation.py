"""Algorithms with orientation."""
import itertools as it

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
import knotpy.algorithms.components as components

# def _oriented_from_partially_oriented(u_k: PlanarDiagram, k: PlanarDiagram, unoriented_endpoints: set) -> list:
#     """
#     Return a list of shallow copies with added oriented endpoints from unoriented_endpoints.
#     :param u_k: original unoriented diagram
#     :param k: planar partially initialized oriented diagram
#     :param unoriented_endpoints:
#     :return:
#     """
#
#     if not unoriented_endpoints:  # all endpoints are already oriented
#         return [k]
#
#     unoriented_endpoints = set(unoriented_endpoints)  # make a copy
#     #ep = unoriented_endpoints.pop()
#     ep = next(iter(unoriented_endpoints))
#     twin_ep = u_k.twin(ep)
#
#     for start_endpoint_type in (IngoingEndpoint, OutgoingEndpoint):
#         # crate new instance of k, which will have more oriented strands
#         new_k = k.copy()  # shallow copy of diagram
#
#         ep_type = start_endpoint_type
#
#         # follow the orientation
#         while ep in unoriented_endpoints:
#             unoriented_endpoints.remove(ep)
#             #new_ep = new_endpoint_type(ep.node, ep.position, **ep.attr)
#             new_k.set_endpoint(endpoint_for_setting=twin_ep,
#                                adjacent_endpoint=ep,
#                                create_using=ep_type)
#
#             twin_ep = ep  # let previous endpoint be the new endpoint for setting
#             ep = u_k.jump_over_node(ep)
#             ep_type = IngoingEndpoint if ep_type is OutgoingEndpoint else OutgoingEndpoint  # switch types
#
#             unoriented_endpoints.remove(ep)


def _orient_by_strands(k: PlanarDiagram, strands: list):
    """Orient the diagram in order given by te strands.
    :param k:
    :param strands:
    :return:
    """

    # initialize an oriented version of the diagram
    new_k = k.to_oriented_class()(**k.attr)
    for node in k.nodes:
        new_k.add_node(node_for_adding=node,
                       create_using=type(k.nodes[node]),
                       degree=k.nodes[node].degree(),
                       **k.nodes[node].attr)

    for strand in strands:
        for ep, twin_ep in zip(strand[::2], strand[1::2]):
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
    strands = components.strands(k)
    #fb_strands = (strands, [list(reversed(s)) for s in strands])  # forward/backwards strands
    fb_strands = [(s, list(reversed(s))) for s in strands]
    print(fb_strands)
    """Create a new strand sequence from the orientations [0,...,0,0], [0,...,0,1], [0,...,1,0],... where 0 donates
    a forward orientation and 1 denotes a backward orientation."""
    strand_orientations = it.product((0, 1), repeat=len(strands))
    print(list(it.product((0, 1), repeat=len(strands))))

    return [
        _orient_by_strands(k=k,
                           strands=[s[o] for s in fb_strands])
        for o in strand_orientations
    ]

def oriented(k: PlanarDiagram) -> PlanarDiagram:
    """Convert an unoriented diagram to an oriented one.
    :param k: input diagram (knot, spatial graph,...)
    :return: list of oriented diagrams of all possible orientations of k
    """
    return _orient_by_strands(k, components.strands(k))




if __name__ == "__main__":

    from knotpy.generate.example import trefoil_knot
    k = trefoil_knot()
    print(k)

    k_oriented = oriented(k)
    print(k_oriented)

    print()
    for m in all_orientations(k):
        print(m)