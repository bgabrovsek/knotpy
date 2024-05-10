import csv

from knotpy.readwrite.read_invariants import read_invariants_from_csv
from knotpy.invariants.jones import jones_polynomial
from knotpy.algorithms.orientation import all_orientations

# Read the CSV file
data = read_invariants_from_csv("knotinfo.csv")
for knot_name in data:
    k = data[knot_name]["diagram"]

    print(k)

    ok = all_orientations(k)
    for o in ok:
        print("   ", o)

    jones_knotinfo = data[knot_name]["Jones"]
    joneses = [jones_polynomial(o) for o in ok]

    print(k.name, jones_knotinfo, joneses)