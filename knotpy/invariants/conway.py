__all__ = ['conway']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

from sympy import symbols, expand, Integer

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.invariants.homflypt import homflypt_xyz

from knotpy.invariants._symbols import _x, _y, _z

def conway(k: PlanarDiagram | OrientedPlanarDiagram):
    """Return the Alexander-Conway polynomial of a knot."""
    polynomial = homflypt_xyz(k)
    return expand(polynomial.subs({_x: Integer(1), _y: Integer(-1), _z: -_z}))

