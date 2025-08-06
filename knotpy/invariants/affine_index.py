__all__ = ['affine_index_polynomial']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'


from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.orientation import orient
from knotpy.classes.node import Crossing
from knotpy.classes.endpoint import OutgoingEndpoint, IngoingEndpoint
from knotpy.invariants._symbols import _t



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
    polynomial = sum(k.nodes[crossing].sign() * (_t ** weights[crossing] - 1) for crossing in k.crossings)
    return polynomial









