"""
The bracket polynomial <.> (aka the Kauffman bracket) is a polynomial invariant of unoriented framed links.
It is characterized by the following three rules:
1. <U> = 1, where U is the unknot.
2. <L_X> = A <L_0> + 1/A <L_inf>
3. <L ⊔ U> = (-A^2 - A^-2) <L>
See Louis H. Kauffman, State models and the Jones polynomial. Topology 26 (1987), no. 3, 395--407.
"""

__all__ = ['bracket_polynomial', "kauffman_bracket_skein_module"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'

from sympy import Expr, expand, Integer, symbols, Symbol
from collections import deque

from knotpy.algorithms.skein import smoothen_crossing #smoothing_type_A, smoothing_type_B
from knotpy.invariants.writhe import writhe
from knotpy.algorithms.orientation import unoriented
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.orientation import all_orientations
from knotpy.algorithms.structure import is_knot, is_planar_graph
from knotpy.algorithms.components_disjoint import number_of_unknots, remove_unknots
from knotpy.utils.module import module
from knotpy.algorithms.canonical import canonical
from knotpy.reidemeister.simplification import simplify_diagram_crossing_reducing

def _forced_writhe(k: PlanarDiagram) -> int:
    """
    :param k:
    :return:
    """
    if k.is_oriented():
        return writhe(k)
    else:
        try:
            return writhe(k)
        except ValueError:
            return min(writhe(ok) for ok in all_orientations(k))

def kauffman_bracket_skein_module(k :PlanarDiagram, variable="A", normalize=True, use_cache=True):
    """

    :param k:
    :param variable:
    :param normalize:
    :return:

    # TODO: take care of vertices connected by two arcs,
    TODO: take care that we unframe once we add the framing to the polynomial
    TODO: canonical
    TODO: expression as defaultdicT?
    """
    if k.is_oriented():
        raise NotImplementedError("The Kauffman bracket skein module is not implemented for oriented knots")

    original_knot = k
    A = variable if isinstance(variable, Symbol) else symbols(variable)
    _kauffman_term = (-A ** 2 - A ** (-2))
    expression = module()
    stack = deque()

    stack.append((Integer(1), k.copy() if not k.is_oriented() else unoriented(k)))

    CACHE_NODES = 7
    precomputed = {}

    while stack:
        coeff, k = stack.pop()

        #print("->", k)
        simplify_diagram_crossing_reducing(k, inplace=True)
        #print("==", k)
        #
        # if use_cache and len(k) <= CACHE_NODES:
        #     k = canonical(k)
        #     if k in precomputed:
        #         for m in precomputed:
        #             print("    ", m)
        #         expression += precomputed[k]
        #     else:
        #         invariant_value = kauffman_bracket_skein_module(k, variable, normalize=False, use_cache=False)
        #         invariant_value = module.from_tuples(invariant_value)
        #         precomputed[k] = invariant_value
        #         expression += invariant_value
        #     continue

        if k.crossings:
            crossing = next(iter(k.crossings))
            kA = smoothen_crossing(k, crossing_for_smoothing=crossing, method="A") # smoothing_type_A(k, crossing)
            kB = smoothen_crossing(k, crossing_for_smoothing=crossing, method="B") # smoothing_type_A(k, crossing)
            stack.append((coeff * A, kA))
            stack.append((coeff * (A**-1), kB))
        else:
            #print("u",k)
            number_of_unknots = remove_unknots(k)
            #print("r", k)
            k_canonical = canonical(k)
            framing = k_canonical.framing
            k_canonical.framing = 0

            expression += (coeff * (_kauffman_term ** number_of_unknots) * ((- A ** 3) ** framing), k_canonical)
            #expression.append((coeff * (_kauffman_term ** number_of_unknots) * ((- A ** 3) ** k.framing), k_canonical))

    if normalize:
        wr = _forced_writhe(original_knot)
        #print("writhe", wr)
        expression *= (- A ** (3)) ** (wr + original_knot.framing)
        #expression = [(expand(koeff * _kauffman_term ** wr), g) for koeff, g in expression]  # the normalized bracket is (-A^-3)^w(L) * <L>
    #else:
    #    expression = [(expand(koeff), g) for koeff, g in expression]

    return [(expand(r), s) for r, s in expression.to_tuple()]



def bracket_polynomial(k, variable="A", normalize=True) -> Expr:
    """
    :param k:
    :param variable:
    :param normalize:
    :return:
    """
    if not is_knot(k):
        raise ValueError("The bracket polynomial can onlt be computed for knots and links.")
        #return kauffman_bracket_skein_module(k, variable, normalize)

    if k.is_oriented():
        raise NotImplementedError("The bracket polynomial is not implemented for oriented knots")

    original_knot = k
    A = variable if isinstance(variable, Symbol) else symbols(variable)
    _kauffman_term = (-A ** 2 - A ** (-2))
    polynomial = Integer(0)
    stack = deque()

    stack.append((Integer(1), k if not k.is_oriented() else unoriented(k)))

    while stack:
        coeff, k = stack.pop()

        if k.crossings:
            crossing = next(iter(k.crossings))
            kA = smoothen_crossing(k, crossing_for_smoothing=crossing, method="A") # smoothing_type_A(k, crossing)
            kB = smoothen_crossing(k, crossing_for_smoothing=crossing, method="B") # smoothing_type_A(k, crossing)
            stack.append((coeff * A, kA))
            stack.append((coeff * (A**-1), kB))
        else:
            #polynomial += coeff * (_kauffman_term ** (k.number_of_nodes - 1)) * ((- A ** 3) ** k.framing
            if k.number_of_nodes != k.number_of_unknots:
                raise ValueError("After skein resolution, number of nodes does not equal number of unknots")
            polynomial += coeff * (_kauffman_term ** (k.number_of_unknots - 1)) * ((- A ** 3) ** k.framing)

    if normalize:
        polynomial *= (- A ** 3) ** _forced_writhe(original_knot)  # the normalized bracket is (-A^-3)^w(L) * <L>

    return expand(polynomial)

