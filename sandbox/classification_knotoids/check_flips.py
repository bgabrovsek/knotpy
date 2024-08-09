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
input = DATA_FOLDER / "knotoids-filter-2.txt"
#output = DATA_FOLDER / "knotoids-filter-1-nosums.txt"

def is_flip(group):

    a, b = group

    f = kp.canonical(kp.flip(b, inplace=False))
    a = kp.canonical(a)

    if a == f:
        return True

    a = kp.canonical(kp.simplify(a, depth=1, method="smart", framed=False))  # already in canonical form
    f = kp.canonical(kp.simplify(f, depth=1, method="smart", framed=False))  # already in canonical form

    if a == f:
        return True

    a = kp.canonical(kp.simplify(a, depth=2, method="smart", framed=False))  # already in canonical form
    f = kp.canonical(kp.simplify(f, depth=2, method="smart", framed=False))  # already in canonical form

    return a == f



print("Input:", input)


#comment = "Knotoids up to 6 crossings without mirrors simplified once in parallel without sums // 9.8.2024"

header = kp.load_invariant_collection_header(input)
# save an empty file containing only comments and headers
#kp.save_invariant_collection(filename=output, data=[], invariant_names=header, notation="cpd", comment=comment)

for diagrams, invariant in kp.load_invariant_collection_iterator(input, "cpd"):

    if len(diagrams) == 1:
        continue

    elif len(diagrams) == 2:
        if is_flip(diagrams):
            print("ok")
        else:
            print("!!!!!")

    else:
        print("Error!")

    # counter += 1
    # new_diagrams = remove_obvious_sums(diagrams)
    #
    # if len(new_diagrams) == 0:
    #     print("#", end="" if counter % 100 else "\n")
    # elif len(new_diagrams) < len(diagrams):
    #     print("?", end="" if counter % 100 else "\n")
    # else:
    #     print(" ", end="" if counter % 100 else "\n")
    #
    # if new_diagrams:
    #     kp.append_invariant_collection(output, new_diagrams, invariant, "cpd")

print()
# print_stats(output)
#
# print("Output:", output)
