from random import choice
from knotpy.notation.pd import from_pd_notation
from knotpy.algorithms.sanity import sanity_check
from knotpy.classes.node import Crossing, Vertex
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.manipulation.subdivide import subdivide_endpoint_by_crossing, subdivide_endpoint
from knotpy.manipulation.remove import remove_bivalent_vertex
from knotpy.notation.native import to_knotpy_notation, from_knotpy_notation
from fractions import Fraction
from knotpy._settings import settings


def find_reidemeister_5_twists(k: PlanarDiagram):
    """ A twist is given by two adjacent endpoints form the vertex, an over (vertex, position2)
    and an under (vertex, position1), where |position1 - position2| == 1"""
    for v in k.vertices:

        deg = k.degree(v)

        if settings.r5_only_trivalent and deg != 3:
            continue

        if deg > 2:
            for pos in range(deg):
                yield k.endpoint_from_pair((v, pos)), k.endpoint_from_pair((v, (pos + 1) % deg))
                yield k.endpoint_from_pair((v, (pos + 1) % deg)), k.endpoint_from_pair((v, pos))
        elif deg == 2:
            yield k.endpoint_from_pair((v, 0)), k.endpoint_from_pair((v, 1))
            yield k.endpoint_from_pair((v, 1)), k.endpoint_from_pair((v, 0))


def choose_reidemeister_5_twist(k: PlanarDiagram, random=False):
    """
    Selects a kink to remove a crossing using the Reidemeister 5 move.
    """
    if random:
        locations = tuple(find_reidemeister_5_twists(k))
        return choice(locations) if locations else None
    else:
        return next(find_reidemeister_5_twists(k), None)



def find_reidemeister_5_untwists(k: PlanarDiagram):
    """ An untwist is given by two incident endpoints, first one is the vertex endpoint, the second one is
    the crossing endpoint."""
    for face in k.faces:
        if len(face) == 2:
            ep1, ep2 = face
            # ep1 must be a vertex and ep2 must be a crossing
            if isinstance(k.nodes[ep1.node], Crossing):
                ep2, ep1 = ep1, ep2

            if not isinstance(k.nodes[ep1.node], Vertex) or not isinstance(k.nodes[ep2.node], Crossing):
                continue

            if settings.r5_only_trivalent and k.degree(ep1.node) != 3:
                continue

            yield ep1, ep2


def choose_reidemeister_5_untwist(k: PlanarDiagram, random=False):
    """
    Selects a kink to remove a crossing using the Reidemeister 5 move.
    """
    if random:
        faces = tuple(find_reidemeister_5_untwists(k))
        return choice(faces) if faces else None
    else:
        return next(find_reidemeister_5_untwists(k), None)


def reidemeister_5_twist(k, endpoints, inplace=False):

    ep_under, ep_over = endpoints

    if not inplace:
        k = k.copy()

    # Add the "twist" crossing.
    crossing = subdivide_endpoint_by_crossing(k, ep_under, 0)

    over_twin = k.twin(ep_over)

    # Insert over-arcs (choose positions 1 and 3 or 3 and 1, depending on the CCW/CW position of the under-arc)
    if (ep_under.position + 1) % k.degree(ep_under.node) == ep_over.position:
        k.set_endpoint(over_twin, (crossing, 3))
        k.set_endpoint((crossing, 3), over_twin)
        k.set_endpoint(ep_over, (crossing, 1))
        k.set_endpoint((crossing, 1), ep_over)
        # adjust framing
        if k.is_framed():
            k.framing = k.framing - Fraction(1, 2)
    else:
        k.set_endpoint(over_twin, (crossing, 1))
        k.set_endpoint((crossing, 1), over_twin)
        k.set_endpoint(ep_over, (crossing, 3))
        k.set_endpoint((crossing, 3), ep_over)
        if k.is_framed():
            k.framing = k.framing + Fraction(1, 2)

    # switch the endpoints from the vertex
    ep_under_twin = k.twin(ep_under)
    ep_over_twin = k.twin(ep_over)
    k.set_endpoint(ep_under, ep_over_twin)
    k.set_endpoint(ep_over_twin, ep_under)
    k.set_endpoint(ep_over, ep_under_twin)
    k.set_endpoint(ep_under_twin, ep_over)




    # backtrack Reidemeister moves
    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R5"


    return k



def reidemeister_5_untwist(k:PlanarDiagram, face: tuple, inplace=False):
    """
    Reidemeister move 5 untwist operation on a given planar diagram.

    Parameters:
        k (PlanarDiagram): The PlanarDiagram object to perform the untwisting operation on.
        face (tuple): A tuple containing two endpoints representing the 2-region (face) of the twist.
        inplace (bool, optional): A boolean indicating whether the operation should
                                  modify the provided diagram directly (True) or
                                  create a modified copy and leave the original
                                  untouched (False). Default is False.

    Returns:
        PlanarDiagram: The modified planar diagram with the untwisting operation
                       applied. If inplace is True, the same object is returned;
                       otherwise, a new object with the modifications is returned.
    """

    # TODO: attributes

    #print("R5u", to_knotpy_notation(k), face, sanity_check(k))
    if not inplace:
        k = k.copy()

    v1_ep, c2_ep = face  # vertex endpoint and crossing endpoint (CCW)
    v2_ep, c1_ep = k.nodes[c2_ep.node][c2_ep.position], k.nodes[v1_ep.node][v1_ep.position]  # twins of the endpoints (CCW)

    # split incident endpoints
    y1_ep = k.endpoint_from_pair((c1_ep.node, (c1_ep.position + 2) % 4))
    y2_ep = k.endpoint_from_pair((c2_ep.node, (c2_ep.position + 2) % 4))

    b_node_1 = subdivide_endpoint(k, y1_ep)
    b_node_2 = subdivide_endpoint(k, y2_ep)

    x1_ep = k.nodes[c2_ep.node][(c2_ep.position + 2) % 4]  # this should be connected to v1_ep
    x2_ep = k.nodes[c1_ep.node][(c1_ep.position + 2) % 4]  # this should be connected to v2_ep

    k.set_endpoint(endpoint_for_setting=v1_ep, adjacent_endpoint=x1_ep)
    k.set_endpoint(endpoint_for_setting=x1_ep, adjacent_endpoint=v1_ep)
    k.set_endpoint(endpoint_for_setting=v2_ep, adjacent_endpoint=x2_ep)
    k.set_endpoint(endpoint_for_setting=x2_ep, adjacent_endpoint=v2_ep)

    remove_bivalent_vertex(k, b_node_1)
    remove_bivalent_vertex(k, b_node_2)

    # # does the untwist not form a loop?
    # if x1_ep.node != v1_ep.node:
    #     # do we have a Reidemeister 1 loop at the end of the crossing?
    #     if x1_ep.node == v2_ep.node == c1_ep.node == c2_ep.node:
    #         k.set_endpoint(endpoint_for_setting=v1_ep, adjacent_endpoint=c2_ep)
    #         k.set_endpoint(endpoint_for_setting=v2_ep, adjacent_endpoint=c1_ep)
    #         # TODO: join this with the loop condition, since it is the same operation on endpoints.
    #     else:
    #         # we have a "normal situation"
    #         k.set_endpoint(endpoint_for_setting=v1_ep, adjacent_endpoint=x1_ep)
    #         k.set_endpoint(endpoint_for_setting=x1_ep, adjacent_endpoint=v1_ep)
    #         k.set_endpoint(endpoint_for_setting=v2_ep, adjacent_endpoint=x2_ep)
    #         k.set_endpoint(endpoint_for_setting=x2_ep, adjacent_endpoint=v2_ep)
    # else:
    #     # after untwisting, we have a loop
    #     k.set_endpoint(endpoint_for_setting=v1_ep, adjacent_endpoint=v2_ep)
    #     k.set_endpoint(endpoint_for_setting=v2_ep, adjacent_endpoint=v1_ep)
    #
    k.remove_node(c2_ep.node, remove_incident_endpoints=False)

    if k.is_framed():
        k.framing = k.framing + (Fraction(-1, 2) if c2_ep.position % 2 else Fraction(1, 2))  # if we remove positive kink, the framing decreases by 1


    # backtrack Reidemeister moves
    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R5"

    #assert sanity_check(k), f"{k}"

    return k

if __name__ == "__main__":

    # test framing

    code = "a=V(c1 c0 b0) b=V(a2 b2 b1) c=X(a1 a0 c3 c2)"
    k = from_knotpy_notation(code)
    for e in find_reidemeister_5_untwists(k):
        print(e)
        k_2 = reidemeister_5_untwist(k, e, inplace=False)
        print(k_2)
        exit()

    exit()



    k = from_pd_notation("[[0,1,2],[2,3,5],[7,8,6],[0,13,12],[11,7,12,13],[1,6,8,9],[3,9,4,10],[10,4,11,5]]")

    print(k)
    for e in find_reidemeister_5_twists(k):
        print(e)
        k_2 = reidemeister_5_twist(k, e, inplace=False)
        print(k_2)
        exit()

    exit()

    sanity_check(k)
    print(k)

    while f := list(find_reidemeister_5_untwists(k)):
        print(f)
        reidemeister_5_untwist(k, f[0])
        print(k)
        sanity_check(k)

    print(k)