"""
=====================
Knot example
=====================

Print the diagram of the trefoil knot (oriented/non-oriented)
"""

import knotpy as kp

k = kp.knot("3_1")
print(k)

k = kp.knot("+3_1")
print(k)