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

from sympy import Expr, expand, Integer
from collections import deque

from knotpy.utils.decorators import single_variable_invariant
from knotpy.algorithms.skein import smoothing_type_A, smoothing_type_B

@single_variable_invariant('A')
def bracket_polynomial(k, variable='A') -> Expr:

    print(k)
    if k.is_oriented():
        raise NotImplemented("Oriented case not yet implemented")  # TODO: convert to unoriented version

    A = variable
    kauff_term = (-A**2 - 1 / A**2)
    polynomial = Integer(0)
    stack = deque()

    stack.append((Integer(1), k))  # framing!!

    while stack:
        poly, k = stack.pop()
        if k.crossings:
            cr = next(iter(k.crossings))
            stack.append((poly * A, smoothing_type_A(k, cr)))
            stack.append((poly / A, smoothing_type_B(k, cr)))
        else:
            polynomial += poly * kauff_term ** (k.number_of_trivial_components - 1)

    return expand(polynomial)
