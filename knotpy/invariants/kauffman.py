"""

The Kauffman 2-variable polynomial.

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
L(K U K') = (z^-1 (a + a^-1) -1) L(K) * L(K')


"""

__all__ = ['kauffman']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

from sympy import Expr, expand, Integer
from collections import deque

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.reidemeister.simplify import simplify_decreasing
from knotpy.algorithms.remove import remove_unknots
from knotpy.invariants.homflypt import _choose_crossing_for_switching
from knotpy.algorithms.symmetry import mirror
from knotpy.algorithms.skein import smoothen_crossing
from knotpy.invariants.writhe import writhe
from knotpy.algorithms.orientation import unorient


from knotpy.invariants._symbols import _a, _z, _KAUFFMAN_2_VARIABLE_SUM


def _compute_kauffman(k: PlanarDiagram) -> Expr:

    stack = deque([k.copy(_coefficient=Integer(1), _unknots=0)])
    polynomial = Integer(0)

    while stack:
        k = stack.pop()

        # if "y" in str(k.attr["_coefficient"]):
        #     raise ValueError(f"Got a y coefficient in the Kauffman polynomial for {k_switch}")


        k = simplify_decreasing(k, inplace=True)


        # if "y" in str(k.attr["_coefficient"]):
        #     raise ValueError(f"Got a y coefficient in the Kauffman polynomial for {k_switch}")


        k.attr["_unknots"] += remove_unknots(k)

        # if "y" in str(k.attr["_coefficient"]):
        #     raise ValueError(f"Got a y coefficient in the Kauffman polynomial for {k_switch}")

        k, crossing = _choose_crossing_for_switching(k, sum_coefficient=_KAUFFMAN_2_VARIABLE_SUM)

        # if "y" in str(k.attr["_coefficient"]):
        #     print("BAD", k.attr["_coefficient"])
        #     raise ValueError(f"Got a y coefficient in the Kauffman polynomial for {k_switch}")

        if crossing is not None:
            k_switch = mirror(k, [crossing], inplace=False)  # switch the crossing sign
            k_smooth_A= smoothen_crossing(k, crossing, method="A", inplace=False)  # smoothen the crossing
            k_smooth_B = smoothen_crossing(k, crossing, method="B", inplace=False)  # smoothen the crossing

            # if "y" in str(k_switch.attr["_coefficient"]):
            #     raise ValueError(f"Got a y coefficient in the Kauffman polynomial for {k_switch}")
            #
            # if "y" in str(k_smooth_A.attr["_coefficient"]):
            #     raise ValueError(f"Got a y coefficient in the Kauffman polynomial for {k_switch}")
            #
            # if "y" in str(k_smooth_B.attr["_coefficient"]):
            #     raise ValueError(f"Got a y coefficient in the Kauffman polynomial for {k_switch}")

            k_switch.attr["_coefficient"] *= -1
            k_smooth_A.attr["_coefficient"] *= _z
            k_smooth_B.attr["_coefficient"] *= _z

            # if "y" in str(k_switch.attr["_coefficient"]):
            #     raise ValueError(f"Got a y coefficient in the Kauffman polynomial for {k_switch}")
            #
            # if "y" in str(k_smooth_A.attr["_coefficient"]):
            #     raise ValueError(f"Got a y coefficient in the Kauffman polynomial for {k_switch}")
            #
            # if "y" in str(k_smooth_B.attr["_coefficient"]):
            #     raise ValueError(f"Got a y coefficient in the Kauffman polynomial for {k_switch}")

            stack.append(k_switch)
            stack.append(k_smooth_A)
            stack.append(k_smooth_B)
        else:
            if len(k) == 0:
                polynomial += expand(k.attr["_coefficient"] * (_a ** k.framing) * _KAUFFMAN_2_VARIABLE_SUM ** (k.attr["_unknots"] - 1))
            else:
                raise ValueError(f"Got a reduced HOMFLYPT polynomial state with vertices or crossings.")


    return polynomial

def kauffman(k: PlanarDiagram | OrientedPlanarDiagram) -> Expr:

    original_knot = k
    k = unorient(k) if k.is_oriented() else k.copy()
    if not k.is_framed():
        k.framing = 0

    polynomial = _compute_kauffman(k)

    original_framing = original_knot.framing if original_knot.is_framed() else 0

    polynomial *= _a ** (writhe(original_knot) + original_framing)  # ignore framing if normalized

    return expand(polynomial)


if __name__ == '__main__':
    import knotpy as kp
    k = kp.knot("3_1")
    print(kauffman(k))
    k = kp.mirror(kp.knot("3_1"))
    print(kauffman(k))


"""
2*a**6 - a**5/z + 2*a**4 - a**4/(a**2 - a*z + 1) + a**3/(a**2/z - a + 1/z) - a**3/z - a**2/(a**2 - a*z + 1)


z**2/a**2 - 2/a**2 + z/a**3 + z**2/a**4 - 1/a**4 + z/a**5
a**2*z**2 - a**2 + a*z**3 - a*z + 2*z**2 - 1 + z**3/a - z/a + z**2/a**2 - 1/a**2
z**4/a**4 - 4*z**2/a**4 + 3/a**4 + z**3/a**5 - 2*z/a**5 + z**4/a**6 - 3*z**2/a**6 + 2/a**6 + z**3/a**7 - z/a**7 + z**2/a**8 + z/a**9
z**2/a**2 - 1/a**2 + z**3/a**3 + z**4/a**4 - z**2/a**4 + a**(-4) + 2*z**3/a**5 - 2*z/a**5 + z**4/a**6 - 2*z**2/a**6 + a**(-6) + z**3/a**7 - 2*z/a**7

"""