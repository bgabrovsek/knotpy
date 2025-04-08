from pathlib import Path
from collections import Counter
import os
from time import time
from datetime import datetime

import sys
#sys.path.append('/home/bostjan/Dropbox/Code/knotpy')

import knotpy as kp
import knotpy.algorithms.topology

DATA_FOLDER = Path("data")
input = DATA_FOLDER / "knotoids-0-split-no-mirrors.txt"
output = DATA_FOLDER / "knotoids-1-reidemeister-1.txt"
output_classified = DATA_FOLDER / "knotoids-1-classified.txt"  # save PD codes of knotoids


if __name__ == "__main__":

    # cpu_count = os.cpu_count()
    # print(f"Number of CPUs: {cpu_count}")

    number_of_diagrams = kp.count_lines(input)
    CHUNK_SIZE = 6

    count_total, count_new = 0, 0

    knotoids_unique = []
    knotoids_non_unique = []
    knotoids_connected_sums = []
    knotoids_disjoint_sums = []

    print("Diagrams", sum(len(k) for k in kp.DiagramSetReader(input)))

    for knotoid_group in kp.Bar(kp.DiagramSetReader(input), total=kp.count_lines(input)):

        new_knotoid_group = set([kp.simplify(k, method="nonincreasing") for k in knotoid_group])

        new_good_group = []
        for k in new_knotoid_group:
            if kp.is_disjoint_sum(k):
                knotoids_disjoint_sums.append(k)
            elif kp.is_connected_sum(k) or len(knotpy.algorithms.topology.bridges(k)) > 2:
                knotoids_connected_sums.append(k)
            else:
                new_good_group.append(k)



        if len(new_good_group) == 1:
            knotoids_unique.append(new_good_group.pop())
        elif new_good_group:
            knotoids_non_unique.append(new_good_group)

    print("Disjoint sums:", len(knotoids_disjoint_sums))
    print("Connected sums:", len(knotoids_connected_sums))
    print("Unique knotoids:", len(knotoids_unique))
    print("Duplicate knotoids:", sum(len(g) for g in knotoids_non_unique))

    kp.save_diagrams(output_classified, knotoids_unique, comment=f"Added {datetime.now().isoformat()}")
    kp.save_diagrams("data/connected-sums-1.txt", knotoids_connected_sums, comment=f"{datetime.now().isoformat()}")
    kp.save_diagrams("data/disjoint-sums-1.txt", knotoids_disjoint_sums, comment=f"{datetime.now().isoformat()}")
    kp.save_diagram_sets(output, knotoids_non_unique)

    all_of = []
    for i, group in enumerate(knotoids_non_unique):
        for k in group:
            k.name = str(i)
            all_of.append(k)
    kp.export_pdf(all_of,"plot/knotoids-1-r-1.pdf", with_title=True)


"""

PlanarDiagram named 4 with 8 nodes, 13 arcs, and adjacencies 
a → V(b0), b → X(a0 c0 d0 d2), c → X(b1 d1 e1 f0), d → X(b2 c1 b3 g0), e → X(f1 c2 h1 h0), f → X(c3 e0 h3 h2), g → V(d3), h → X(e3 e2 f3 f2)
Traceback (most recent call last):


"""