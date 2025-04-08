from pathlib import Path
import itertools as it

from knotpy.notation.native import from_knotpy_notation
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.endpoint import IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.node.vertex import Vertex
from knotpy.algorithms.topology import edges
from knotpy.algorithms.orientation import all_orientations

import knotpy.algorithms.orientation as orientation
from knotpy.notation.native import to_knotpy_notation
from knotpy import export_pdf, draw
#from knotpy.classes.node.bond import Bond
from knotpy.reidemeister.phantom import (insert_phantom_node,
                                         insert_phantom_nodes_on_internal_arcs)
from knotpy.reidemeister.elementary import copy_and_move_arc
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from copy import deepcopy
from knotpy.algorithms.cut_set import cut_vertices

data_folder = Path("data")
txt_input_file = data_folder / 'bonded-simple-oriented.txt'
txt_output_file_bonded = data_folder / 'bonded-structure.txt'
txt_output_file_bonded_eva = data_folder / 'bonded-structure_eva.txt'


image_folder = Path("images")
pdf_output_file_bonded_nodes = image_folder / 'bonded-structure.pdf'


def to_bonded_structure(k: PlanarDiagram):
    other = {IngoingEndpoint: OutgoingEndpoint, OutgoingEndpoint: IngoingEndpoint}

    print()
    print(k)

    k = k.copy()
    bond = [arc for arc in k.arcs if len(arc) == 2 and all("color" in ep.attr and ep.attr["color"] == 1 for ep in arc)][0]
    ep1, ep2 = bond
    print("ep", ep1, ep2)
    if k.degree(ep1.node) != 3 or k.degree(ep2.node) != 3:
        raise ValueError("Cannot convert non-3-valent nodes to bonded structures.")

    # add phantom nodes
    #phantom_nodes = insert_phantom_nodes_on_internal_arcs(k, [ep1.node, ep2.node], exclude_arcs={bond})
    k.add_node(node_for_adding="bond", create_using=Bond, degree=4)
    #print("bond", bond, ep1, ep2)
    copy_and_move_arc(k, [
        {k.endpoint_from_pair((ep1.node, (ep1.position + 1) % 3)): ("bond", 0)},
        {k.endpoint_from_pair((ep1.node, (ep1.position - 1) % 3)): ("bond", 1)},
        {k.endpoint_from_pair((ep2.node, (ep2.position + 1) % 3)): ("bond", 2)},
        {k.endpoint_from_pair((ep2.node, (ep2.position - 1) % 3)): ("bond", 3)},
    ])

    print(k)
    k.remove_nodes_from(nodes_for_removal=[ep1.node, ep2.node], remove_incident_endpoints=False)
    print(k)
    return k


print("outputting")

# load the simple bonded knots
with open(txt_input_file, 'r', newline='') as file:
    lines = file.readlines()
simple = [from_knotpy_notation(s) for s in lines]

bonded_structure = []
for k in simple:
    bonded_structure.append(to_bonded_structure(k))


print("Bonded structures reduced from", len(bonded_structure), end=" ")
bonded_structure_no_cut = [k for k in bonded_structure if len(cut_vertices(k)) == 0]
print("to", len(bonded_structure_no_cut), "by removing cut vertices")

with open(txt_output_file_bonded, 'w') as f:
    for k in bonded_structure:
        #print(">> ", k)
        f.write(to_knotpy_notation(k) + "\n")

# To "Eva's" format
for k in bonded_structure:
    print(k.is_oriented())


#export_pdf(bonded_structure_no_cut, pdf_output_file_bonded_nodes, draw_circles=False, with_labels=False, with_title=True, author="Boštjan Gabrovšek")

