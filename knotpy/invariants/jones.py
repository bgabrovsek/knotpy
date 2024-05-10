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

from sympy import Expr, expand, symbols, Symbol

from knotpy.invariants.bracket import bracket_polynomial


def jones_polynomial(k, variable="q") -> Expr:
    """

    :param k:
    :param variable:
    :return:
    """

    if not k.is_oriented():
        raise NotImplemented("the jones polynomial is defined for oriented knots or links")

    q = variable if isinstance(variable, Symbol) else symbols(variable)
    A = symbols("A") if q.name != "A" else "B"

    polynomial = bracket_polynomial(k, A, normalize=True)
    return expand(polynomial.subs(A, q**(1/4)))
