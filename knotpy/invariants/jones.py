# knotpy/invariants/jones.py
"""
The bracket polynomial ⟨·⟩ (also called the Kauffman bracket) is a polynomial invariant
of unoriented framed links.

See: L. H. Kauffman, *State models and the Jones polynomial*, Topology 26(3), 1987.
"""

from __future__ import annotations

__all__ = ["jones"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"



import sympy as sp

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.invariants.bracket import bracket
from knotpy.invariants._symbols import _A, _t, _x, _y, _z

def jones_from_homflypt(polynomial_xyz) -> sp.Expr:
    """Compute the Jones polynomial from the homflypt polynomial in variables xyz."""

    polynomial_xyz = sp.expand(
        polynomial_xyz.subs({_x: _t**-1, _y: -_t, _z: _t ** sp.Rational(1, 2) - _t ** sp.Rational(-1, 2)})
    )
    return polynomial_xyz



def jones(k: PlanarDiagram | OrientedPlanarDiagram) -> sp.Expr:
    r"""Compute the Jones polynomial via the normalized Kauffman bracket.

    The Kauffman bracket polynomial ⟨·⟩ is characterized by:

    .. math::

        \langle U \rangle &= 1, \quad \text{where $U$ is the unknot}, \\
        \langle L_\times \rangle &= A \, \langle L_0 \rangle \;+\; A^{-1} \, \langle L_\infty \rangle, \\
        \langle L \sqcup U \rangle &= \left(-A^2 - A^{-2}\right) \langle L \rangle.

    The Jones polynomial is obtained from the normalized bracket polynomial by the specialization:

    .. math::

        A = t^{-1/4}.

    Args:
        k: Planar diagram of a knot or link (oriented or unoriented).

    Returns:
        A SymPy expression in ``t`` representing the Jones polynomial.

    Notes:
        Alternative (equivalent) substitution in the \(l\)–\(m\) variables:
        :math:`l = i \, t^{-1}`, :math:`m = i \, (t^{-1/2} - t^{1/2})`.

    Examples:
        >>> import knotpy as kp
        >>> k = kp.knot("3_1")
        >>> kp.jones(k)
        -t**4 + t**3 + t
    """
    polynomial = bracket(k, normalize=True)

    # alternative: l = i * t^(−1),  m = i * (t^(−1/2) − t^(1/2))
    return sp.expand(polynomial.subs({_A: _t ** sp.Rational(-1, 4)}))


if __name__ == "__main__":
    pass
