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

__all__ = ['homflypt', 'homflypt_lm', 'homflypt_vz', 'homflypt_az', 'homflypt_xyz']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'


from sympy import Integer, expand
from collections import deque, OrderedDict
from random import choice


from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.orientation import orient
from knotpy.reidemeister.simplify import simplify_decreasing, simplify_non_increasing
from knotpy.algorithms.symmetry import mirror
from knotpy.algorithms.skein import smoothen_crossing
from knotpy._settings import settings
from knotpy.algorithms.remove import remove_unknots
from knotpy.algorithms.alternating import is_face_alternating
from knotpy.utils.set_utils import LeveledSet
from knotpy.algorithms.canonical import canonical
from knotpy.reidemeister.reidemeister_3 import reidemeister_3, find_reidemeister_3_triangle
from knotpy.classes.freezing import freeze

from knotpy.invariants._symbols import _A, _l, _m, _v, _x, _y, _z, _HOMFLYPT_SUM_XYZ


_USE_HOMFLYPT_PRECACHE = False
_homflypt_xyz_precache = OrderedDict()


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

def _choose_crossing_for_switching(k: OrientedPlanarDiagram, sum_coefficient):
    """Choose the best crossing to perform the skein relation, so the diagram simplifies after the crossing switch."""
    if not k.crossings:
        return k, None
    faces = list(k.faces)

    #print("len1")
    # Are there any faces of length 1?
    if [face for face in faces if len(face) == 1]:
        #print("yes")
        raise RuntimeError(f"There exists a kink after simplification, which should not happen {k}.")
    #print("no")

    #print("len2")
    # Are there any faces of length 2?
    if faces2 := [face for face in faces if len(face) == 2]:
        #print("yes")
        return k, faces2[0][0].node
    #print("no")

    # print("faces:",list(k.faces))
    # print("faces:",[f for f in list(k.faces) if len(f) == 3])
    # print("faces:",faces3 := [face for face in faces if len(face) == 3])
    # print("non-alt", [face for face in faces3 if not is_face_alternating(face)])
    # print("    alt", [face for face in faces3 if is_face_alternating(face)])

    # Are there any faces of length 3?
    if faces3 := [face for face in faces if len(face) == 3]:

        # if there are non-alternating faces, make r3 moves and try to make a R2 face via R-moves
        if non_alt_faces := [face for face in faces3 if not is_face_alternating(face)]:
            # Try to simplify the diagram so that we have a good crossing to make a skein move on.
            ls = LeveledSet(freeze(canonical(k)))
            while not ls.is_level_empty(-1):
                # Put diagrams after removing kinks and unpokes to the next level.
                ls.new_level()
                for k_ in ls.iter_level(-2):
                    for location in find_reidemeister_3_triangle(k_):

                        k_r3 = reidemeister_3(k_, location, inplace=False)
                        num_nodes = len(k_r3)
                        k_r3_ = simplify_non_increasing(k_r3, greediness=3) #fast_simplification_greedy(k)
                        if len(k_r3_) < num_nodes or any(len(f) == 2 for f in k_r3_.faces):
                            #print("found!")
                            k_r3_.attr["_coefficient"] *= sum_coefficient ** remove_unknots(k_r3_)
                            if len(k_r3_.crossings) == 0:
                                return k_r3_, None
                            return _choose_crossing_for_switching(k_r3_, sum_coefficient=_HOMFLYPT_SUM_XYZ)  #TODO: it is not optimal to call the function again
                        ls.add(freeze(canonical(k_r3)))
            print("end of loop")
        # If no good non-alternating 3-faces found, make an alternating 3-face a non-alternating one
        if alt_faces := [face for face in faces3 if is_face_alternating(face)]:
            face_3_crossings = [c for face in alt_faces for c in [face[0].node, face[1].node, face[2].node]]
            cr_ch = choice(list(face_3_crossings))

            return k, cr_ch  # todo: sometimes this takes long, why?

    print(k)
    raise RuntimeError(f"There are no 3-faces in the diagram {k}")  # A contradiction due to Euler's characteristic.


def _compute_homflypt(k: OrientedPlanarDiagram):
    """ Compute the HOMFLYPT polynomial in variables x,y,z of a knot k."""



    stack = deque([k.copy(_coefficient=Integer(1))])
    polynomial = Integer(0)

    while stack:
        k = stack.pop()
        k = simplify_decreasing(k, inplace=True)
        k.attr["_coefficient"] *= _HOMFLYPT_SUM_XYZ ** remove_unknots(k)

        k, crossing = _choose_crossing_for_switching(k, sum_coefficient=_HOMFLYPT_SUM_XYZ)

        if crossing is not None:
            k_switch = mirror(k, [crossing], inplace=False)  # switch the crossing sign
            k_smooth = smoothen_crossing(k, crossing, method="O", inplace=False)  # smoothen the crossing
            k_switch.attr["_coefficient"] *= (- _y * _x ** -1) if k.sign(crossing) > 0 else (- _x * _y ** -1)
            k_smooth.attr["_coefficient"] *= (- _z * _x ** -1) if k.sign(crossing) > 0 else (- _z * _y ** -1)
            stack.append(k_switch)
            stack.append(k_smooth)
        else:
            if len(k) == 0:
                polynomial += k.attr["_coefficient"] / _HOMFLYPT_SUM_XYZ
            else:
                raise ValueError(f"Got a reduced HOMFLYPT polynomial state with vertices or crossings.")

    return polynomial


def homflypt_xyz(k: PlanarDiagram | OrientedPlanarDiagram):
    """Return the HOMFLYPT polynomial in variables v and z of a knot k. Respecting the skein relation
    x * P(L+) + y * P(L-) + z * P(L0) = 0.
    """

    # Simple lightweight cache
    #key = id(k)  # only caches for this *specific* object

    # if is_unknot(k):
    #     print("uk")
    #     return Integer(1)

    if _USE_HOMFLYPT_PRECACHE:
        if k in _homflypt_xyz_precache:
            return _homflypt_xyz_precache[k]

    k_original = k
    k = k.copy() if k.is_oriented() else orient(k)

    settings_dump = settings.dump()
    settings.update({"trace_moves": False, "allowed_moves": "r1,r2,r3", "framed": False})
    polynomial = expand(_compute_homflypt(k))
    settings.load(settings_dump)

    if _USE_HOMFLYPT_PRECACHE:
        # put to cache and remove the oldest from cache
        _homflypt_xyz_precache[freeze(k_original, inplace=False)] = polynomial
        if len(_homflypt_xyz_precache) > 16:
            _homflypt_xyz_precache.popitem(last=False)  # Remove oldest

    return polynomial

def _xyy_to_lm(polynomial):
    return expand(polynomial.subs({_x: _l, _y: _l ** -1, _z: _m}))

def _xyz_to_vz(polynomial):
    return expand(polynomial.subs({_x: _v ** -1, _y: -_v, _z: -_z}))

def _xyz_to_az(polynomial):
    return expand(polynomial.subs({_x: _A, _y: -_A ** -1, _z: -_z}))

def homflypt_lm(k: PlanarDiagram | OrientedPlanarDiagram):
    """Return the HOMFLYPT polynomial in variables v and z of a knot k. Respecting the skein relation
    l * P(L+) + l^-1 * P(L-) + m * P(L0) = 0
    """
    return _xyy_to_lm(homflypt_xyz(k))

def homflypt_vz(k: PlanarDiagram | OrientedPlanarDiagram):
    """Return the HOMFLYPT polynomial in variables v and z of a knot k. Respecting the skein relation
    v^-1 * P(L+) - v * P(L-) - z * P(L0) = 0
    """
    return _xyz_to_vz(homflypt_xyz(k))

def homflypt(k: PlanarDiagram | OrientedPlanarDiagram):
    """Return the HOMFLYPT polynomial in variables v and z of a knot k. Respecting the skein relation
    v^-1 * P(L+) - v * P(L-) - z * P(L0) = 0
    """
    return _xyz_to_vz(homflypt_xyz(k))

def homflypt_az(k: PlanarDiagram | OrientedPlanarDiagram):
    """Return the HOMFLYPT polynomial in variables v and z of a knot k. Respecting the skein relation
    v^-1 * P(L+) - v * P(L-) - z * P(L0) = 0
    """
    return _xyz_to_az(homflypt_xyz(k))


if __name__ == '__main__':
    import knotpy as kp

    k = kp.from_knotpy_notation("b → X(e0 f3 k3 d0), d → X(b3 l0 h0 e1), e → X(b0 d3 h3 f0), f → X(e3 j0 k0 b1), h → X(d2 l3 j1 e2), j → X(f1 h2 l2 k1), k → X(f2 j3 l1 b2), l → X(d1 k2 j2 h1)")
    print(homflypt_xyz(k))
    #print(_choose_crossing_for_switching(k, 1))
    exit()
    for knot in ["3_1", "4_1", "5_2", "6_3"]:
        k = kp.knot(knot)
        print(" ", knot, homflypt(k))
        print("*", knot, homflypt(kp.mirror(k)))