"""
Decompose a knot (kinks, loops, sums, components,...) to improve drawing.
"""

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.classes.node import Node, Vertex, Crossing
from knotpy.algorithms.topology import kinks

# def decompose_kinks(k: PlanarDiagram | OrientedPlanarDiagram):
#
#     removed_kinks = []
#
#     while _kinks := kinks(k):
#         ep = next(iter(_kinks))
#         c_inst = k.nodes[ep.node]
#         removed_kinks.append((ep, c_inst))
#         v = Vertex(degree=2, _kink=True)
#         del k._nodes[ep.node]
#         # TODO: if we need a bigger space for kinks, we can insert additional bivertices
#         ep1 = c_inst[(ep.position + 1) % 4]
#         ep2 = c_inst[(ep.position + 2) % 4]
#         k.set_arc((ep1, ep2), _kink=(ep, c_inst))
#
#     return k
#
# def decompose(k: PlanarDiagram | OrientedPlanarDiagram):
#     k = k.copy()
#     result = decompose_kinks(k)
#     return result

