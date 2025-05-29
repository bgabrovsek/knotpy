"""

l * P(L+) + l^-1 * P(L-) + m * P(L0) = 0

or

P(L+) = - l^-2 * P(L-) - m/l * P(L0)
P(L-) = - l^2 * P(L-) - lm * P(L0)

There are three variations:
l-m: l * P(L+) + l^-1 * P(L-) + m * P(L0) = 0
v-z: v * P(L+) - v^-1 * P(L-) - z * P(L0) = 0
α-z: α^-1 * P(L+) - a * P(L-) - z * P(L0) = 0
xyz: x * P(L+) + y * P(L-) + z * P(L0) = 0

see
https://ncatlab.org/nlab/show/HOMFLY-PT+polynomial
and
https://en.wikipedia.org/wiki/HOMFLY_polynomial


"""
from sympy import symbols, Symbol, Integer, expand
from collections import deque

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.orientation import orient
from knotpy.reidemeister.simplify import reduce_crossings_greedy
from knotpy.manipulation.symmetry import mirror
from knotpy.algorithms.skein import smoothen_crossing
from knotpy._settings import settings
from knotpy.algorithms import sanity_check
from knotpy.algorithms.topology import loops, is_unlink

# possible homflypt variables
_V, _Z, _L, _M, _ALPHA, _X, _Y = symbols("v z l m α x y")

_SUM_LM = expand((-_L - _L ** -1) / _M)
_SUM_VZ = expand((_V - _V ** -1) / _Z)
_SUM_ALPHA_Z = expand((-_ALPHA + _ALPHA ** -1) / _Z)
_SUM_XYZ = expand((-_X - _Y) / _Z)

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
    polynomial = Integer(0)

    while stack:
        k = stack.pop()
        k = reduce_crossings_greedy(k, inplace=True)

        if k.crossings:
            # Get the shortest smallest face.
            face = min(k.faces, key=len)
            #print("face", face)

            if len(face) == 2:

                crossing = next(iter(face)).node  # get one of the crossings from the 2-gon

                k_switch = mirror(k, [crossing], inplace=False)  # switch the crossing sign
                k_smooth = smoothen_crossing(k, crossing, method="O", inplace=False)  # smoothen the crossing

                sanity_check(k_smooth)
                sanity_check(k_switch)

                # print("L=", k, "crossing", crossing)
                # print(" x", k_switch)
                # print(" o", k_smooth)
                # print()

                # P(L+) = - l^-2 * P(L-) - m/l * P(L0)
                # P(L-) = - l^2 * P(L-) - lm * P(L0)
                # k_switch.attr["_coefficient"] *= (- _L ** -2) if k.sign(crossing) > 0 else (- _L ** 2)
                # k_smooth.attr["_coefficient"] *= (- _L ** -1 * _M) if k.sign(crossing) > 0 else (- _L * _M)

                k_switch.attr["_coefficient"] *= (_V ** -2) if k.sign(crossing) > 0 else (_V ** 2)
                k_smooth.attr["_coefficient"] *= (_V ** -1 * _Z) if k.sign(crossing) > 0 else (- _V * _Z)

                stack.append(k_switch)
                stack.append(k_smooth)
            else:
                print("PASS face=",face)
                print("  ", k)
                pass
        else:
            if not is_unlink(k):
                raise ValueError(f"A HOMFLYPT polynomial state (without crossings) is not the unlink: {k}")
            polynomial += k.attr["_coefficient"] if len(k) == 1 else (_SUM_VZ ** (len(k) - 1) * k.attr["_coefficient"])  # "if" is redundant, but faster

    return polynomial

def homflypt_polynomial(k: PlanarDiagram | OrientedPlanarDiagram):

    """Return the HOMFLYPT polynomial of a knot k."""

    k = k.copy() if k.is_oriented() else orient(k)

    settings_dump = settings.dump()
    settings.update({"trace_moves": False, "allowed_moves": "r1,r2,r3", "framed": False})

    polynomial = _compute_homflypt(k)

    settings.load(settings_dump)

    return expand(polynomial)


if __name__ == '__main__':
    import knotpy as kp
    k = kp.from_knotpy_notation("b → X(c3 c2 c1 c0), c → X(b3 b2 b1 b0)")
    print(k)
    print(list(k.faces))
    print(min(k.faces, key=len))
    print(homflypt_polynomial(k))
    # o = orient(k)
    # print(homflypt_polynomial(o))