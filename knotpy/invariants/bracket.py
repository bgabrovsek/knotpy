# knotpy/invariants/bracket.py
"""
The Kauffman bracket polynomial ⟨·⟩ is a polynomial invariant of unoriented framed links.

It is characterized by three rules:
1. ⟨U⟩ = 1, where U is the unknot.
2. ⟨L_X⟩ = A⟨L_0⟩ + A⁻¹⟨L_∞⟩.
3. ⟨L ⊔ U⟩ = (−A² − A⁻²)⟨L⟩.

References:
    Louis H. Kauffman, *State models and the Jones polynomial*,
    Topology 26 (1987), no. 3, 395–407.
"""

__all__ = ["bracket", "kauffman_bracket_skein_module"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from collections import deque
import sympy as sp

from knotpy.invariants.skein import smoothen_crossing
from knotpy.invariants.writhe import writhe
from knotpy.algorithms.orientation import unorient
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.topology import is_empty_diagram, is_knot
from knotpy.algorithms.remove import remove_unknots
from knotpy.utils.module import Module
from knotpy.algorithms.canonical import canonical
from knotpy.reidemeister.simplify import simplify_decreasing
from knotpy.invariants.cache import Cache
from knotpy._settings import settings
from knotpy.invariants._symbols import _A, _KAUFFMAN_TERM, _x, _y, _z

_USE_JONES_CACHE = False
_KBSM_cache = Cache(max_number_of_nodes=5, cache_size=10000)


def lowest_exponent(laurent_polynomial: sp.Expr, variable: sp.Symbol) -> int:
    """Return the minimal exponent of ``variable`` in a Laurent polynomial."""
    exponents = [term.as_coeff_exponent(variable)[1] for term in laurent_polynomial.as_ordered_terms()]
    return int(min(exponents))


def kauffman_bracket_skein_module(
    k: PlanarDiagram,
    normalize: bool = True,
) -> list[tuple[sp.Expr, PlanarDiagram]]:
    """Compute the Kauffman bracket skein module (unoriented case).

    Args:
        k: Unoriented planar diagram. Oriented diagrams are not yet supported.
        normalize: If True, normalize by a power of ``(-A³)`` depending on writhe/framing.

    Returns:
        A list of pairs ``(polynomial, diagram)`` for the module expansion.

    Raises:
        NotImplementedError: If ``k`` is oriented.
    """
    # Adjust settings for skein module computation.
    settings_dump = settings.dump()
    settings.update({"trace_moves": False, "r5_only_trivalent": True, "framed": True})

    if k.is_oriented():
        raise NotImplementedError(
            "The Kauffman bracket skein module is not implemented for oriented knots."
        )

    is_single_knot = is_knot(k)
    original_framing = k.framing if k.is_framed() else 0
    original_knot = k
    expression = Module()
    stack = deque()

    k = unorient(k) if k.is_oriented() else k.copy()
    if not k.is_framed():
        k.framing = 0

    stack.append((sp.Integer(1), k))

    while stack:
        coeff, k = stack.pop()
        simplify_decreasing(k, inplace=True)

        if k.crossings:
            crossing = next(iter(k.crossings))
            kA = smoothen_crossing(k, crossing_for_smoothing=crossing, method="A")
            kB = smoothen_crossing(k, crossing_for_smoothing=crossing, method="B")
            stack.append((coeff * _A, kA))
            stack.append((coeff * (_A**-1), kB))
        else:
            number_of_unknots = remove_unknots(k)
            framing = k.framing
            k_canonical = canonical(k)
            k_canonical.framing = 0
            expression += (
                coeff
                * (_KAUFFMAN_TERM**number_of_unknots)
                * ((- _A**3) ** (-framing)),
                k_canonical,
            )

    if normalize:
        if is_single_knot:
            expression *= (-_A**-3) ** (writhe(original_knot) + original_framing)
        else:
            adjusted_writhe = min(
                lowest_exponent(sp.expand(r), _A) // 3
                for r, _ in expression.to_tuple()
            )
            expression *= (-_A**-3) ** adjusted_writhe
    else:
        expression *= (-_A**-3) ** original_framing

    settings.load(settings_dump)
    for r, s in expression.to_tuple():
        s.name = None
    return [(sp.expand(r), s) for r, s in expression.to_tuple()]

def bracket_from_homflypt(polynomial_xyz) -> sp.Expr:
    """Compute the normalized bracket polynomial from the homflypt polynomial in variables xyz."""

    polynomial_xyz = sp.expand(
        polynomial_xyz.subs({_x: _A**4, _y: -_A**-4, _z: _A**-2 - _A**2})
    )
    return polynomial_xyz


def bracket(k: PlanarDiagram, normalize: bool = True) -> sp.Expr:
    """Compute the Kauffman bracket polynomial ⟨·⟩.

    Defined by:
        1. ⟨U⟩ = 1.
        2. ⟨L_X⟩ = A⟨L_0⟩ + A⁻¹⟨L_∞⟩.
        3. ⟨L ⊔ U⟩ = (−A² − A⁻²)⟨L⟩.

    Args:
        k: Planar diagram.
        normalize: If True, multiply by factor ``(-A³)^{-wr(k)}`` (ignore framing).

    Returns:
        Laurent polynomial in variable ``A``.

    Raises:
        ValueError: If unknot removal yields a non-empty diagram.
    """

    # try do compute the bracket polynomial from the precomputed homflypt polynomial
    from knotpy.tables.knot import knot_precomputed_homflypt
    polynomial = knot_precomputed_homflypt(k)
    if polynomial is not None:
        polynomial = bracket_from_homflypt(polynomial)
        original_framing = k.framing if k.is_framed() else 0
        if normalize:
            polynomial *= (-_A ** -3) ** (-original_framing)  # reverse
        else:
            polynomial *= (-_A ** -3) ** (-original_framing - writhe(k))  # reverse
        return sp.expand(polynomial)


    settings_dump = settings.dump()
    settings.update({"trace_moves": False, "r5_only_trivalent": True, "framed": True})

    original_knot = k
    if k.is_oriented():
        k = unorient(k)

    polynomial = sp.Integer(0)
    stack = deque()
    k = unorient(k) if k.is_oriented() else k.copy()
    if not k.is_framed():
        k.framing = 0

    stack.append((sp.Integer(1), k))

    while stack:
        coeff, k = stack.pop()
        simplify_decreasing(k, inplace=True)

        if k.crossings:
            crossing = next(iter(k.crossings))
            kA = smoothen_crossing(k, crossing_for_smoothing=crossing, method="A")
            kB = smoothen_crossing(k, crossing_for_smoothing=crossing, method="B")
            stack.append((coeff * _A, kA))
            stack.append((coeff * (_A**-1), kB))
        else:
            number_of_unknots = remove_unknots(k)
            if not is_empty_diagram(k):
                raise ValueError("Obtained non-empty diagram after removing all crossings.")
            polynomial += coeff * (_KAUFFMAN_TERM ** (number_of_unknots - 1)) * (
                (-_A**3) ** (-k.framing)
            )

    original_framing = original_knot.framing if original_knot.is_framed() else 0

    if normalize:
        polynomial *= (-_A**-3) ** (writhe(original_knot) + original_framing)
    else:
        polynomial *= (-_A**-3) ** original_framing

    settings.load(settings_dump)
    return sp.expand(polynomial)


if __name__ == "__main__":
    pass
