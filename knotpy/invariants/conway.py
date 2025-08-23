"""
Alexander–Conway polynomial via HOMFLY-PT specialization.
"""

__all__ = ["conway"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from statistics import variance

import sympy as sp

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.invariants.homflypt import homflypt
from knotpy.invariants._symbols import _x, _y, _z


def conway(k: PlanarDiagram | OrientedPlanarDiagram) -> sp.Expr:
    """Return the Alexander–Conway polynomial of a knot or link.

    This uses the HOMFLY-PT specialization with your convention::

        x = 1
        y = -1
        z → -z

    Args:
        k: Planar diagram (oriented or unoriented).

    Returns:
        SymPy expression in ``z`` representing the Conway polynomial.
    """
    polynomial = homflypt(k, variables="xyz")
    return sp.expand(
        polynomial.subs({_x: sp.Integer(1), _y: sp.Integer(-1), _z: -_z})
    )


if __name__ == "__main__":
    pass
