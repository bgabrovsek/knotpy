from pathlib import Path
import os
import sympy
import matplotlib.pyplot as plt
import multiprocessing
from collections import Counter
from functools import partial
from tqdm import tqdm
import random
import os
from time import time
from math import ceil

import sys
sys.path.append('/home/bostjan/Dropbox/Code/knotpy')

import knotpy as kp

DATA_FOLDER = Path("data")
input = DATA_FOLDER / "knotoids-filter-0.txt"
output = DATA_FOLDER / "knotoids-filter-1.txt"
header = None
#
# def simplify_knotoid_group_and_write(lock, knotoids_invaraints_pair):
#     """
#
#     :param knotoids:
#     :param invariants:
#     :param lock:
#     :return:
#     """
#
#     knotoids, invariants = knotoids_invaraints_pair
#
#     # make nice names for knots "crossings number.index"
#     minimal_crossings = min(len(k) - 1 for k in knotoids)
#     knotoids = sorted(knotoids)
#     for i, k in enumerate(knotoids):
#         k.name = f"{minimal_crossings}-{i}"
#
#     result = kp.simultaneously_simplify_group(knotoids, depth=1)
#
#     # er = kp.EquivalenceRelation([kp.canonical(k) for k in knotoids])  # put knots into equiv. relation
#     #
#     #
#     # # Filter no. 1: non-increasing Reidemeister moves
#     # if er.number_of_classes() > 1:
#     #     for k in list(er.representatives()):
#     #         er[k] = kp.canonical(kp.simplify(k, method="nonincreasing", framed=False))  # it's already in canonical form
#     #
#     # # Filter no. 2: Simplify with depth 1
#     # if er.number_of_classes() > 1:
#     #     for k in list(er.representatives()):
#     #         er[k] = kp.canonical(kp.simplify(k, depth=1, method="smart", framed=False))  # already in canonical form
#
#     # diagrams_in_group = list(er.representatives())
#
#     if lock is None:
#         kp.append_invariant_collection(output, result, invariants,"cpd")
#     else:
#         with lock:
#             # append the computations to the classification file
#             kp.append_invariant_collection(output, result, invariants, "cpd")
#
#     print(f"{len(knotoids)}->{len(result)} ", end="" if random.randint(0, 100) else "\n", flush=True)
#
#     # print(knotoids)
#     # print(invariants)
#     # print(lock)
#     return

# def print_stats(filename):
#     group_sizes = kp.invariant_collection_group_sizes(filename, "pdc")
#     number_of_groups = sum(val for val in group_sizes.values())
#     number_of_diagrams = sum(key * val for key, val in group_sizes.items())
#     print(f"In {filename} there are:")
#     print(f"  {number_of_groups} groups containing {number_of_diagrams} diagrams")
#     print(f"  Group sizes:", " ".join([f"{x}:{y}" for x,y in sorted(group_sizes.items())]))
#

if __name__ == "__main__":

    PARALLEL = True

    cpu_count = os.cpu_count()
    print(f"Number of CPUs: {cpu_count}")

    group_sizes_before = []
    group_sizes_after = []
    comment = f"Knotoids up to 6 crossings without mirrors simplified once in parallel // 8.8.2024"

    t = time()

    kp.init_collection(output, multiple_diagrams_per_line=True, comment=comment)

    num_diagrams = kp.count_lines(input)

    CHUNK_SIZE = 8

    # print statistics of the input
    for chunk in kp.Bar(kp.load_collection_chunk_iterator(input, CHUNK_SIZE), total=ceil(num_diagrams/CHUNK_SIZE)):

        group_sizes_before.extend([len(g) for g in chunk])

        result = kp.simultaneously_simplify_diagrams_parallel(chunk, 1, processes=8)

        kp.extend_collection(output, result)

        group_sizes_after.extend([len(g) for g in result])

    print(f"{Counter(group_sizes_before)} -> {Counter(group_sizes_after)}")

    print("Time spent:", time()-t)

"""


Counter({1: 842, 2: 458, 3: 185, 4: 181, 5: 87, 6: 60, 7: 47, 8: 45, 10: 20, 12: 20, 9: 15, 11: 15, 13: 14, 20: 7, 15: 7, 32: 7, 16: 6, 17: 6, 21: 6, 18: 6, 36: 5, 22: 5, 19: 5, 14: 4, 
26: 4, 49: 3, 48: 3, 58: 3, 40: 3, 30: 3, 54: 3, 45: 3, 76: 2, 25: 2, 29: 2, 47: 2, 41: 2, 27: 2, 28: 2, 53: 2, 33: 2, 23: 2, 62: 2, 24: 2, 1043: 1, 87: 1, 227: 1, 225: 1, 373: 1, 1390: 1, 439: 1, 122: 1, 144: 1, 44: 1, 117: 1, 161: 1, 103: 1, 86: 1, 267: 1, 111: 1, 38: 1, 67: 1, 78: 1, 56: 1, 199: 1, 64: 1, 75: 1, 156: 1, 37: 1, 79: 1, 80: 1, 46: 1, 82: 1, 60: 1, 34: 1, 55: 1}) -> 
Counter({1: 1074, 2: 965, 3: 44, 4: 40, 5: 5, 6: 4, 8: 1, 10: 1})


"""