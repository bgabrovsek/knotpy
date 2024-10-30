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
input = DATA_FOLDER / "knotoids-filter-4.txt"
output_good = DATA_FOLDER / "knotoids-filter-4-no-flips.txt"
output_flips = DATA_FOLDER / "knotoids-filter-4-flips.txt"

flattened = []

def is_same(d:kp.PlanarDiagram, mirror, flip):

    global flattened
    invariant_functions = (lambda q: kp.kauffman_bracket_skein_module(q, normalize=True)[0][0],
                           kp.affine_index_polynomial,
                           kp.arrow_polynomial,
                           kp.mock_alexander_polynomial)

    x = d.copy()
    if mirror:
        x = kp.mirror(x, inplace=True)
    if flip:
        x = kp.flip(x, inplace=True)

    text = "mirror flip" if flip and mirror else ("flip" if flip else "mirror")

    is_the_same = False

    inv_d = list(i(d) for i in invariant_functions)
    inv_x = list(i(x) for i in invariant_functions)

    if inv_d == inv_x:
        print(text)
        if x in flattened:
            is_is = flattened[flattened.index(x)]
            x.name = f"{x.name} ({text} of {is_is.name})"
            is_the_same = True
            print("Yes")
        else:
            x = kp.simplify_smart(x, depth=1)
            if x in flattened:
                is_is = flattened[flattened.index(x)]
                x.name = f"{x.name} ({text} of {is_is.name})"
                is_the_same = True
                print("Yes")
    return x, is_the_same


if __name__ == "__main__":

    collection = kp.load_collection(input)

    good_collection = []
    flip_collection = []

    for diagrams in kp.Bar(collection):

        good_diagrams = []
        flip_mirror_diagrams = []

        for d in diagrams:

            is_the_same_ = False

            for flip, mirror in [(True, False), (False, True), (True, True)]:
                x, is_the_same_ = is_same(d, flip, mirror)
                if is_the_same_:
                    flip_mirror_diagrams.append(x)
                    break

            if not is_the_same_:
                flattened.append(d)
                good_diagrams.append(d)

        if good_diagrams:
            good_collection.append(good_diagrams)

        if flip_mirror_diagrams:
            flip_collection.append(flip_mirror_diagrams)

    print("Good:", len(good_collection), sum(len(d) for d in good_collection))
    print("Flip:", len(flip_collection), sum(len(d) for d in flip_collection))
    kp.save_collection(output_good, good_collection)
    kp.save_collection(output_flips, flip_collection)

    kp.export_pdf()

"""


Counter({1: 842, 2: 458, 3: 185, 4: 181, 5: 87, 6: 60, 7: 47, 8: 45, 10: 20, 12: 20, 9: 15, 11: 15, 13: 14, 20: 7, 15: 7, 32: 7, 16: 6, 17: 6, 21: 6, 18: 6, 36: 5, 22: 5, 19: 5, 14: 4, 
26: 4, 49: 3, 48: 3, 58: 3, 40: 3, 30: 3, 54: 3, 45: 3, 76: 2, 25: 2, 29: 2, 47: 2, 41: 2, 27: 2, 28: 2, 53: 2, 33: 2, 23: 2, 62: 2, 24: 2, 1043: 1, 87: 1, 227: 1, 225: 1, 373: 1, 1390: 1, 439: 1, 122: 1, 144: 1, 44: 1, 117: 1, 161: 1, 103: 1, 86: 1, 267: 1, 111: 1, 38: 1, 67: 1, 78: 1, 56: 1, 199: 1, 64: 1, 75: 1, 156: 1, 37: 1, 79: 1, 80: 1, 46: 1, 82: 1, 60: 1, 34: 1, 55: 1}) -> 
Counter({1: 1074, 2: 965, 3: 44, 4: 40, 5: 5, 6: 4, 8: 1, 10: 1})


"""