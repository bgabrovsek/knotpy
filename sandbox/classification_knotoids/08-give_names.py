from pathlib import Path
import os
import sympy
import matplotlib.pyplot as plt
import multiprocessing
from collections import Counter

import sys
sys.path.append('/home/bostjan/remote_code/knotpy')

import knotpy as kp

DATA_FOLDER = Path("data")
input = DATA_FOLDER / "knotoids-filter-3.txt"
output = DATA_FOLDER / "knotoids-filter-3-names.txt"

names = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]

kp.init_collection(output,multiple_diagrams_per_line=True,comment="named no sums no mirrors")

for diagrams in kp.Bar(kp.load_collection(input)):
    for d in diagrams:
        N = len(d) - 2

        name = str(N) + "_" + str(names[N])
        names[N] += 1

        if d.name is None:
            d.name = name
        else:
            d.name = name + " " + d.name

    kp.append_to_collection(output, diagrams)

kp.append_comment(output, "done.")