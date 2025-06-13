from random import choice
from itertools import product
import warnings

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.classes.node import Crossing
from knotpy.algorithms.cut_set import arc_cut_sets
from knotpy.manipulation.rewire import swap_endpoints
from knotpy.manipulation.symmetry import flip
from knotpy._settings import settings

def _path_within_crossings(k: PlanarDiagram, nodes, endpoint):
    """Follow the strand of the endpoint until it reaches a node not in the given list of nodes."""

    # print("---")
    # print(nodes)
    # print(endpoint)

    if endpoint.node not in nodes:
        raise ValueError("Endpoint not in nodes")
        #return []

    path = [endpoint]
    while True:
        jump = k.twin((path[-1].node, (path[-1].position + 2) % 4))
        if jump.node not in nodes:
            break
        path.append(jump)
    return [ep.node for ep in path]


def _is_integer_tangle_cut(k: PlanarDiagram | OrientedPlanarDiagram, partition: set, endpoints):
    """Check if the tangle cut by the partition is integer."""
    return _path_within_crossings(k, partition, endpoints[0]) == _path_within_crossings(k, partition, endpoints[1])


def find_flype(k: PlanarDiagram | OrientedPlanarDiagram):
    """
    Find all flype positions. A flype is given by a list of four endpoints, where the endpoints form an arc-cut set.
    The first two endpoints are in the same crossing and the obtained tangle by cutting the arcs of the endpoints is
    not integer.

    A flype is a local move on a knotted diagram that transforms a tangle positioned near a twist region
    (crossing or half-twist) by rotating part of the diagram 180° around an axis perpendicular to the projection plane.

    Args:
        k: A planar or oriented planar diagram representing a knot diagram
            where potential flype positions need to be located.

    Returns:
        list: A list of positions where flype operations can be applied,
        represented in the context of the provided diagram.
    """

    if "FLYPE" not in settings.allowed_moves:
        return

    for arcs, partition_, ccw_endpoints_ in arc_cut_sets(k, order=4, minimum_partition_nodes=2, return_partition=True, return_ccw_ordered_endpoints=True):


        # loop through both possibilities
        for index, rotation in product(range(2), range(4)):
            partition = partition_[index]

            # are we allowed to flype crossings only?
            if settings.flype_crossings_only and not all(isinstance(k.nodes[node], Crossing) for node in partition):
                continue

            ccw_endpoints = ccw_endpoints_[index][rotation:] + ccw_endpoints_[index][:rotation]
            ccw_endpoints_c = ccw_endpoints_[1 - index][rotation:] + ccw_endpoints_[1 - index][:rotation]

            # is there a "flype" crossing?
            if ccw_endpoints[0].node != ccw_endpoints[1].node or not isinstance(k.nodes[ccw_endpoints[0].node], Crossing):
                continue

            # is any side an integer tangle? TODO: this is checked too many times
            if _is_integer_tangle_cut(k, partition_[index], ccw_endpoints) or _is_integer_tangle_cut(k, partition_[1 - index], ccw_endpoints_c):
                continue

            yield partition, ccw_endpoints


def choose_flype(k, random=False):
    """ Return one flype."""

    if "FLYPE" not in settings.allowed_moves:
        return None

    if random:
        locations = tuple(find_flype(k))
        return choice(locations) if locations else None
    else:
        return next(find_flype(k), None)  # select 1st item


def flype(k:PlanarDiagram | OrientedPlanarDiagram, partition_endpoints_pair: tuple, inplace=False):

    if "FLYPE" not in settings.allowed_moves:
        warnings.warn("A flype move is being performed, although it is disabled in the global KnotPy settings.")

    partition, endpoints_quadruple = partition_endpoints_pair


    if endpoints_quadruple[0].node != endpoints_quadruple[1].node:
        raise ValueError("Endpoints should share the first crossings")

    if not inplace:
        k = k.copy()


    # The crossing to flip to the "other side".
    #crossing = endpoints_quadruple[0]

    # Flip the crossing to the "other side" of the tangle.
    ep0, ep1, ep2, ep3 = endpoints_quadruple
    twin0, twin1, twin2, twin3 = k.twin(ep0), k.twin(ep1), k.twin(ep2), k.twin(ep3)
    next0 = k.nodes[ep0.node][(ep0.position + 2) % 4]
    next1 = k.nodes[ep1.node][(ep1.position + 2) % 4]
    twin_next0 = k.twin(next0)  # other side of the crossing
    twin_next1 = k.twin(next1)  # other side of the crossing

    # remove crossing
    k.set_arc((twin0, next0))
    k.set_arc((twin1, next1))

    # set new crossing
    k.set_arc((twin_next0, twin3))
    k.set_arc((twin_next1, twin2))
    k.set_arc((ep1, ep2))
    k.set_arc((ep0, ep3))

    # flip the part of the diagram
    k = flip(k, partition, inplace=True)

    return k

if __name__ == "__main__":

    import knotpy as kp

    k = PlanarDiagram()
    k.add_crossings_from("xbcde")
    k.add_vertices_from("ijkl")
    k.set_arcs_from("i0x1,j0x2,k0d3,l0e3,x0b3,x3e2,b0e1,b1c0,b2c3,c1d1,c2d0,d2e0")

    kf = kp.flip(k, inplace=False)
    km = kp.mirror(kf, inplace=False)
    kfm = kp.flip(km, inplace=False)

    print("         ", k)
    print("flip     ", kf)
    print("     mirr", km)
    print("flip mirr", kfm)

    ck = kp.canonical(k)
    ckf = kp.canonical(kf)
    ckm = kp.canonical(km)
    ckfm = kp.canonical(kfm)
    print("         ", ck)
    print("flip     ", ckf)
    print("     mirr", ckm)
    print("flip mirr", ckfm)
