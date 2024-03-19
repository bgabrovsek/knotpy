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
from knotpy.algorithms.faces import choose_kink
from knotpy.manipulation.reidemeister import remove_kink
from knotpy.manipulation.simplification import simplify

_A = symbols("A")
_kauffman_term = (-_A ** 2 - _A ** (-2))
_framing_term = - _A ** 3

#@single_variable_invariant('A')
def bracket_polynomial(k, variable="A") -> Expr:

    if k.is_oriented():
        raise NotImplemented("Oriented case not yet implemented")  # TODO: convert to unoriented version

    A = variable if isinstance(variable, Symbol) else symbols(variable)

    poly = Integer(0)
    stack = deque()
    stack.append((Integer(1), k))

    #print("ok")

    while stack:
        #print("pop")
        poly, k = stack.pop()

        if reduce:
            simplify(k, in_place=True)

        #print("k", k)
        if k.crossings:
            crossing = next(iter(k.crossings))
            kA = smoothing_type_A(k, crossing)
            kB = smoothing_type_B(k, crossing)
            #print(kA)
            #print(kB)
            stack.append((poly * A, kA))
            stack.append((poly / A, kB))

        else:
            polynomial += poly * (kauff_term ** (k.number_of_nodes - 1)) * (framing_term ** k.framing)

    return expand(polynomial)
