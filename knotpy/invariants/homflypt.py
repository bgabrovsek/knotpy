# knotpy/invariants/homflypt.py
"""
HOMFLY-PT polynomial in several normalizations.

Variations (skein relations):

- l–m:   ``l·P(L+) + l⁻¹·P(L−) + m·P(L₀) = 0``
- v–z:   ``v⁻¹·P(L+) − v·P(L−) − z·P(L₀) = 0``
- A–z:   ``A·P(L+) − A⁻¹·P(L−) − z·P(L₀) = 0``
- x–y–z: ``x·P(L+) + y·P(L−) + z·P(L₀) = 0``

References:
- https://ncatlab.org/nlab/show/HOMFLY-PT+polynomial
- https://en.wikipedia.org/wiki/HOMFLY_polynomial
"""

from __future__ import annotations

__all__ = ["homflypt"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from collections import OrderedDict, deque
from random import choice

import sympy as sp

from knotpy._settings import settings
from knotpy.algorithms.alternating import is_face_alternating
from knotpy.algorithms.canonical import canonical
from knotpy.algorithms.orientation import orient
from knotpy.algorithms.remove import remove_unknots
from knotpy.invariants.skein import smoothen_crossing
from knotpy.algorithms.symmetry import mirror
from knotpy.classes.freezing import freeze
from knotpy.classes.planardiagram import OrientedPlanarDiagram, PlanarDiagram
from knotpy.reidemeister.reidemeister_3 import find_reidemeister_3_triangle, reidemeister_3
from knotpy.reidemeister.simplify import simplify_decreasing, simplify_non_increasing
from knotpy.utils.set_utils import LeveledSet
#from knotpy.tables.knot import knot_precomputed_homflypt

from knotpy.invariants._symbols import _A, _a, _l, _m, _v, _x, _y, _z, _HOMFLYPT_SUM_XYZ, _tmp


_USE_HOMFLYPT_PRECACHE = False
_homflypt_xyz_precache: "OrderedDict[object, sp.Expr]" = OrderedDict()


def _simplify_to_2_face(k: PlanarDiagram) -> PlanarDiagram | None:
    """Perform R3 moves until there is a 2-face available; return the resulting diagram or ``None``."""
    if "R3" not in settings.allowed_moves:
        return k
    ls = LeveledSet(freeze(canonical(k)))
    while ls[-1]:
        ls.new_level()
        for k in ls[-2]:
            for location in find_reidemeister_3_triangle(k):
                k_r3 = reidemeister_3(k, location, inplace=False)
                if any(len(f) == 2 for f in k_r3.faces):
                    return k_r3
                ls.add(freeze(canonical(k_r3)))
    return None


def _choose_crossing_for_switching(
    k: OrientedPlanarDiagram, sum_coefficient: sp.Expr
) -> tuple[OrientedPlanarDiagram, object | None]:
    """Choose a crossing for skein expansion that tends to simplify after switching.

    Returns:
        A pair ``(diagram, crossing_or_none)``. If no crossing is chosen, the diagram should be terminal.
    """
    if not k.crossings:
        return k, None

    faces = list(k.faces)

    if any(len(face) == 1 for face in faces):
        raise RuntimeError(
            f"There exists a kink after simplification, which should not happen: {k}."
        )

    faces2 = [face for face in faces if len(face) == 2]
    if faces2:
        return k, faces2[0][0].node

    faces3 = [face for face in faces if len(face) == 3]
    if faces3:
        non_alt_faces = [face for face in faces3 if not is_face_alternating(face)]
        if non_alt_faces:
            ls = LeveledSet(freeze(canonical(k)))
            while not ls.is_level_empty(-1):
                ls.new_level()
                for k_ in ls.iter_level(-2):
                    for location in find_reidemeister_3_triangle(k_):
                        k_r3 = reidemeister_3(k_, location, inplace=False)
                        num_nodes = len(k_r3)
                        k_r3_ = simplify_non_increasing(k_r3, greediness=3)
                        if len(k_r3_) < num_nodes or any(
                            len(f) == 2 for f in k_r3_.faces
                        ):
                            k_r3_.attr["_coefficient"] *= sum_coefficient ** remove_unknots(k_r3_)
                            if len(k_r3_.crossings) == 0:
                                return k_r3_, None
                            # Not optimal to recurse, but keeps logic simple
                            return _choose_crossing_for_switching(
                                k_r3_, sum_coefficient=_HOMFLYPT_SUM_XYZ
                            )
                        ls.add(freeze(canonical(k_r3)))

        alt_faces = [face for face in faces3 if is_face_alternating(face)]
        if alt_faces:
            face_3_crossings = [
                c
                for face in alt_faces
                for c in [face[0].node, face[1].node, face[2].node]
            ]
            return k, choice(list(face_3_crossings))

    raise RuntimeError(
        f"There are no 3-faces in the diagram {k} (contradiction with Euler characteristic)."
    )


def _compute_homflypt(k: OrientedPlanarDiagram) -> sp.Expr:
    """Compute the HOMFLY-PT polynomial in variables ``x, y, z`` for an oriented diagram."""
    stack: deque[OrientedPlanarDiagram] = deque([k.copy(_coefficient=sp.Integer(1))])
    polynomial = sp.Integer(0)

    while stack:
        k = stack.pop()
        k = simplify_decreasing(k, inplace=True)
        k.attr["_coefficient"] *= _HOMFLYPT_SUM_XYZ ** remove_unknots(k)

        k, crossing = _choose_crossing_for_switching(
            k, sum_coefficient=_HOMFLYPT_SUM_XYZ
        )

        if crossing is not None:
            k_switch = mirror(k, [crossing], inplace=False)
            k_smooth = smoothen_crossing(k, crossing, method="O", inplace=False)

            if k.sign(crossing) > 0:
                k_switch.attr["_coefficient"] *= (-_y * _x ** -1)
                k_smooth.attr["_coefficient"] *= (-_z * _x ** -1)
            else:
                k_switch.attr["_coefficient"] *= (-_x * _y ** -1)
                k_smooth.attr["_coefficient"] *= (-_z * _y ** -1)

            stack.append(k_switch)
            stack.append(k_smooth)
        else:
            if len(k) == 0:
                polynomial += k.attr["_coefficient"] / _HOMFLYPT_SUM_XYZ
            else:
                raise ValueError(
                    "Reduced HOMFLY-PT state has vertices or crossings unexpectedly."
                )

    return polynomial


def _homflypt_xyz(k: PlanarDiagram | OrientedPlanarDiagram) -> sp.Expr:
    """Return the HOMFLY-PT polynomial in variables ``x, y, z``, satisfying ``xP(L+) + yP(L−) + zP(L₀) = 0``."""
    if _USE_HOMFLYPT_PRECACHE and k in _homflypt_xyz_precache:
        return _homflypt_xyz_precache[k]

    k_original = k
    k = k.copy() if k.is_oriented() else orient(k)

    settings_dump = settings.dump()
    settings.update({"trace_moves": False, "allowed_moves": "r1,r2,r3", "framed": False})
    polynomial = sp.expand(_compute_homflypt(k))
    settings.load(settings_dump)

    if _USE_HOMFLYPT_PRECACHE:
        _homflypt_xyz_precache[freeze(k_original, inplace=False)] = polynomial
        if len(_homflypt_xyz_precache) > 16:
            _homflypt_xyz_precache.popitem(last=False)

    return polynomial

def homflypt(k: PlanarDiagram | OrientedPlanarDiagram, variables: str="vz") -> sp.Expr:
    r"""Compute the HOMFLY–PT polynomial.

    This version satisfies the skein relation

    .. math::

        x\,P(L_+) + y\,P(L_-) + z\,P(L_0) \;=\; 0.
 .. math::

        \ell\,P(L_+) + \ell^{-1}\,P(L_-) + m\,P(L_0) \;=\; 0.

    .. math::

        v^{-1}\,P(L_+) - v\,P(L_-) - z\,P(L_0) \;=\; 0.


    .. math::

        A\,P(L_+) - A^{-1}\,P(L_-) - z\,P(L_0) \;=\; 0.

    If the diagram is not oriented, it is oriented automatically.

    Args:
        k: The input knot or link diagram (oriented or unoriented).

    Returns:
        sympy.Expr: The HOMFLY–PT polynomial \(P\) in variables \(x, y, z\).

    Raises:
        ValueError: If a reduced terminal state contains unexpected vertices/crossings.

    Examples:
        >>> import knotpy as kp
        >>> k = kp.knot("3_1")
        >>> kp.homflypt(k)
        -v**4 + v**2*z**2 + 2*v**2
        >>> kp.homflypt(k, variables="lm")
        m**2/l**2 - 2/l**2 - 1/l**4
        >>> kp.homflypt(k, variables="az")
        z**2/A**2 + 2/A**2 - 1/A**4
        >>> kp.homflypt(k, variables="xyz")
        -2*y/x - y**2/x**2 + z**2/x**2
    """

    from knotpy.tables.knot import knot_precomputed_homflypt

    variables = str(variables).lower()

    # try to get the HOMFLYPT polynomial from the precomputed data
    polynomial = knot_precomputed_homflypt(k)
    # otherwise, compute it
    if polynomial is None:
        polynomial = _homflypt_xyz(k)

    if "x" in variables and "y" in variables and "z" in variables:
        return polynomial
    if "v" in variables and "z" in variables:
        return _xyz_to_vz(polynomial)
    if "l" in variables and "m" in variables:
        return _xyz_to_lm(polynomial)
    if "a" in variables and "z" in variables:
        return _xyz_to_az(polynomial)
    raise ValueError(f"Invalid variable choice: {variables}")

def _homflypt_xyz_mirror(polynomial: sp.Expr) -> sp.Expr:
    return sp.expand(polynomial.xreplace({_x: _tmp, _y: _x}).xreplace({_tmp: _y}))

def _xyz_to_lm(polynomial: sp.Expr) -> sp.Expr:
    return sp.expand(polynomial.subs({_x: _l, _y: _l ** -1, _z: _m}))

def _xyz_to_vz(polynomial: sp.Expr) -> sp.Expr:
    return sp.expand(polynomial.subs({_x: _v ** -1, _y: -_v, _z: -_z}))

def _xyz_to_az(polynomial: sp.Expr) -> sp.Expr:
    return sp.expand(polynomial.subs({_x: _a, _y: -_a ** -1, _z: -_z}))

if __name__ == "__main__":
    pass
