"""

l * P(L+) + l^-1 * P(L-) + m * P(L0) = 0

or

P(L+) = - l^-2 * P(L-) - m/l * P(L0)
P(L-) = - l^2 * P(L-) - lm * P(L0)


"""
from sympy import symbols, Symbol, Integer, expand
from collections import deque

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.orientation import orient
from knotpy.reidemeister.simplify import reduce_crossings_greedy
from knotpy.manipulation.symmetry import mirror
from knotpy.algorithms.skein import smoothen_crossing
from knotpy import settings
from sandbox.knotpy.algorithms import sanity_check

_L, _M = symbols(("l", "m"))

def _min_len_item(f: list):
    if not f:
        raise ValueError("Cannot find minimum length item in empty list")
    min_len = min(len(_) for _ in f)
    for _ in f:
        if len(_) == min_len:
            return _
    return None


def _compute_homflypt(k: OrientedPlanarDiagram):

    stack = deque([k.copy(_coefficient=Integer(1))])

    while stack:
        k = stack.pop()
        k = reduce_crossings_greedy(k, inplace=True)

        if k.crossings:
            # Get the shortest smallest face.
            face = min(k.faces, key=len)
            print("face", face)

            if len(face) == 2:

                crossing = next(iter(face)).node  # get one of the crossings from the 2-gon

                k_switch = mirror(k, [crossing], inplace=False)  # switch the crossing sign
                k_smooth = smoothen_crossing(k, crossing, method="O", inplace=False)  # smoothen the crossing

                sanity_check(k_smooth)
                sanity_check(k_switch)

                print("L=", k, "crossing", crossing)
                print(" x", k_switch)
                print(" o", k_smooth)
                print()

                # P(L+) = - l^-2 * P(L-) - m/l * P(L0)
                # P(L-) = - l^2 * P(L-) - lm * P(L0)
                k_switch.attr["_coefficient"] *= (- _L ** -2) if k.sign(crossing) > 0 else (- _L ** 2)
                k_smooth.attr["_coefficient"] *= (- _L ** -1 * _M) if k.sign(crossing) > 0 else (- _L * _M)

                stack.append(k_switch)
                stack.append(k_smooth)
            else:
                pass
        else:
            pass

    pass

def homflypt_polynomial(k: PlanarDiagram | OrientedPlanarDiagram):

    """Return the HOMFLYPT polynomial of a knot k."""

    k = k.copy() if k.is_oriented() else orient(k)

    settings_dump = settings.dump()
    settings.update({"trace_moves": False, "allowed_moves": "r1,r2,r3", "framed": False})

    polynomial = _compute_homflypt(k)

    settings.load(settings_dump)

    return polynomial


if __name__ == '__main__':
    import knotpy as kp
    k = kp.PlanarDiagram("3_1")
    print(k)
    o = orient(k)
    homflypt_polynomial(o)