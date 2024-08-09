from pathlib import Path
import os
import sympy
import matplotlib.pyplot as plt
import multiprocessing
from collections import Counter

# import sys
# sys.path.append('/home/bostjan/remote_code/knotpy')

import knotpy as kp

DATA_FOLDER = Path("data")
input = DATA_FOLDER / "knotoids-filter-1.txt"
output = DATA_FOLDER / "knotoids-filter-1-nosums.txt"

def remove_obvious_sums(knots):
    at_lest_one_sum = False
    all_are_sums = True

    knots_that_are_not_sums = []

    for k in knots:
        three_bridges = len(kp.bridges(k)) > 2
        is_sum = kp.is_connected_sum(k) or three_bridges
        at_lest_one_sum |= is_sum
        all_are_sums &= is_sum

        if not is_sum:
            knots_that_are_not_sums.append(k)
    # if all_are_sums:
    #     return "*"
    # if at_lest_one_sum:
    #     return "-"
    # return " "
    return knots_that_are_not_sums

def print_stats(filename):
    group_sizes = kp.invariant_collection_group_sizes(filename, "pdc")
    number_of_groups = sum(val for val in group_sizes.values())
    number_of_diagrams = sum(key * val for key, val in group_sizes.items())
    print(f"In {filename} there are:")
    print(f"  {number_of_groups} groups containing {number_of_diagrams} diagrams")
    print(f"  Group sizes:", " ".join([f"{x}:{y}" for x,y in sorted(group_sizes.items())]))

print("Input:", input)

print_stats(input)

comment = "Knotoids up to 6 crossings without mirrors simplified once in parallel without sums // 9.8.2024"

header = kp.load_invariant_collection_header(input)
# save an empty file containing only comments and headers
kp.save_invariant_collection(filename=output, data=[], invariant_names=header, notation="cpd", comment=comment)

counter = 0
for diagrams, invariant in kp.load_invariant_collection_iterator(input, "cpd"):

    counter += 1
    new_diagrams = remove_obvious_sums(diagrams)

    if len(new_diagrams) == 0:
        print("#", end="" if counter % 100 else "\n")
    elif len(new_diagrams) < len(diagrams):
        print("?", end="" if counter % 100 else "\n")
    else:
        print(" ", end="" if counter % 100 else "\n")

    if new_diagrams:
        kp.append_invariant_collection(output, new_diagrams, invariant, "cpd")

print()
print_stats(output)

print("Output:", output)
