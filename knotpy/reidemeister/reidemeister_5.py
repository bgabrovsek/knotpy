from knotpy.notation.pd import from_pd_notation
from knotpy.algorithms.sanity import sanity_check
from knotpy.classes.node import Crossing, Vertex
from knotpy.classes.planardiagram import PlanarDiagram

def find_reidemeister_5_twists(k: PlanarDiagram):
    """ A twist is given by two adjacent endpoints form the vertex, e.g. (vertex, position), (vertex, position + 1)"""
    for v in k.vertices:
        if (deg := k.degree(v)) >= 2:
            for pos in range(deg):
                yield k.endpoint_from_pair((v, pos)), k.endpoint_from_pair((v, (pos + 1) % deg))

def find_reidemeister_5_untwists(k: PlanarDiagram):
    """ An untwist is given by two incident endpoints, first one is the vertex endpoint, the second one is
    the crossing endpoint."""
    for v in k.vertices:
        for ep in k.vertices[v]:
            if isinstance(k.nodes[ep.node], Crossing):
                ep_from_adj_crossing = k.crossings[ep.node][(ep.position - 1) % k.degree(ep.node)]
                if ep_from_adj_crossing.node == v:
                    yield ep_from_adj_crossing, ep  # first node, then crossing


def reidemeister_5_twist(k, endpoints):
    NotImplementedError()

def reidemeister_5_untwist(k:PlanarDiagram, face: tuple):

    v1_ep, c2_ep = face  # vertex endpoint and crossing endpoint
    v2_ep, c1_ep = k.nodes[c2_ep.node][c2_ep.position], k.nodes[v1_ep.node][v1_ep.position]

    x1_ep = k.nodes[c2_ep.node][(c2_ep.position + 2) % 4]  # this should be connected to v1_ep
    x2_ep = k.nodes[c1_ep.node][(c1_ep.position + 2) % 4]  # this should be connected to v2_ep


    # does the twist form a loop?
    if x1_ep.node != v1_ep.node:
        k.set_endpoint(endpoint_for_setting=v1_ep, adjacent_endpoint=x1_ep)
        k.set_endpoint(endpoint_for_setting=x1_ep, adjacent_endpoint=v1_ep)
        k.set_endpoint(endpoint_for_setting=v2_ep, adjacent_endpoint=x2_ep)
        k.set_endpoint(endpoint_for_setting=x2_ep, adjacent_endpoint=v2_ep)
    else:
        k.set_endpoint(endpoint_for_setting=v1_ep, adjacent_endpoint=v2_ep)
        k.set_endpoint(endpoint_for_setting=v2_ep, adjacent_endpoint=v1_ep)

    k.remove_node(c2_ep.node, remove_incident_endpoints=False)

if __name__ == "__main__":

    k = from_pd_notation("[[0,1,2],[2,3,5],[7,8,6],[0,13,12],[11,7,12,13],[1,6,8,9],[3,9,4,10],[10,4,11,5]]")
    sanity_check(k)
    print(k)

    while f := list(find_reidemeister_5_untwists(k)):
        reidemeister_5_untwist(k, f[0])
        sanity_check(k)

    print(k)