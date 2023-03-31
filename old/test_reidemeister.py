from knotted import *
from HOMFLYPT import *
from reidemeister_walk import *
from reidemeister_moves import *


KNOTS = load_knots("data/00-knots-7-reduced-02.txt")


for i, K in enumerate(KNOTS):
    print(str(i)+": ",K.name)
    for r_count in range(13):
        random_Reidemesiter_move_check(K, HSM)
