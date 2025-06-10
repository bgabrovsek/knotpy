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
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

from sympy import Expr, expand, Integer, symbols, Symbol
from collections import deque

from knotpy.algorithms.skein import smoothen_crossing
from knotpy.invariants.writhe import forced_writhe
from knotpy.algorithms.orientation import unorient
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.topology import is_empty_diagram
from knotpy.manipulation.remove import remove_unknots
from knotpy.utils.module import module
from knotpy.algorithms.canonical import canonical
from knotpy.reidemeister.simplify import simplify_crossing_reducing
from knotpy.invariants.cache import Cache
from knotpy._settings import settings

_KBSM_cache = Cache(max_number_of_nodes=5, cache_size=10000)

_A = symbols("A")
_kauffman_term = -_A ** 2 - _A ** (-2)


def kauffman_bracket_skein_module(k: PlanarDiagram, normalize=True):
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

    # Do not allow R5 moves in general when simplifying yamada states, Yamada needs different settings than the global diagram
    settings_dump = settings.dump()
    settings.update({"trace_moves": False, "r5_only_trivalent": True, "framed": True})

    if k.is_oriented():
        raise NotImplementedError("The Kauffman bracket skein module is not implemented for oriented knots")

    original_knot = k
    expression = module()
    stack = deque()

    k = unorient(k) if k.is_oriented() else k.copy()
    # add framing if unframed
    if not k.is_framed():
        k.framing = 0

    stack.append((Integer(1), k))

    while stack:
        coeff, k = stack.pop()

        #print("> ",coeff, k)
        simplify_crossing_reducing(k, inplace=True)
        #print("s ", coeff, k)

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
            expression += (coeff * (_kauffman_term ** number_of_unknots) * ((- _A ** 3) ** (-framing)), k_canonical)

    original_framing = original_knot.framing if original_knot.is_framed() else 0

    if normalize:
        wr = forced_writhe(original_knot)
        expression *= (- _A ** (-3)) ** (wr + original_framing)
    else:
        expression *= (- _A ** (-3)) ** original_framing

    settings.load(settings_dump)
    return [(expand(r), s) for r, s in expression.to_tuple()]


def bracket_polynomial(k: PlanarDiagram, normalize=True) -> Expr:
    """Return the (Kauffman) Bracket polynomial defined via the skein relations <L_X> = A <L_0> + 1/A <L_inf>,
    <L ⊔ U> = (-A^2 - A^-2) <L> and <unknot> = 1.
       :param k: Planar diagram
       :param normalize: should we normalize it by multiplying by the factor (-A^3)^wr(k), where wr is the writhe of the
       diagram d
       :return: (Laurent) polynomial in variable

       TODO: take care of vertices connected by two arcs,
       TODO: take care that we unframe once we add the framing to the polynomial
       TODO: canonical
       """

    # Do not allow R5 moves in general when simplifying yamada states, Yamada needs different settings than the global diagram
    settings_dump = settings.dump()
    settings.update({"trace_moves": False, "r5_only_trivalent": True, "framed": True})

    original_knot = k
    if k.is_oriented():
        raise NotImplementedError("The Kauffman bracket skein module is not implemented for oriented knots")

    polynomial = Integer(0)  # current bracket polynomial
    stack = deque()
    k = unorient(k) if k.is_oriented() else k.copy()
    # add framing if unframed
    if not k.is_framed():
        k.framing = 0

    stack.append((Integer(1), k))

    while stack:
        coeff, k = stack.pop()

        simplify_crossing_reducing(k, inplace=True)

        if k.crossings:
            crossing = next(iter(k.crossings))
            kA = smoothen_crossing(k, crossing_for_smoothing=crossing, method="A")  # smoothing_type_A(k, crossing)
            kB = smoothen_crossing(k, crossing_for_smoothing=crossing, method="B")  # smoothing_type_A(k, crossing)
            stack.append((coeff * _A, kA))
            stack.append((coeff * (_A ** -1), kB))
        else:
            number_of_unknots = remove_unknots(k)
            if not is_empty_diagram(k):
                raise ValueError("Obtained non-empty diagram when removing crossings from knot.")

            polynomial += coeff * (_kauffman_term ** (number_of_unknots-1)) * ((- _A ** 3) ** (-k.framing))


    original_framing = original_knot.framing if original_knot.is_framed() else 0

    if normalize:
        polynomial *= (- _A ** (-3)) ** (forced_writhe(original_knot) + original_framing)  # ignore framing if normalized
    else:
        polynomial *= (- _A ** (-3)) ** (original_framing)

    settings.load(settings_dump)

    return expand(polynomial)


if __name__ == '__main__':
    import knotpy as kp
    import matplotlib.pyplot as plt
    import sympy

    a = kp.from_pd_notation("X[1,5,2,4],X[3,1,4,6],X[5,3,6,2]")  # trefoil
    b = kp.from_pd_notation("X[5,2,4,1],X[1,4,6,3],X[3,6,2,5]")  # mirror trefoil
    k = kp.from_pd_notation("X[1,5,2,4],X[3,9,4,8],X[5,1,6,10],X[7,3,8,2],X[9,7,10,6]]")  # 5_2 knot

    knots = [a, b, k]
    for k in knots:
        print(k)
        poly = kp.bracket_polynomial(k, normalize=True)
        poly_nn = kp.bracket_polynomial(k, normalize=False)
        print(poly)
        for _ in kp.random_reidemeister_moves(k, count=12):
            poly_ = kp.bracket_polynomial(_, normalize=True)
            poly_nn_ = kp.bracket_polynomial(_, normalize=False)
            if poly_ != poly:
                print("Not the same:", poly)
            if poly_nn_ != poly_nn:
                print("Non-normalized Not the same:", poly_nn_)

    exit()


    m = kp.from_pd_notation("X[4, 5, 6, 3], X[4, 3, 7, 8], X[6, 5, 8, 7]")
    print(m)
    print(kp.bracket_polynomial(m))

    m = kp.from_pd_notation("X[4, 5, 6, 3], X[3, 7, 8, 4], X[6, 5, 8, 7]")
    print(m)
    print(kp.bracket_polynomial(m))


    m = kp.from_pd_notation("X[3, 4, 5, 6], X[7, 8, 9, 3], X[4, 9, 8, 10], X[5, 10, 7, 6]")
    print(m)
    print(kp.bracket_polynomial(m))


    exit()

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
