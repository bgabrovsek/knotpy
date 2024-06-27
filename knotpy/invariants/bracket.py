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
from knotpy.invariants.cache import Cache
from knotpy.algorithms.classification import is_empty_diagram

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


_KBSM_cache = Cache(max_number_of_nodes=5, cache_size=10000)



def kauffman_bracket_skein_module(k: PlanarDiagram, variable="A", normalize=True):
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

        simplify_diagram_crossing_reducing(k, inplace=True)


        if k.crossings:
            crossing = next(iter(k.crossings))
            kA = smoothen_crossing(k, crossing_for_smoothing=crossing, method="A") # smoothing_type_A(k, crossing)
            kB = smoothen_crossing(k, crossing_for_smoothing=crossing, method="B") # smoothing_type_A(k, crossing)
            stack.append((coeff * A, kA))
            stack.append((coeff * (A**-1), kB))
        else:
            number_of_unknots = remove_unknots(k)
            k_canonical = canonical(k)
            framing = k_canonical.framing
            k_canonical.framing = 0

            expression += (coeff * (_kauffman_term ** number_of_unknots) * ((- A ** 3) ** framing), k_canonical)

    if normalize:
        wr = _forced_writhe(original_knot)
        expression *= (- A ** 3) ** (wr + original_knot.framing)

    return [(expand(r), s) for r, s in expression.to_tuple()]


def bracket_polynomial(k: PlanarDiagram, variable="A", normalize=True) -> Expr:
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
    polynomial = Integer(0)  # current bracket polynomial
    stack = deque()

    stack.append((Integer(1), k.copy() if not k.is_oriented() else unoriented(k)))

    while stack:
        coeff, k = stack.pop()

        simplify_diagram_crossing_reducing(k, inplace=True)

        if k.crossings:
            crossing = next(iter(k.crossings))
            kA = smoothen_crossing(k, crossing_for_smoothing=crossing, method="A")  # smoothing_type_A(k, crossing)
            kB = smoothen_crossing(k, crossing_for_smoothing=crossing, method="B")  # smoothing_type_A(k, crossing)
            stack.append((coeff * A, kA))
            stack.append((coeff * (A ** -1), kB))
        else:
            number_of_unknots = remove_unknots(k)
            k_canonical = canonical(k)
            framing = k_canonical.framing
            k_canonical.framing = 0

            polynomial += coeff * (_kauffman_term ** (number_of_unknots-1)) * ((- A ** 3) ** framing)

    if normalize:
        wr = _forced_writhe(original_knot)
        polynomial *= (- A ** 3) ** (wr + original_knot.framing)

    return expand(polynomial)


if __name__ == '__main__':
    import knotpy as kp
    import matplotlib.pyplot as plt
    import sympy

    plt.close()

    a = kp.from_pd_notation("X[1,5,2,4],X[3,1,4,6],X[5,3,6,2]")  # trefoil
    b = kp.from_pd_notation("X[5,2,4,1],X[1,4,6,3],X[3,6,2,5]")  # mirror trefoil
    k = kp.from_pd_notation("X[1,5,2,4],X[3,9,4,8],X[5,1,6,10],X[7,3,8,2],X[9,7,10,6]]")  # 5_2 knot

    # draw a knot
    kp.draw(k)
    plt.show()

    # save a knot
    kp.draw(k)
    plt.savefig("knot.png")

    # draw many knots to pdf
    knot_list = [a, b, k]

    a.name = "Right Trefoil"
    b.name = "Left Trefoil"
    k.name = "5_2"
    kp.export_pdf(knot_list, "knots.pdf", with_title=True)


    print(a, a.is_oriented())
    print(b)
    print(k)

    bracket_a = bracket_polynomial(a)
    bracket_b = bracket_polynomial(b)
    bracket_k = bracket_polynomial(k)

    print(bracket_a)
    print(bracket_b)
    print(bracket_k)

    A = sympy.symbols("A")
    mirror_b = bracket_b.subs(A,A**(-1))

    print("Mirror:", mirror_b)

    if mirror_b == bracket_a:
        print("Knots are mirrors of each other")


"""A**14 + A**6 - A**2
-1/A**2 + A**(-6) + A**(-14)"""

"""
A**14 + A**6 - A**2
-1/A**2 + A**(-6) + A**(-14)
"""
