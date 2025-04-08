import knotpy as kp


s = "V[0,1,2],V[3,4,5],V[1,6,7],V[8,9,7],X[5,10,11,9],X[12,13,11,10],X[4,2,13,12],X[0,3,8,6]"
k = kp.from_pd_notation(s)
kk = kp.simplify(k,"ni")
print(k)
print(kk)