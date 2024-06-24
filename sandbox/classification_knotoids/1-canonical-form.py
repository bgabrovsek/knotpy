from pathlib import Path
from itertools import combinations, chain
from time import time
import knotpy as kp
from random import choice


t = time()
DATA_FOLDER = Path("data")
path_knots_6 = DATA_FOLDER / "knots_pdcodes-2-6.gz"
path_knots_7 = DATA_FOLDER / "knots_pdcodes-7.gz"
path_knots_8 = DATA_FOLDER / "knots_pdcodes-8.gz"
path_knots_9 = DATA_FOLDER / "knots_pdcodes-9.gz"
path_knots_10 = DATA_FOLDER / "knots_pdcodes-10.gz"

knots = kp.load_collection(path_knots_6)
canonical_knots = [kp.canonical(k) for k in knots]


for k in canonical_knots:
    b = kp.kauffman_bracket_skein_module(k, normalize=True)

    if len(b) != 1:
        raise ValueError
    poly = b[0]

    #print(k)

    r3_areas = list(kp.find_reidemeister_3_triangles(k))
    if len(r3_areas) >= 1:
        a = choice(r3_areas)
        kp.reidemeister_3(k, a)

        #print(k)
        b = kp.kauffman_bracket_skein_module(k, normalize=True)
        poly2 = b[0]

        if poly != poly2:
            print("Wrong")
        else:
            print("good.")

    #print()

    #print(list(kp.find_reidemeister_3_nonalternating_triangles(k)))
