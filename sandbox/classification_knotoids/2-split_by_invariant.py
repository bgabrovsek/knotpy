from pathlib import Path

import sympy
from tqdm import tqdm
from time import time
from collections import defaultdict
import knotpy as kp

DATA_FOLDER = Path("data")
POLY_FOLDER = Path("polynomials")
filename_knots = {6: "knots_pdcodes-2-6.gz", 7: "knots_pdcodes-7.gz", 8: "knots_pdcodes-8.gz", 9: "knots_pdcodes-9.gz", 10: "knots_pdcodes-10.gz"}
path_kauffman = DATA_FOLDER / "kbsm.csv"


def poly2str(poly):
    d = ["/d", "*x", "+p", "-m", " s", "(o", ")z"]
    s = str(poly)
    for x, y in d:
        s = s.replace(x, y)
    return s

def str2poly(s):
    d = ["/d", "*x", "+p", "-m", " s", "(o", ")z"]
    for x, y in d:
        s = s.replace(y, x)
    return sympy.sympify(s)


LOAD_KBSM_FROM_CSV = False

print("Loading...", end=" ")
knots = kp.load_collection(DATA_FOLDER / filename_knots[6])
print("6", end=" ")
knots += kp.load_collection(DATA_FOLDER / filename_knots[7])
print("7", end=" ")
knots += kp.load_collection(DATA_FOLDER / filename_knots[8])
print("8", end=" ")
# ls

print("done.")


print("Canonical...", end=" ")
canonical_knots = [kp.canonical(k) for k in knots]
print("done")

s = set(canonical_knots)
print(f"There are {len(s)} unique diagrams out of {len(canonical_knots)} diagrams.")

print("computing KBSM...")

kbsm_dict = defaultdict(set)
for k in tqdm(canonical_knots):
    #print(k)
    kbsm_expr = kp.kauffman_bracket_skein_module(k)
    if len(kbsm_expr) != 1:
        raise ValueError("KBSM wrong generators")
    poly = kbsm_expr[0][0]

    kbsm_dict[poly].add(k)

print("There are", len(kbsm_dict), "polies with", sum(len(v) for v in kbsm_dict.values()),"knots")

for poly in kbsm_dict:

    filename = poly2str(poly) + ".gz"
    min_crossing_number = min(len(k) for k in kbsm_dict[poly])
    filename = str(min_crossing_number) + "_" + filename
    filename = POLY_FOLDER / filename

    kp.save_collection(filename, kbsm_dict[poly])

#knots_kbsm = dict()
#for k in tqdm(canonical_knots):

 #   knots_kbsm[k] = {"kbsm": str(kp.kauffman_bracket_skein_module(k)[0][0])}

# kp.save_invariant_collection(path_kauffman, knots_kbsm)
#
#
# print("Number of diagrams", len(knots_kbsm))
# # splitting knots into groups
# groups = kp.inverse_nested_dict(knots_kbsm)
#
#
# print(f"There are {len(groups)} unique KBSM's and {sum([len(groups[inv]) == 1 for inv in groups])} unique (classified) diagrams.")
