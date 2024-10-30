"""" Creates a dual graph of a planar diagram
"""

__all__ = ['dual_planar_diagram']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

import warnings
from string import ascii_letters
from copy import deepcopy
from itertools import combinations, permutations

import knotpy as kp
from knotpy.algorithms.node_operations import name_for_new_node
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.utils.equivalence import EquivalenceRelation
from knotpy.classes.node import Vertex

def dual_planar_diagram(k: PlanarDiagram) -> PlanarDiagram:
    dual = PlanarDiagram()
    faces = list(k.faces)
    ep_face_dict = {ep: face for face in faces for ep in face}
    dual.add_nodes_from(faces, create_using=Vertex)
    for face in faces:
        for pos, ep in enumerate(face):
            twin = k.twin(ep)
            adjacent_dual_node = ep_face_dict[twin]
            adjacent_dual_position = ep_face_dict[twin].index(twin)
            dual.set_endpoint(endpoint_for_setting=(face, pos), adjacent_endpoint=(adjacent_dual_node, adjacent_dual_position))

    if k.name is not None:
        dual.name = k.name + "^*"
    return dual


if __name__ == "__main__":
    from knotpy.notation.pd import from_pd_notation
    k = from_pd_notation("X[1,5,2,4],X[3,9,4,8],X[5,1,6,10],X[7,3,8,2],X[9,7,10,6]]")  # 5_2 knot
    print(k)
    dual = dual_planar_diagram(k)