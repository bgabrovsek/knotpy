"""
===============
Drawing example
===============

A short description of what the example does.
"""
from knotpy.drawing.draw_matplotlib import draw
from knotpy.notation.native import from_knotpy_notation
import matplotlib.pyplot as plt

###############################################################################
# Parsing knotpy notation
# -----------------------
#
# Load the knot from internal representation.
s = "('OrientedSpatialGraph', {'name': 't0_1(0).0'}, [('Vertex', 'a', (('OutgoingEndpoint', 'b', 0, {'color': 1}), ('OutgoingEndpoint', 'b', 2, {}), ('OutgoingEndpoint', 'b', 1, {})), {}), ('Vertex', 'b', (('IngoingEndpoint', 'a', 0, {'color': 1}), ('IngoingEndpoint', 'a', 2, {}), ('IngoingEndpoint', 'a', 1, {})), {})])"
k = from_knotpy_notation(s)

###############################################################################
# Perform some operations on the knot.
k.permute_node("a", {0:1,1:2,2:0})

###############################################################################
# Drawing the knot
# ----------------
# 
# Draw the know using matplotlib and show it.
draw(k, draw_circles=True, with_labels=True, with_title=True)
plt.show()