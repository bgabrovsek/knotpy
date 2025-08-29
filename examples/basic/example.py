"""
=====================
Knot example
=====================

Compute the Jones polynomial of the trefoil knot.
"""

import knotpy as kp

k = kp.PlanarDiagram("3_1")
kp.draw(k, show=True)