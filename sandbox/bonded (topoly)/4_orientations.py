from pathlib import Path
import itertools as it

from knotpy.notation.native import from_knotpy_notation
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.structure import edges
from knotpy.algorithms.orientation import all_orientations
import knotpy.algorithms.structure as structure
import knotpy.algorithms.orientation as orientation
from knotpy.notation.native import to_knotpy_notation
from knotpy import export_pdf, draw

data_folder = Path("data")
txt_input_file = data_folder / 'bonded-simple.txt'
txt_output_file_orinted_simple = data_folder / 'bonded-simple-oriented.txt'


image_folder = Path("images")
pdf_output_file_oriented = image_folder / 'bonded-simple-oriented.pdf'


def all_orientations_except_bond(k: PlanarDiagram) -> list:
    edges = list(e for e in structure.edges(k) if all("color" not in ep.attr for ep in e))
    colored_edge = structure.edges(k, color=1)
    orient = list(it.product((True, False), repeat=len(edges)))  # not needed to be a list

    knot_candidates = [
        orientation._orient_with_edges(k=k, edges=edge_orientations + colored_edge)
        for edge_orientations in ([e if _ else e[::-1] for e, _ in zip(edges, o)] for o in orient)
    ]
    good_knots = []
    for k in knot_candidates:
        good = True
        for v in k.vertices:
            uncolored_endpoints = [ep for ep in k.endpoints[v] if "color" not in ep]
            colored_endpoints = [ep for ep in k.endpoints[v] if "color" in ep]
            if len(uncolored_endpoints) == 2 and type(uncolored_endpoints[0]) == type(uncolored_endpoints[1]):
                good = False
            if len(colored_endpoints) == 2 and type(colored_endpoints[0]) == type(colored_endpoints[1]):
                good = False

        if good:
            good_knots.append(k)
    return good_knots
# load the simple bonded knots
with open(txt_input_file, 'r', newline='') as file:
    lines = file.readlines()
simple = [from_knotpy_notation(s) for s in lines]

print("Simple:")
for k in simple[:4]:
    print(k)


oriented_simple = []

for k in simple:
    kor = all_orientations_except_bond(k)
    for i in range(len(kor)):
        kor[i].name += f".{i}"
    oriented_simple += kor

with open(txt_output_file_orinted_simple, 'w') as f:
    for k in oriented_simple:
        f.write(to_knotpy_notation(k) + "\n")

print("Wrote", len(oriented_simple), "PD codes to", txt_output_file_orinted_simple)

export_pdf(oriented_simple, pdf_output_file_oriented, draw_circles=False, with_labels=False, with_title=True, author="Boštjan Gabrovšek")