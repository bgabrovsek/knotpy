from pathlib import Path
import os
import sympy

import knotpy as kp

DATA_FOLDER = Path("data")


knots = kp.load_collection(DATA_FOLDER / "knotoids_native_codes-6.gz")



        #print("  ", k)


k = knots[3]

k = kp.from_pd_notation("X[0,1,2,3],X[4,5,6,7],X[3,2,8,9],X[8,1,10,11],X[12,4,6,13],X[11,14,5,12],X[9,13,14,10],V[0],V[7]")
print(k)
import matplotlib.pyplot as plt
kp.draw(k)
plt.show()