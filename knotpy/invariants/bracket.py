"""
The bracket polynomial <.> (aka the Kauffman bracket) is a polynomial invariant of unoriented framed links.
It is characterized by the following three rules:
1. <U> = 1, where U is the unknot.
2. <L_X> = A <L_0> + 1/A <L_inf>
3. <L ⊔ U> = (-A^2 - A^-2) <L>
See Louis H. Kauffman, State models and the Jones polynomial. Topology 26 (1987), no. 3, 395--407.
"""

__all__ = ['bracket_polynomial']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'

from sympy import Expr, expand, Integer, symbols, Symbol
from collections import deque

from knotpy.algorithms.skein import smoothing_type_A, smoothing_type_B
from knotpy.invariants.writhe import writhe
from knotpy.algorithms.orientation import unorient

def bracket_polynomial(k, variable="A", normalize=True) -> Expr:
    """

    :param k:
    :param variable:
    :param normalize:
    :return:
    """

    # if k.is_oriented():
    #     raise NotImplemented("the bracket polynomial is defined for unoriented knots")  # TODO: convert to unoriented version

    A = variable if isinstance(variable, Symbol) else symbols(variable)

    _kauffman_term = (-A ** 2 - A ** (-2))
    _framing_term = - A ** 3

    polynomial = Integer(0)
    stack = deque()
    stack.append((Integer(1), k if not k.is_oriented() else unorient(k)))

    while stack:
        polynomial, k = stack.pop()

        if k.crossings:
            crossing = next(iter(k.crossings))
            kA = smoothing_type_A(k, crossing)
            kB = smoothing_type_B(k, crossing)
            stack.append((polynomial * A, kA))
            stack.append((polynomial * (A**-1), kB))

        else:
            polynomial += polynomial * (_kauffman_term ** (k.number_of_nodes - 1)) * (_framing_term ** k.framing)

    if normalize:
        polynomial *= _framing_term ** writhe(k)  # the normalized bracket is (-A^-3)^w(L) * <L>


    return expand(polynomial)

