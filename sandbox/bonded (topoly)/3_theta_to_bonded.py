import csv
from pathlib import Path
from itertools import chain, combinations
from copy import deepcopy

import knotpy as kp
from knotpy import SpatialGraph, from_pd_notation, to_pd_notation
from knotpy.algorithms.structure import edges
from knotpy import export_pdf, draw
from knotpy.notation.native import to_knotpy_notation

_DEBUG = True
data_folder = Path("data")
csv_input_file = data_folder / 'theta-pd-ccw.csv'
csv_output_file_bonded = data_folder / 'bonded-pd.csv'
csv_output_file_simple = data_folder / 'bonded-simple.txt'

image_folder = Path("images")
pdf_output_file_bonded = image_folder / 'bonded.pdf'
pdf_output_file_simple = image_folder / 'bonded-simple.pdf'

def theta_to_bonded_knot(rk: SpatialGraph, only_simple=True) -> list:
    """
    :param k: theta curve
    :param only_simple: choose only the ones with a bond that contains no crossing
    :return: list of 0, 1, 2, or 3 bonded knots
    """
    result = []
    for i in range(3):
        new_k = deepcopy(k)
        edge = list(edges(new_k)[i])
        if edge[0].node == edge[-1].node:  # skip bonded knots if the bond forms a loop, since it is not bonded then
            continue
        #print(k.name, edge)
        #if len(edge) ==
        for ep in edge:
            ep["color"] = 1
        new_k.name = new_k.name + f"({i})"
        result.append(new_k)
    return result


def is_simple_bonded(k) -> bool:
    """Returns bonded knots that are simple, i.e. the bonded component contains no crossings
    :param k: Planar diagram
    :return:
    """
    bonds = edges(k, color=1)
    return len(bonds) == 1 and len(bonds[0]) == 2


with open(csv_input_file, 'r', newline='') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)
    data = list(csv_reader)
    if _DEBUG:
        print("Loaded", len(data), "thetas.")

theta_curves = [from_pd_notation(s, create_using=SpatialGraph, name=name) for name, s in data]

bonded_knots = []  # theta curves with one strand colored
for k in theta_curves:
    bonded_knots += theta_to_bonded_knot(k)

export_pdf(bonded_knots, pdf_output_file_bonded, draw_circles=False, with_labels=False, with_title=True, author="Boštjan Gabrovšek")


simple_bonded_knots = [k for k in bonded_knots if is_simple_bonded(k)]

with open(csv_output_file_simple, 'w') as f:
    for k in simple_bonded_knots:
        f.write(to_knotpy_notation(k) + "\n")

print("Wrote", len(simple_bonded_knots), "PD codes to", csv_output_file_simple)

export_pdf(simple_bonded_knots, pdf_output_file_simple, draw_circles=False, with_labels=False, with_title=True, author="Boštjan Gabrovšek")
