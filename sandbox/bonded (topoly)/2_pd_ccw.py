"""
Load PD codes from a CSV file, fixes CCW orientation of arcs, and exports them to a new csv file.
"""

import csv
from itertools import chain, combinations
from copy import deepcopy
from pathlib import Path


import knotpy as kp
from knotpy import SpatialGraph, from_pd_notation, to_pd_notation
from knotpy import export_pdf, draw
from knotpy import bridges, loops

_DEBUG = False
data_folder = Path("data")
image_folder = Path("images")

csv_input_file = data_folder / 'theta-pd-non-ccw.csv'
csv_output_file = data_folder / 'theta-pd-ccw.csv'

pdf_output_file = image_folder / 'thetas.pdf'

# load the pd codes
with open(csv_input_file, 'r', newline='') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)
    data = list(csv_reader)
    if _DEBUG:
        print("Loaded", len(data), "thetas.")


# convert pd codes to ccw ones
thetas_ccw = list()

for count, (name, pd) in enumerate(data):
    k = from_pd_notation(text=pd, node_type=str, create_using=SpatialGraph)
    k.name = name
    if _DEBUG:
        print("Converted", pd, "to", k)

    if kp.check_faces_sanity(k) or len(k) <= 2:
        thetas_ccw.append(k)

    else:
        #print("Non-realizable:", k)

        # loop through all subsets of degree 3 nodes of length > 0
        nodes3 = k.nodes(degree=3)
        has_sane_candidate = False
        L = None

        for nodes in chain(*(combinations(nodes3, i) for i in range(1, len(nodes3) + 1))):
            L = deepcopy(k)
            for node in nodes:
                kp.permute_node(L, node, list(range(len(L.nodes[node]) - 1, -1, -1)))
            if kp.check_faces_sanity(k):
                has_sane_candidate = True
                break

        if has_sane_candidate:
            print(name + " converted to \"" + str(L) + "\"")
            thetas_ccw.append(L)
        else:
            print("Unable to convert" + name + "(\"" + to_pd_notation(L) + "\")")

# write to file
with open(csv_output_file, 'w') as csvfile:
    csv_writer = csv.writer(csvfile)
    # Write the data
    csv_writer.writerow(("Name", "PD"))
    for k in thetas_ccw:
        csv_writer.writerow((k.name, to_pd_notation(k)))
    print("Wrote", len(thetas_ccw), "PD codes to", csv_output_file)


# plot them to pdf
export_pdf(thetas_ccw, pdf_output_file, draw_circles=False, with_labels=True, with_title=True, author="Boštjan Gabrovšek")
