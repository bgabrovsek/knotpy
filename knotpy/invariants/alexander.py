
from sympy import symbols, expand, Rational, Integer

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.invariants.homflypt import homflypt_polynomial_xyz

_T, _X, _Y, _Z = symbols("t x y z")

def alexander_polynomial(k: PlanarDiagram | OrientedPlanarDiagram):
    """Return the Alexander polynomial of a knot."""
    polynomial = homflypt_polynomial_xyz(k)
    return expand(polynomial.subs({_X: Integer(1), _Y: Integer(-1), _Z: -_T ** Rational(1, 2) + _T ** Rational(-1, 2)}))

