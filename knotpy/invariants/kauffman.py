"""

The Kauffman 2-variable polynomial.
"""

from sympy import Expr, expand, Integer, symbols, Symbol
from collections import deque

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram

_A = symbols("A")
_kauffman_term = -_A ** 2 - _A ** (-2)


def kauffman_polynomial(k: PlanarDiagram | OrientedPlanarDiagram) -> Expr:
    pass
