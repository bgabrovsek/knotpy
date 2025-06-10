from sympy import symbols, Symbol
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.orientation import orient
from knotpy.classes.node import Crossing
from knotpy.classes.endpoint import OutgoingEndpoint, IngoingEndpoint
from knotpy.reidemeister.reidemeister import make_all_reidemeister_moves
from knotpy.reidemeister.reidemeister_1 import reidemeister_1_add_kink

_T = symbols("t")

def affine_index_polynomial(k: PlanarDiagram):
    """
    The affine index polynomial of a knotoid.
    """

    k = k if k.is_oriented() else orient(k)

    # positive crossing: w = a - b - 1, negative crossing: w = b - a + 1
    weights = {crossing: -k.nodes[crossing].sign() for crossing in k.crossings}  # start with - 1 and + 1
    #print(weights)
    modified = {crossing: 1 for crossing in k.crossings}
    ep = [ep for ep in k.endpoints if k.degree(ep.node) == 1 and type(ep) is OutgoingEndpoint][0]  # start with outgoing terminal
    ep = k.twin(ep)  # jump over arc (ingoing endpoint)
    label = 0
    while type(k.nodes[ep.node]) is Crossing:
        ccw_ep = k.endpoint_from_pair((ep.node, (ep.position - 1) % 4))
        weights[ep.node] += label if (k.nodes[ep.node].sign() > 0) ^ (type(ccw_ep) is IngoingEndpoint) else -label
        ep = k.endpoint_from_pair((ep.node, (ep.position + 2) % 4))  # jump over crossing to the incident endpoint
        ep = k.twin(ep)  # jump over arc (outgoing endpoint)
        label += 1 if type(ccw_ep) is IngoingEndpoint else -1

    #print(weights)
    polynomial = sum(k.nodes[crossing].sign() * (_T ** weights[crossing] - 1) for crossing in k.crossings)
    return polynomial



if __name__ == '__main__':
    import knotpy as kp

    k = kp.from_pd_notation("X[0,4,1,5],X[5,1,6,2],X[2,6,3,7],X[8,4,7,3],V[0],V[8]")
    #k = kp.from_pd_notation("X[3,2,4,1],X[2,5,3,4],V[1],V[5]")

    print(k)

    for o in kp.all_orientations(k):
        print(o)
        print(affine_index_polynomial(o))

    print("---")
    for k_r in make_all_reidemeister_moves(k, [reidemeister_1_add_kink], depth=1):
        #print(k_r)
        for o in kp.all_orientations(k_r):
            #print(o)
            # print(kp.to_pd_notation(o))
            print(affine_index_polynomial(o))





