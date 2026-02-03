"""
=====================
Knot example
=====================

Draw the diagram of the trefoil knot (oriented/non-oriented)
"""

import knotpy as kp

k = kp.knot("3_1")
kp.draw(k, show=True)

k = kp.knot("+3_1")
kp.draw(k, show=True)