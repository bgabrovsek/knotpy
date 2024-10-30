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
input = DATA_FOLDER / "knotoids-filter-4-no-flips.txt"

unique = []
non_unique = []
for j in kp.load_collection_iterator(input):


    if len(j) == 1:
        unique += j
    else:
        non_unique.append(j)


#kp.export_pdf(unique, "plot/filter-4/unique.pdf",with_title=True)


for i, j in kp.Bar(enumerate(non_unique), total=len(non_unique)):
    if len(j) <= 1:
        continue
    s = "plot/filter-4/" + str(len(j)) + "_" + str(i).zfill(4) + ".pdf"
    kp.export_pdf(j, s, with_title=True)
#kp.export_pdf()