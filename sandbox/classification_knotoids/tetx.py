import knotpy as kp

import knotpy.algorithms.topology

k = kp.from_pd_notation("V[0],X[0,1,2,3],X[1,4,5,6],X[2,4,3,7],X[8,5,9,10],X[6,8,11,12],V[7],X[10,9,12,11]")
print(k)
# kp.export_png(k,"test.png")
print("---")
print(kp.cut_sets(k, 1))
print("---")
print(kp.cut_sets(k, 2))
print(knotpy.algorithms.topology.bridges(k))
print(kp.is_connected_sum(k))