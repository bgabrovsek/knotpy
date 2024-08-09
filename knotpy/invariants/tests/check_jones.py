import csv

from knotpy.readwrite.read_invariants import read_invariants_from_csv
from knotpy.invariants.jones_polynomial import jones_polynomial
from knotpy.invariants.bracket import bracket_polynomial
from knotpy.algorithms.orientation import all_orientations, unoriented

# From the csv file read: Name,PD Notation,Alexander,Jones,Conway,Kauffman,HOMFLYPT
data = read_invariants_from_csv("knotinfo.csv")

import os

# get the current working directory
current_working_directory = os.getcwd()

# print output to the console
print(current_working_directory)

for knot_name in data:
    k = data[knot_name]["diagram"]
    print(k)
    print(bracket_polynomial(k, normalize=False))

    ok = all_orientations(k)
    for o in ok:
        print("   ", o, [o.nodes[node].sign() for node in o.nodes])
        print("bracket", bracket_polynomial(o))

    jones_knotinfo = data[knot_name]["Jones"]
    joneses = [jones_polynomial(o) for o in ok]


    #print(k.name, jones_knotinfo, joneses)
    print("   ", jones_knotinfo)
    for j in joneses:
        print("   ", j)

    exit()