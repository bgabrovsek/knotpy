"""
There are three variations:
l-m: l * P(L+) + l^-1 * P(L-) + m * P(L0) = 0
v-z: v^-1 * P(L+) - v * P(L-) - z * P(L0) = 0
α-z: α * P(L+) - a^-1 * P(L-) - z * P(L0) = 0
xyz: x * P(L+) + y * P(L-) + z * P(L0) = 0


https://ncatlab.org/nlab/show/HOMFLY-PT+polynomial
and
https://en.wikipedia.org/wiki/HOMFLY_polynomial


"""
from sympy import symbols, Symbol, Integer, expand
from collections import deque

from knotpy.algorithms.alternating import alternating_crossings
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.orientation import orient
from knotpy.reidemeister.simplify import simplify_greedy_decreasing
from knotpy.manipulation.symmetry import mirror
from knotpy.algorithms.skein import smoothen_crossing
from knotpy._settings import settings
from knotpy.algorithms import sanity_check
from knotpy.algorithms.topology import loops, is_unlink
from knotpy.manipulation.remove import remove_unknots
from knotpy.algorithms.alternating import alternating_crossings, is_face_alternating
from random import choice
from knotpy.reidemeister.simplify import fast_simplification_greedy
from knotpy.utils.set_utils import LeveledSet
from knotpy.classes.freezing import freeze, unfreeze
from knotpy.algorithms.canonical import canonical
from knotpy.reidemeister.reidemeister_3 import reidemeister_3, find_reidemeister_3_triangle

_V, _Z, _L, _M, _A, _X, _Y = symbols("v z l m a x y")  # all possible HOMFLYPT variables
_SUM_XYZ = expand((-_X - _Y) / _Z)  # P(A u B) = ((-_X - _Y) / _Z) P(A) * P(B)

def _min_len_item(f: list):
    if not f:
        raise ValueError("Cannot find minimum length item in empty list")
    min_len = min(len(_) for _ in f)
    for _ in f:
        if len(_) == min_len:
            return _
    return None

def simplify_to_2_face(k: PlanarDiagram):
    """Perform R3 until there is a 2-face available."""
    # if R3 moves are not allowed, we cannot do further simplifications
    if "R3" not in settings.allowed_moves:
        return k
    ls =LeveledSet(freeze(canonical(k)))  # assume k has no 2-face
    while ls[-1]:
        # Put diagrams after an R3 to the next level.
        ls.new_level()
        for k in ls[-2]:
            for location in find_reidemeister_3_triangle(k):
                k_r3 = reidemeister_3(k, location, inplace=False)
                if any(len(f)==2 for f in k_r3.faces):
                    return k_r3
                ls.add(freeze(canonical(k_r3)))

    return None

def _choose_crossing_for_switching(k: OrientedPlanarDiagram):
    """Choose the best crossing to perform the skein relation, so the diagram simplifies after the crossing switch."""
    if not k.crossings:
        return k, None
    faces = list(k.faces)

    # Are there any faces of length 1?
    if [face for face in faces if len(face) == 1]:
        raise RuntimeError(f"There exists a kink after simplification, which should not happen {k}.")

    # Are there any faces of length 2?
    if faces2 := [face for face in faces if len(face) == 2]:
        return k, faces2[0][0].node

    # Are there any faces of length 3?
    if faces3 := [face for face in faces if len(face) == 3]:
        non_alt_faces = [face for face in faces3 if not is_face_alternating(face)]

        # if there are non-alternating faces, make r3 moves and try to make a R2 face via R-moves
        if non_alt_faces:
            # Try to simplify the diagram so that we have a good crossing to make a skein move on.
            ls = LeveledSet(freeze(canonical(k)))
            while ls[-1]:
                # Put diagrams after removing kinks and unpokes to the next level.
                ls.new_level()
                for k_ in ls[-2]:
                    for location in find_reidemeister_3_triangle(k_):

                        k_r3 = reidemeister_3(k_, location, inplace=False)
                        sanity_check(k_r3)
                        num_nodes = len(k_r3)
                        k_r3_ = fast_simplification_greedy(k)
                        if len(k_r3_) < num_nodes or any(len(f) == 2 for f in k_r3_.faces):
                            k_r3_.attr["_coefficient"] *= _SUM_XYZ ** remove_unknots(k_r3_)
                            if len(k_r3_.crossings) == 0:
                                return k_r3_, None
                            return _choose_crossing_for_switching(k_r3_)  #TODO: it is not optimal to call the function again
                        ls.add(freeze(canonical(k_r3)))

        # If no good non-alternating 3-faces found, make an alternating 3-face a non-alternating one
        if alt_faces := [face for face in faces3 if is_face_alternating(face)]:
            face_3_crossings = [c for face in alt_faces for c in [face[0].node, face[1].node, face[2].node]]
            cr_ch = choice(list(face_3_crossings))

            return k, cr_ch  # todo: sometimes this takes long, why?

    raise RuntimeError(f"There are no 3-faces in the diagram {k}")  # A contradiction due to Euler's characteristic.


def _compute_homflypt(k: OrientedPlanarDiagram):
    """ Compute the HOMFLYPT polynomial in variables x,y,z of a knot k."""

    stack = deque([k.copy(_coefficient=Integer(1))])
    polynomial = Integer(0)

    while stack:
        k = stack.pop()
        k = simplify_greedy_decreasing(k, inplace=True)
        k.attr["_coefficient"] *= _SUM_XYZ ** remove_unknots(k)

        k, crossing = _choose_crossing_for_switching(k)

        if crossing is not None:
            k_switch = mirror(k, [crossing], inplace=False)  # switch the crossing sign
            k_smooth = smoothen_crossing(k, crossing, method="O", inplace=False)  # smoothen the crossing
            k_switch.attr["_coefficient"] *= (- _Y * _X ** -1) if k.sign(crossing) > 0 else (- _X * _Y ** -1)
            k_smooth.attr["_coefficient"] *= (- _Z * _X ** -1) if k.sign(crossing) > 0 else (- _Z * _Y ** -1)
            stack.append(k_switch)
            stack.append(k_smooth)
        else:
            if len(k) == 0:
                polynomial += k.attr["_coefficient"] / _SUM_XYZ
            else:
                raise ValueError(f"Got a reduced HOMFLYPT polynomial state with vertices or crossings.")

    return polynomial


def homflypt_polynomial_xyz(k: PlanarDiagram | OrientedPlanarDiagram):
    """Return the HOMFLYPT polynomial in variables v and z of a knot k. Respecting the skein relation
    x * P(L+) + y * P(L-) + z * P(L0) = 0.
    """
    k = k.copy() if k.is_oriented() else orient(k)
    settings_dump = settings.dump()
    settings.update({"trace_moves": False, "allowed_moves": "r1,r2,r3", "framed": False})
    polynomial = _compute_homflypt(k)
    settings.load(settings_dump)
    return expand(polynomial)

def homflypt_polynomial_lm(k: PlanarDiagram | OrientedPlanarDiagram):
    """Return the HOMFLYPT polynomial in variables v and z of a knot k. Respecting the skein relation
    l * P(L+) + l^-1 * P(L-) + m * P(L0) = 0
    """
    return expand(homflypt_polynomial_xyz(k).subs({_X: _L, _Y: _L**-1, _Z: _M}))

def homflypt_polynomial_vz(k: PlanarDiagram | OrientedPlanarDiagram):
    """Return the HOMFLYPT polynomial in variables v and z of a knot k. Respecting the skein relation
    v^-1 * P(L+) - v * P(L-) - z * P(L0) = 0
    """
    return expand(homflypt_polynomial_xyz(k).subs({_X: _V**-1, _Y: -_V, _Z: -_Z}))

def homflypt_polynomial(k: PlanarDiagram | OrientedPlanarDiagram):
    """Return the HOMFLYPT polynomial in variables v and z of a knot k. Respecting the skein relation
    v^-1 * P(L+) - v * P(L-) - z * P(L0) = 0
    """
    return expand(homflypt_polynomial_xyz(k).subs({_X: _V**-1, _Y: -_V, _Z: -_Z}))

def homflypt_polynomial_az(k: PlanarDiagram | OrientedPlanarDiagram):
    """Return the HOMFLYPT polynomial in variables v and z of a knot k. Respecting the skein relation
    v^-1 * P(L+) - v * P(L-) - z * P(L0) = 0
    """
    return expand(homflypt_polynomial_xyz(k).subs({_X: _A, _Y: -_A**-1, _Z: -_Z}))


if __name__ == '__main__':
    import knotpy as kp
    for knot in ["3_1", "4_1", "5_2", "6_3"]:
        k = kp.knot(knot)
        print(" ",knot, homflypt_polynomial(k))
        print("*", knot, homflypt_polynomial(kp.mirror(k)))