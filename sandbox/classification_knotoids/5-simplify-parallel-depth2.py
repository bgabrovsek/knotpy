from pathlib import Path
import os
import sympy
import matplotlib.pyplot as plt
import multiprocessing
from collections import Counter
from functools import partial
from tqdm import tqdm

import sys
sys.path.append('/home/bostjan/remote_code/knotpy')

import knotpy as kp


import random

# shared_number_of_groups = None
# shared_group_counter = None

# TODO: paralize

DATA_FOLDER = Path("data")
input = DATA_FOLDER / "knotoids-filter-1-nosums.txt"
output = DATA_FOLDER / "knotoids-filter-2.txt"
header = None

def simplify_knotoid_group_and_write(lock, knotoids_invaraints_pair):
    """

    :param knotoids:
    :param invariants:
    :param lock:
    :return:
    """

    knotoids, invariants = knotoids_invaraints_pair

    # make nice names for knots "crossings number.index"
    minimal_crossings = min(len(k) - 1 for k in knotoids)
    knotoids = sorted(knotoids)
    for i, k in enumerate(knotoids):
        k.name = f"{minimal_crossings}-{i}"

    er = kp.EquivalenceRelation([kp.canonical(k) for k in knotoids])  # put knots into equiv. relation

    # Filter no. 2: Simplify with depth 1
    if er.number_of_classes() > 1:
        for k in list(er.representatives()):
            er[k] = kp.canonical(kp.simplify(k, depth=2, method="smart", framed=False))  # already in canonical form

    diagrams_in_group = list(er.representatives())

    if lock is None:
        kp.append_invariant_collection(output, diagrams_in_group, invariants,"cpd")
    else:
        with lock:
            # append the computations to the classification file
            kp.append_invariant_collection(output, diagrams_in_group, invariants, "cpd")

    print("*", end="" if random.randint(0, 100) else "\n", flush=True)
    # print(knotoids)
    # print(invariants)
    # print(lock)
    return

def print_stats(filename):
    group_sizes = kp.invariant_collection_group_sizes(filename, "pdc")
    number_of_groups = sum(val for val in group_sizes.values())
    number_of_diagrams = sum(key * val for key, val in group_sizes.items())
    print(f"In {filename} there are:")
    print(f"  {number_of_groups} groups containing {number_of_diagrams} diagrams")
    print(f"  Group sizes:", " ".join([f"{x}:{y}" for x,y in sorted(group_sizes.items())]))


if __name__ == "__main__":

    print("Input:", input)

    PARALLEL = True

    comment = f"Knotoids up to 6 crossings without mirrors simplified with depth 2 in parallel // 9.8.2024"

    print_stats(input)

    header = kp.load_invariant_collection_header(input)

    # save an empty file containing only comments and headers
    kp.save_invariant_collection(filename=output, data=[], invariant_names=header, notation="cpd", comment=comment)



    if PARALLEL:
        # Create a manager to manage shared objects and create managed lock object
        manager = multiprocessing.Manager()

        lock = manager.Lock()

        # shared_number_of_groups = manager.int()
        # shared_group_counter = manager.int()
        # shared_number_of_groups = kp.count_lines(input)
        # shared_group_counter = 0

        process_func = partial(simplify_knotoid_group_and_write, lock)

        with multiprocessing.Pool(processes=multiprocessing.cpu_count() - 1) as pool:
            pool.map(process_func, kp.load_invariant_collection_iterator(input, notation="cpd"))
            #pool.map(process_func, kp.load_invariant_collection_iterator(input, notation="cpd"))


    else:
        for q in kp.load_invariant_collection_iterator(input, notation="cpd"):
            simplify_knotoid_group_and_write(None, q)

    print("\nSimplification finished")
    print_stats(output)

    print("Output:", output)
    #
    # header = classification_file_header(input_knotoids)
    # print("Header", header)
    #
    # exit()
    # for invariants, knots in loop_classification_file(input_knotoids, kp.from_condensed_pd_notation):
    #
    #     print(invariants, knots)



#
#
#
# with multiprocessing.Pool(processes=multiprocessing.cpu_count()-2) as pool:
#     results = pool.map(process_knot_group, filenames)
#
# print("Original groups:", Counter([b for a, b in results]))
# print("     New groups:", Counter([a for a, b in results]))
