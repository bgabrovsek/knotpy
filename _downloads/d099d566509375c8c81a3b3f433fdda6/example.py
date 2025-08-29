"""
=====================
Knot example
=====================

Draw the trefoil knot.
"""

import knotpy as kp

k = kp.knot("+3_1")
kp.draw(k, show=True)