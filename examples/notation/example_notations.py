"""Test various knot/graph notations."""

import knotpy as kp
from knotpy.generate.example import example_spatial_graph


print("PD notation\n")

# Mathematica format
text = "X[1,9,2,8], X[3,10,4,11], X[5,3,6,2], X[7,1,8,12], X[9,4,10,5], X[11,7,12,6]"
print("In:", text)
print("Out:", k := kp.from_pd_notation(text))
print("Out:", kp.to_pd_notation(k))

print()

# KnotInfo notation
text = "[[4,2,5,1],[8,6,1,5],[6,3,7,4],[2,7,3,8]]"
print("In:", text)
print("Out:", k := kp.from_pd_notation(text))
print("Out:", kp.to_pd_notation(k))

print()

# Topoly notation
text = "V[12,14,5],V[14,13,2],X[11,10,13,12],X[7,11,5,6],X[10,7,6,2]"
print("In:", text)
print("Out:", k := kp.from_pd_notation(text))
print("Out:", kp.to_pd_notation(k))

print("\nEM notation\n")

text = "b0e1,a0c0d0,b1d1,b2c1e0,d2a1"
print("In:", text)
print("Out:", k := kp.from_condensed_em_notation(text))
print("Out:", kp.to_condensed_em_notation(k))

print("\nKnot notation\n")

k = example_spatial_graph()
print("In:", k)
print("Out:", text := kp.to_knot_notation(k))
print("Out:", kp.to_knot_notation(k, attributes=False))
# print("Out:", kp.from_knot_notation(text))

