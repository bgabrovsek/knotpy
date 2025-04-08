from pathlib import Path
import os
import sympy
import matplotlib.pyplot as plt
import multiprocessing
from collections import Counter

import sys


import knotpy.algorithms.topology

sys.path.append('/home/bostjan/remote_code/knotpy')

import knotpy as kp

DATA_FOLDER = Path("../data")
input = DATA_FOLDER / "knotoids-filter-3-names.txt"
output = DATA_FOLDER / "knotoids-filter-4.txt"

collection = kp.load_collection(input)
flatten = [d for diagrams in collection for d in diagrams]

good_collection = []

for diagrams in kp.Bar(collection):
    good_diagrams = []
    for k in diagrams:
        if not (len(knotpy.algorithms.topology.bridges(k)) > 2 or kp.is_connected_sum(k)):
            good_diagrams.append(k)
    if good_diagrams:
        good_collection.append(good_diagrams)


kp.save_collection(output, good_collection, comment="with names not sums")