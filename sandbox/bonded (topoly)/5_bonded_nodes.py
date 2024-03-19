from pathlib import Path
import itertools as it

from knotpy.notation.native import from_knotpy_notation
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.endpoint import IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.node.vertex import Vertex
from knotpy.algorithms.structure import edges
from knotpy.algorithms.orientation import all_orientations
import knotpy.algorithms.structure as structure
import knotpy.algorithms.orientation as orientation
from knotpy.notation.native import to_knotpy_notation
from knotpy import export_pdf, draw
from knotpy.classes.node.bond import Bond
from knotpy.manipulation.phantom import insert_phantom_bivalent_vertex_on_arc

data_folder = Path("data")
txt_input_file = data_folder / 'bonded-simple-oriented.txt'
txt_output_file_bonded = data_folder / 'bonded-structure.txt'


image_folder = Path("images")
pdf_output_file_oriented = image_folder / 'bonded-nodes.pdf'


def to_bonded_structure(k: PlanarDiagram):
    other = {IngoingEndpoint: OutgoingEndpoint, OutgoingEndpoint: IngoingEndpoint}

    print()
    print(k)
    bond = [arc for arc in k.arcs if len(arc) == 2 and all("color" in ep.attr and ep.attr["color"] == 1 for ep in arc)][0]
    ep1, ep2 = bond
    if k.degree(ep1.node) != 3 or k.degree(ep2.node) != 3:
        raise ValueError("Cannot convert non-3-valent nodes to bonded structures.")

    # add phantom nodes if the bond's arcs go again to the bond
    adjacent_arcs = (set(k.arcs[ep1.node]) | set(k.arcs[ep1.node])) - {bond}
    adjacent_self_arcs = {a for a in adjacent_arcs if all(isinstance(k.nodes[ep.node], Vertex) for ep in a)}
    if adjacent_self_arcs:
        for arc in adjacent_self_arcs:
            insert_phantom_bivalent_vertex_on_arc(k, arc)
        bond = [arc for arc in k.arcs if len(arc) == 2 and all("color" in ep.attr and ep.attr["color"] == 1 for ep in arc)][0]
        ep1, ep2 = bond


    print("BOND", bond, "arcs", adjacent_self_arcs)

    print(ep1, ":", k.nodes[ep1.node][ep1.position], "=", k.endpoints[(ep1.node, ep1.position)])


    k.add_node(node_for_adding="bond", create_using=Bond, degree=4)

    # set endpoints of the bond

    k.set_endpoint(endpoint_for_setting=("bond", 0),
                   adjacent_endpoint=k.nodes[ep1.node][(ep1.position+1) % 3],
                   create_using=k.nodes[ep1.node][(ep1.position+1) % 3],
                   **k.get_endpoint_from_pair((ep1.node, (ep1.position+1) % 3)).attr
                   )
    k.set_endpoint(endpoint_for_setting=("bond", 1),
                   adjacent_endpoint=k.nodes[ep1.node][(ep1.position-1) % 3],
                   create_using=k.nodes[ep1.node][(ep1.position-1) % 3],
                   **k.get_endpoint_from_pair((ep1.node, (ep1.position - 1) % 3)).attr
                   )
    k.set_endpoint(endpoint_for_setting=("bond", 2),
                   adjacent_endpoint=k.nodes[ep2.node][(ep2.position+1) % 3],
                   create_using=k.nodes[ep2.node][(ep2.position+1) % 3],
                   **k.get_endpoint_from_pair((ep2.node, (ep2.position + 1) % 3)).attr
                   )
    k.set_endpoint(endpoint_for_setting=("bond", 3),
                   adjacent_endpoint=k.nodes[ep2.node][(ep2.position-1) % 3],
                   create_using=k.nodes[ep2.node][(ep2.position-1) % 3],
                   **k.get_endpoint_from_pair((ep2.node, (ep2.position - 1) % 3)).attr
                   )

    # set endpoints to the bond's adjacent nodes

    k.set_endpoint(endpoint_for_setting=(ep1.node, (ep1.position+1) % 3),
                   adjacent_endpoint=k.nodes["bond"][0],
                   create_using=k.nodes["bond"][0],
                   **k.get_endpoint_from_pair((ep1.node, (ep1.position+1) % 3)).attr
                   )

    print(k)
    pass

# load the simple bonded knots
with open(txt_input_file, 'r', newline='') as file:
    lines = file.readlines()
simple = [from_knotpy_notation(s) for s in lines]

bonded_structure = []
for k in simple[:10]:

    bonded_structure.append(to_bonded_structure(k))




# oriented_simple = []
#
# for k in simple:
#     kor = all_orientations_except_bond(k)
#     for i in range(len(kor)):
#         kor[i].name += f".{i}"
#     oriented_simple += kor
#
# with open(txt_output_file_orinted_simple, 'w') as f:
#     for k in oriented_simple:
#         f.write(to_knotpy_notation(k) + "\n")
#
# print("Wrote", len(oriented_simple), "PD codes to", txt_output_file_orinted_simple)
#
# export_pdf(oriented_simple, pdf_output_file_oriented, draw_circles=False, with_labels=False, with_title=True, author="Boštjan Gabrovšek")