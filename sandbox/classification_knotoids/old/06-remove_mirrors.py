from pathlib import Path
import os
import sympy
import matplotlib.pyplot as plt
import multiprocessing
from collections import Counter
from functools import partial
import random
import os
from time import time
from math import ceil

import sys

import knotpy.manipulation.symmetry

sys.path.append('/home/bostjan/Dropbox/Code/knotpy')


import knotpy as kp

DATA_FOLDER = Path("../data")
input = DATA_FOLDER / "knotoids-filter-2.txt"
output = DATA_FOLDER / "knotoids-filter-2-no-mirrors.txt"
header = None

def remove_mirror(diagrams):

    N = len(diagrams)
    mirr = kp.EquivalenceRelation(list(range(N)))

    for i in range(N):
        for j in range(i+1, N):
            d = diagrams[i].copy()
            m = knotpy.manipulation.symmetry.mirror(diagrams[j].copy())

            r = kp.simultaneously_simplify_diagrams([d, m], depth=1)
            if len(r) == 1:
                print("reduced")
                mirr[i] = j
    return [diagrams[i] for i in mirr.representatives()]



if __name__ == "__main__":

    PARALLEL = True

    cpu_count = os.cpu_count()
    print(f"Number of CPUs: {cpu_count}")

    group_sizes_before = []
    group_sizes_after = []
    comment = f"Knotoids up to 6 crossings with mirros removed // 17.10.2024"

    t = time()

    # diagrams = "b1,c1a0c0c2,b2b0b3d0,c3e0f1f0,d1g0f3f2,d3d2e3e2,e1 & b0,a0c0c3c1,b1b3d0b2,c2e0f1f0,d1g0f3f2,d3d2e3e2,e1"
    # diagrams = [kp.from_condensed_em_notation(m) for m in diagrams.split(" & ")]
    #
    # k = diagrams[0]
    # m = kp.mirror(diagrams[1])
    #
    # print(k)
    # print(m)
    # print()
    #
    # k = kp.canonical(k)
    # m = kp.canonical(m)
    #
    # print(k)
    # print(m)
    # print()
    #
    # k = kp.simplify_smart(k, 3)
    # m = kp.simplify_smart(m, 3)
    #
    # print(k)
    # print(m)
    # # result = remove_mirror(diagrams)
    # # for r in result:
    # #     print(r)
    # exit()

    kp.init_collection(output, multiple_diagrams_per_line=True, comment=comment)

    num_diagrams = kp.count_lines(input)

    CHUNK_SIZE = int(cpu_count * 3/4)

    # print statistics of the input
    for chunk in kp.Bar(kp.load_collection_chunk_iterator(input, CHUNK_SIZE), total=ceil(num_diagrams/CHUNK_SIZE)):

        group_sizes_before.extend([len(g) for g in chunk])

        good_chunk = [diagrams for diagrams in chunk if len(diagrams) == 1]
        bad_chunk = [diagrams for diagrams in chunk if len(diagrams) > 1]

        # result = [
        #     remove_mirror(diagrams) for diagrams in bad_chunk
        # ]

        with multiprocessing.Pool(processes=32) as pool:
            result = pool.map(remove_mirror, bad_chunk)

        #result = kp.simultaneously_simplify_diagrams_parallel(bad_chunk, 2, processes=cpu_count)

        result = good_chunk + result

        kp.extend_collection(output, result)

        group_sizes_after.extend([len(g) for g in result])

    kp.append_comment(output, "done.")
    print("done.")
    print(f"{Counter(group_sizes_before)} -> {Counter(group_sizes_after)}")

    print("Time spent:", time()-t)

"""


Counter({1: 842, 2: 458, 3: 185, 4: 181, 5: 87, 6: 60, 7: 47, 8: 45, 10: 20, 12: 20, 9: 15, 11: 15, 13: 14, 20: 7, 15: 7, 32: 7, 16: 6, 17: 6, 21: 6, 18: 6, 36: 5, 22: 5, 19: 5, 14: 4, 
26: 4, 49: 3, 48: 3, 58: 3, 40: 3, 30: 3, 54: 3, 45: 3, 76: 2, 25: 2, 29: 2, 47: 2, 41: 2, 27: 2, 28: 2, 53: 2, 33: 2, 23: 2, 62: 2, 24: 2, 1043: 1, 87: 1, 227: 1, 225: 1, 373: 1, 1390: 1, 439: 1, 122: 1, 144: 1, 44: 1, 117: 1, 161: 1, 103: 1, 86: 1, 267: 1, 111: 1, 38: 1, 67: 1, 78: 1, 56: 1, 199: 1, 64: 1, 75: 1, 156: 1, 37: 1, 79: 1, 80: 1, 46: 1, 82: 1, 60: 1, 34: 1, 55: 1}) -> 
Counter({1: 1074, 2: 965, 3: 44, 4: 40, 5: 5, 6: 4, 8: 1, 10: 1})


"""