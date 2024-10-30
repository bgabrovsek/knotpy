import matplotlib.pyplot as plt
from knotpy import kp
pd = "X[0,1,2,3],X[4,5,6,7],X[1,8,9,10],X[11,12,13,9],X[14,15,7,16],X[17,18,19,13],X[10,20,17,12],X[20,19,15,14],V[3,21,22],V[5,23,24],V[6,24,16],V[4,18,23],V[0,22,8],V[2,11,21]"
k = kp.from_pd_notation(pd)
print(pd)
kp.draw(k, draw_circles=True)
plt.show()