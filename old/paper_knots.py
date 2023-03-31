from knotted import *
from HOMFLYPT import HSM
from drawknot import *
from sympy import expand

Trefoil_1 = Knotted(nodes=[
    Crossing([0,5,1,4],1), Crossing([6,3,7,2],1), Crossing([3,0,4,7],1),
    Vertex([5,6,8], ingoingB=[1,0,1], colors=[0,0,1]),
    Vertex([2,1,8], ingoingB=[0,1,0], colors=[0,0,1])], name="tref1")


Trefoil_2 = Knotted(nodes=[
    Crossing([0,8,1,7],1), Crossing([6,0,7,4],1), Crossing([3,6,4,5],1),
    Vertex([3,2,8], ingoingB=[0,1,1], colors=[0,0,1]),
    Vertex([1,2,5], ingoingB=[1,0,0], colors=[0,0,1])], name="tref2")

CN29 = Knotted(nodes=[
    Crossing([2,8,3,9],-1), Crossing([7,1,8,2],-1), Crossing([4,0,5,11],1),
Vertex([0,1,14], ingoingB=[1,0,0], colors=[0,0,1]),
Vertex([7,6,14], ingoingB=[0,1,1], colors=[0,0,1]),
Vertex([11,10,12], ingoingB=[0,1,0], colors=[0,0,1]),
Vertex([3,4,12], ingoingB=[1,0,1], colors=[0,0,1]),
Vertex([9,10,13], ingoingB=[1,0,0], colors=[0,0,1]),
Vertex([5,6,13], ingoingB=[1,0,1], colors=[0,0,1])], name="cn29 ")


adwx = Knotted(nodes=[
    Crossing([3,10,4,9],1), Crossing([4,12,5,11],1),
Vertex([6,5,8], ingoingB=[0,1,0], colors=[0,0,1]),
Vertex([1,0,8], ingoingB=[0,1,1], colors=[0,0,1]),
Vertex([7,0,9], ingoingB=[1,0,0], colors=[0,0,1]),
Vertex([3,2,10], ingoingB=[0,1,1], colors=[0,0,1]),
Vertex([6,7,11], ingoingB=[1,0,0], colors=[0,0,1]),
Vertex([2,1,12], ingoingB=[0,1,1], colors=[0,0,1])], name="adwx ")


kren = Knotted(nodes=[
    Crossing([7,10,8,9],1),
Vertex([0,1,6], ingoingB=[1,0,1], colors=[0,0,1]),
Vertex([1,2,6], ingoingB=[1,0,0], colors=[0,0,1]),
Vertex([2,3,9], ingoingB=[1,0,0], colors=[0,0,1]),
Vertex([4,5,10], ingoingB=[1,0,1], colors=[0,0,1]),
Vertex([3,4,7], ingoingB=[1,0,0], colors=[0,0,1]),
Vertex([5,0,8], ingoingB=[1,0,1], colors=[0,0,1])], name = "kren ")


kren2 = Knotted(nodes=[
    Crossing([9,7,10,8],-1),
Vertex([0,1,6], ingoingB=[1,0,1], colors=[0,0,1]),
Vertex([1,2,6], ingoingB=[1,0,0], colors=[0,0,1]),
Vertex([2,3,9], ingoingB=[1,0,0], colors=[0,0,1]),
Vertex([4,5,10], ingoingB=[1,0,1], colors=[0,0,1]),
Vertex([3,4,7], ingoingB=[1,0,0], colors=[0,0,1]),
Vertex([5,0,8], ingoingB=[1,0,1], colors=[0,0,1])], name = "kren2")

thet = Knotted(nodes=[
    Vertex([0,1,2], ingoingB=[1,0,0], colors=[0,0,1]),
Vertex([1,0,2], ingoingB=[1,0,1], colors=[0,0,1])], name="th   ")


thetatheta = Knotted(nodes=[
    Crossing([6,1,7,0],1), Crossing([8,2,9,3],-1), Crossing([10,2,11,1],1),
    Vertex([0,4,5], ingoingB=[0,1,1], colors=[0,0,1]), Vertex([4,3,5], ingoingB=[0,1,0], colors=[0,0,1]),
    Vertex([6,9,10], ingoingB=[0,1,0], colors=[0,0,1]), Vertex([8,7,11], ingoingB=[0,1,1], colors=[0,0,1])
    ], name="thth ")

thetathetax = Knotted(nodes=[
    Crossing([6,1,7,0],1), Crossing([8,2,9,3],-1), Crossing([1,10,2,11],-1),
    Vertex([0,4,5], ingoingB=[0,1,1], colors=[0,0,1]), Vertex([4,3,5], ingoingB=[0,1,0], colors=[0,0,1]),
    Vertex([6,9,10], ingoingB=[0,1,0], colors=[0,0,1]), Vertex([8,7,11], ingoingB=[0,1,1], colors=[0,0,1])
    ],name="ththx")

xknot  = Knotted(nodes=[
Vertex([0,1,4], ingoingB=[1,0,0], colors=[0,0,1]),
Vertex([2,3,6], ingoingB=[1,0,1], colors=[0,0,1]),
Vertex([3,0,7], ingoingB=[1,0,1], colors=[0,0,1]),
Vertex([1,2,5], ingoingB=[1,0,0], colors=[0,0,1]),
    Crossing([5,6,7,4],1)
    ], name="xknot")


xknot2  = Knotted(nodes=[
Vertex([0,1,4], ingoingB=[1,0,0], colors=[0,0,1]),
Vertex([1,2,4], ingoingB=[1,0,1], colors=[0,0,1]),
Vertex([2,3,5], ingoingB=[1,0,0], colors=[0,0,1]),
Vertex([3,0,5], ingoingB=[1,0,1], colors=[0,0,1]),
    ],name="xkn2 ")

knots = [Trefoil_1, Trefoil_2, CN29, adwx, kren, kren2, thetatheta, thetathetax, xknot, xknot2]



PDF_export_knots(knots,"pdf\proteins.pdf")

print("\nNON-RIGID COLORED\n")

for k in knots:
    colorize_bonds_by_minimal_distance(k)
    print(k.name,str(HSM(k)).replace("**","^"))

print("\nNON-RIGID COLORED REFINED\n")

for k in knots:
    colorize_bonds_by_minimal_distance(k)
    print(k.name,str(HSM(k, refined=True)).replace("**","^"))

print("\nNON-RIGID\n")

for k in knots:
    print(k.name,str(HSM(k)).replace("**","^"))

print("\nRIGID\n")

for k in knots:
    print(k.name,str(expand(HSM(k, rigid=True))).replace("**","^"))


print("\nREFINED\n")

for k in knots:
    print(k.name,str(HSM(k, refined=True)).replace("**","^"))

print("\nREFINED RIGID\n")

for k in knots:
    print(k.name,str(HSM(k, rigid=True, refined=True)).replace("**","^"))



# Vertex([], ingoingB=[0,0,0], colors=[0,0,1]),