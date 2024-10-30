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

diagrams = kp.load_collection(input)
diagrams = [d[0] for d in diagrams]
for d in diagrams:
    d.name = kp.to_condensed_pd_notation(d)


kp.export_pdf([d for d in diagrams], "plot/filt4.pdf", with_title=True)