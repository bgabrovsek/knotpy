from knotted import *
from reidemeister_walk import *

A1 = Knotted([Crossing([0,1,2,3], -1), Crossing([5,2,1,4], -1), Crossing([3,5,6,7], 1), Crossing([4,0,8,9], 1), Vertex([6,9,10],[1,0,0],[0,0,1]), Vertex([7,10,8],[0,1,1],[0,1,0])], name='2587')
A2 = Knotted([Crossing([0,1,2,3], -1), Crossing([5,2,1,4], -1), Crossing([3,5,6,7], 1), Crossing([4,0,8,9], 1), Vertex([6,9,10],[1,0,0],[0,0,1]), Vertex([11,10,12],[1,1,0],[0,1,0]), Crossing([8,7,11,12], 1)], name='2587')


h1 = HSM(A1)

for i in range(30):

    hx = HSM(A2)
    print(equal(h1, hx),"\n", h1, "\n", hx)

    if not equal(h1, hx):
        exit()

#h2 = HSM(A2)
#print(h1) # OK
#print(h2) # NOT OK
#print(equal(h1,h2))


#PDF_export_knots([K], "pdf/1zzzzzzpppp.pdf")
