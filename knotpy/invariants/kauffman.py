# knotpy/invariants/kauffman.py
r"""
The Kauffman 2-variable polynomial.

Definition:

.. math::

    F(K)(a, z) &= a^{-\mathrm{wr}(K)} \, L(K), \\
    F(\text{unknot}) &= 1, \\
    F(s^-) &= a \, F(s), \\
    F(s^+) &= a^{-1} \, F(s), \\
    L(\times) + L(\times) &= z \, L(+) + z \, L(-).

Personal notes:

F(k)(a,z) = a^-wr(K) * L(k)

L(O) = 1
L(s-) = a L(s)
L(s+) = a^-1 L(s)

L(X) + L(X) = z (X+) + z (X-)

If K is an oriented knot/link, and K* the mirror image, then
L(K*) = L(a^-1, z)
F(K*) = L(a^-1, z)
(this is wr(K*) = -wr(K)
F(K*) != L(K) when they are not isotopic

L(K # K') = L(K) * L(K')
L(K U K') = (z^-1 (a + a^-1) - 1) L(K) * L(K')
"""

from __future__ import annotations

__all__ = ["kauffman"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from collections import deque
import sympy as sp

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.reidemeister.simplify import simplify_decreasing
from knotpy.algorithms.remove import remove_unknots
from knotpy.invariants.homflypt import _choose_crossing_for_switching
from knotpy.algorithms.symmetry import mirror
from knotpy.invariants.skein import smoothen_crossing
from knotpy.invariants.writhe import writhe
from knotpy.algorithms.orientation import unorient
from knotpy.invariants._symbols import _a, _z, _KAUFFMAN_2_VARIABLE_SUM


def _compute_kauffman(k: PlanarDiagram) -> sp.Expr:
    stack = deque([k.copy(_coefficient=sp.Integer(1), _unknots=0)])
    polynomial = sp.Integer(0)

    while stack:
        k = stack.pop()
        k = simplify_decreasing(k, inplace=True)
        k.attr["_unknots"] += remove_unknots(k)

        k, crossing = _choose_crossing_for_switching(
            k, sum_coefficient=_KAUFFMAN_2_VARIABLE_SUM
        )

        if crossing is not None:
            k_switch = mirror(k, [crossing], inplace=False)
            k_smooth_A = smoothen_crossing(k, crossing, method="A", inplace=False)
            k_smooth_B = smoothen_crossing(k, crossing, method="B", inplace=False)

            k_switch.attr["_coefficient"] *= -1
            k_smooth_A.attr["_coefficient"] *= _z
            k_smooth_B.attr["_coefficient"] *= _z

            stack.append(k_switch)
            stack.append(k_smooth_A)
            stack.append(k_smooth_B)
        else:
            if len(k) == 0:
                polynomial += sp.expand(
                    k.attr["_coefficient"]
                    * (_a ** k.framing)
                    * _KAUFFMAN_2_VARIABLE_SUM ** (k.attr["_unknots"] - 1)
                )
            else:
                raise ValueError(
                    "Got a reduced HOMFLYPT polynomial state with vertices or crossings."
                )

    return polynomial


def kauffman(k: PlanarDiagram | OrientedPlanarDiagram) -> sp.Expr:
    original_knot = k
    k = unorient(k) if k.is_oriented() else k.copy()
    if not k.is_framed():
        k.framing = 0

    polynomial = _compute_kauffman(k)

    original_framing = original_knot.framing if original_knot.is_framed() else 0
    polynomial *= _a ** (writhe(original_knot) + original_framing)

    return sp.expand(polynomial)


if __name__ == "__main__":
    pass
