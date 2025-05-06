"""
===============
Drawing example
===============

A short description of what the example does.
"""
import matplotlib.pyplot as plt

import knotpy as kp
###############################################################################
# Parsing knotpy notation
# -----------------------
#
# Load the knot from internal representation.
k = kp.PlanarDiagram("3_1")

###############################################################################
# Drawing the knot
# ----------------
# 
# Draw the know using matplotlib and show it.
kp.draw(k, with_title=True)
plt.show()