"""" Create a dual graph of a planar diagram
"""

__all__ = ['dual_planar_diagram']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

from itertools import combinations

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node import Vertex

# TODO: write test

def dual_planar_diagram(k: PlanarDiagram) -> PlanarDiagram:
    """
    Generates the dual of a given planar diagram by transforming its structure such
    that nodes of the dual correspond to faces in the original diagram, and edges
    represent adjacency relationships between those faces.

    The function takes a `PlanarDiagram` object, constructs its dual by iterating
    through its faces and endpoints, and establishes the adjacency relationships
    in the dual. The dual diagram's name is updated to reflect its dual nature
    if the original diagram has a name.

    Args:
        k (PlanarDiagram): The planar diagram whose dual is to be generated.

    Returns:
        PlanarDiagram: The dual planar diagram of the given input diagram.
    """
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

def arc_face_graph(k:PlanarDiagram):
    """Generate an arc-face graph for a given planar diagram.

    An arc-face graph is a graph where the nodes represent arcs in the planar diagram, and
    two arcs are adjacent if they lie on the same face in the planar diagram.

    Args:
        k (PlanarDiagram): The planar diagram object containing arcs and faces, where arcs define
            the edges and faces represent connected regions of the planar diagram.

    Returns:
        dict: A dictionary where keys are arcs from the planar diagram, and values are sets of arcs that
        share a face with the key arc.
    """
    faces = list(k.faces)

    arcs_near_arcs = {arc: set() for arc in k.arcs}  # keys are arcs, values are arcs that share a face with the key arc
    for face in faces:
        for ep1, ep2 in combinations(face, 2):
            arc1, arc2 = k.arcs[ep1], k.arcs[ep2]
            arcs_near_arcs[arc1].add(arc2)
            arcs_near_arcs[arc2].add(arc1)
    return arcs_near_arcs

if __name__ == "__main__":
    pass