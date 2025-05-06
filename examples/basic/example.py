"""
=====================
Knot example
=====================

Compute the Jones polynomial of the trefoil knot.
"""

import knotpy as kp

k = kp.PlanarDiagram("3_1")
print("Jones polynomial:", kp.jones_polynomial(k))