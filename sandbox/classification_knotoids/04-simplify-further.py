from pathlib import Path
import knotpy as kp

import knotpy.algorithms.topology

DATA_FOLDER = Path("data")
input = "data/knotoids-1-reidemeister-1.txt"
output = "data/knotoids-2-reidemeister-1.txt"
output_classified = "data/knotoids-2-classified.txt"  # save PD codes of knotoids

knotoids = kp.load_diagram_sets(input)
knotoids_unclassified = []
knotoids_classified = []
knotoids_sums = []
for group in kp.Bar(knotoids):

    new_group = []

    for k in {kp.simplify(k, depth=1) for k in group}:
        if kp.is_disjoint_sum(k) or kp.is_connected_sum(k) or len(knotpy.algorithms.topology.bridges(k)) > 2:
            knotoids_sums.append(k)
        else:
            new_group.append(k)

    if len(new_group) == 1:
        knotoids_classified.append(new_group[0])
    elif new_group:
        knotoids_unclassified.append(new_group)

print("Classified:", len(knotoids_classified))
print("Sums      :", len(knotoids_sums))
print("Unclassifi:", sum(len(g) for g in knotoids_unclassified))

kp.save_diagram_sets(output, knotoids_unclassified)
kp.save_diagrams(output_classified)

