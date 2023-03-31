from knotted import *
from crossing import *

link1 = Knotted(nodes = [
    Crossing([0,6,1,7], -1), #0
    Crossing([7,1,8,2], -1), #1
    Crossing([2,14,3,13], +1), #2
    Crossing([12,4,13,3], +1), #3
    Crossing([4,9,5,0], -1), #4
    Vertex([5,10,6], colors= [0,1,0], ins= [5]), #5
    Crossing([10,9,11,8], +1), #6
    Vertex([14,11,12], colors= [0,1,0], ins=[14,11]) #7
])


link1_without_bonds = Knotted(nodes = [
    Crossing([0,6,1,7], -1), #0
    Crossing([7,1,8,2], -1), #1
    Crossing([2,14,3,13], +1), #2
    Crossing([12,4,13,3], +1), #3
    Crossing([4,9,5,0], -1), #4
    Vertex([5,6], colors= [0,0], ins= [5]), #5
    #Crossing([10,9,11,8], +1), #6
    Vertex([8,9],colors= [0,0], ins=[8]),
    Vertex([14,12], colors= [0,0], ins=[14]) #7
])


tref_band_1 = Knotted(nodes = [
    Crossing([4,9,5,0], -1),
    Crossing([0,5,1,6], -1),
    Crossing([7,3,8,4],-1),
    Vertex([9,8,10], colors = [0,0,1], ins=[8,10]),
    Vertex([2,10,3], colors = [0,1,0], ins = [2]),
    Vertex([1,2,11], colors = [0,0,1], ins = [1]),
    Vertex([7,6,11], colors = [0,0,1], ins = [6,11])
])


tref_band_2 = Knotted(nodes = [
    Crossing([4,9,5,0], -1),
    Crossing([0,5,1,6], -1),
    Crossing([7,3,8,4],-1),
    Vertex([9,8,10], colors = [0,0,1], ins=[8,10]),
    Vertex([2,10,3], colors = [0,1,0], ins = [2]),
    Vertex([1,2,11], colors = [0,0,1], ins = [1]),
    Vertex([7,6,11], colors = [0,0,1], ins = [6,11])
])


tref_without_band = Knotted(nodes = [
    Crossing([4,9,5,0], -1),
    Crossing([0,5,1,6], -1),
    Crossing([7,3,8,4],-1),
    Vertex([9,8], colors = [0,0], ins=[8]),
    Vertex([2,3], colors = [0,0], ins = [2]),
    Vertex([1,2], colors = [0,0], ins = [1]),
    Vertex([7,6], colors = [0,0], ins = [6])
])


link_41a = Knotted(nodes = [
    Crossing([4,6,0,7],-1),
    Crossing([5,1,6,2], -1),
    Crossing([2,8,3,9],-1),
    Crossing([7,3,8,4],-1),
    Vertex([9,5], colors=[1,1], ins=[9]),
    Vertex([0,1], colors=[0,0], ins = [0])
])

link_41a_rev = Knotted(nodes = [
    Crossing([0,7,1,6], 1),
    Crossing([2,9,3,8], 1),
    Crossing([5,4,6,3], 1),
    Crossing([7,2,8,1], 1),
    Vertex([4,0], colors=[0,0], ins=[4]),
    Vertex([9,5], colors=[1,1], ins = [9])
])

hopf = Knotted(nodes = [Crossing([3,1,2,0], -1), Crossing([0,2,1,3], -1)])

tref = Knotted(nodes = [Crossing([0,4,1,3],1), Crossing([4,2,5,1],1), Crossing([2,0,3,5],1)])


TEST = [hopf, tref, link1, link1_without_bonds, tref_band_1, tref_band_2, tref_without_band, link_41a, link_41a_rev]


#print("Link 1                  :", alexander_polynomial(link1))
#print("Link 1 without bond 1   :", alexander_polynomial(link1_without_bonds))
#print("Trefoil with two bands 1:", alexander_polynomial(tref_band_1))
#print("Trefoil with two bands 2:", alexander_polynomial(tref_band_2))
#print("Trefoil without band    :", alexander_polynomial(tref_without_band))
#print("Link 41a                :", alexander_polynomial(link_41a))
#print("Link 41a (reversed)     :", alexander_polynomial(link_41a_rev))


