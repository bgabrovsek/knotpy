import knotpy as kp

k = kp.from_pd_notation("X[0,1,2,3],X[4,5,6,7],X[6,8,5,4],X[9,10,11,8],V[7],V[0],X[1,3,12,2],X[11,12,10,9]")
print(k)
kp.export_png(k,"test.png")
print("---")
print(kp.cut_sets(k, 1))
print("---")
print(kp.cut_sets(k, 2))