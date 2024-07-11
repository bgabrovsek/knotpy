"""Load knotoids from files and split them by their invariant (normalized Kauffman bracket).
For each polynomial, store the knotoids into a file (with the name of that polynomial)
"""
from pathlib import Path

import sympy
from tqdm import tqdm
from time import time
from collections import defaultdict
import knotpy as kp

DATA_FOLDER = Path("data")
POLY_FOLDER = Path("polys")
#POLY_FOLDER = Path("polynomials-10")
#filename_knots = {6: "knots_pdcodes-2-6.gz", 7: "knots_pdcodes-7.gz", 8: "knots_pdcodes-8.gz", 9: "knots_pdcodes-9.gz", 10: "knots_pdcodes-10.gz"}
#path_kauffman = DATA_FOLDER / "kbsm.csv"


def poly2str(poly):
    """Convert polynomial into a filename-type string"""
    s = str(poly)
    for x, y in ["/d", "*x", "+p", "-m", " _", "(o", ")z"]:
        s = s.replace(x, y)
    return s

def str2poly(s):
    """Convert a filename--type string into a polynomial"""
    for x, y in ["/d", "*x", "+p", "-m", " _", "(o", ")z"]:
        s = s.replace(y, x)
    return sympy.sympify(s)

# load knotoids
print("Loaing...", end="")
knotoids = []
for i in range(5):
    knotoids += kp.load_collection(DATA_FOLDER / f"knotoids_native_codes-{i}.gz")

print(f"loaded {len(knotoids)} knots.")
# print(end="9 ")
# knotoids += kp.load_collection(DATA_FOLDER / "knotoids_native_codes-10.gz")
# print(end="10 ")

# they should already be in canonical form
# print("Checking canonical from")
# for k in tqdm(knotoids[::10]):
#     if k != kp.canonical(k):
#         raise ValueError("Knotoids not in canonical form")  # just a check: at step 1 we saved them into canonical form


print(f"There are {len(set(knotoids))} unique diagrams out of {len(knotoids)} loaded diagrams.")

print("Computing KBSMs...")

kbsm_dict = defaultdict(set)  # store kbsm's (Kauffman bracket polynomials)
for k in tqdm(knotoids):

    kbsm_expr = kp.kauffman_bracket_skein_module(k)
    if len(kbsm_expr) != 1:  # for knotoids there should only be 1 generator of the KBSM (the trivial knotoid)
        raise ValueError("KBSM wrong generators")
    poly = kbsm_expr[0][0]  # get the polynomial

    kbsm_dict[poly].add(k)  # add the knotoid to the polynomial group

print("There are", len(kbsm_dict), "polynomials with", sum(len(v) for v in kbsm_dict.values()), "knots")

poly_group_sizes = defaultdict(int)
for p in kbsm_dict:
    poly_group_sizes[len(kbsm_dict[p])] += 1

for length in sorted(poly_group_sizes):
    print("Group size:", length, "count:", poly_group_sizes[length])

# save
for poly in kbsm_dict:

    filename = poly2str(poly) + ".gz"  # convert the polynomial to a filename type string (no characters "*", "/", ...)
    min_crossing_number = min(len(k) for k in kbsm_dict[poly])  # prepend to the filename the smallest number of crossings
    filename = str(min_crossing_number) + "_" + filename
    filename = POLY_FOLDER / filename

    kp.save_collection(filename, kbsm_dict[poly])
