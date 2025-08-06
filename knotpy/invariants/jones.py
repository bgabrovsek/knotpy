"""
The bracket polynomial <.> (aka the Kauffman bracket) is a polynomial invariant of unoriented framed links.
It is characterized by the following three rules:
1. <U> = 1, where U is the unknot.
2. <L_X> = A <L_0> + 1/A <L_inf>
3. <L ⊔ U> = (-A^2 - A^-2) <L>
See Louis H. Kauffman, State models and the Jones polynomial. Topology 26 (1987), no. 3, 395--407.
"""

__all__ = ['jones']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

from sympy import Expr, expand, symbols, Symbol, Rational

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.invariants.bracket import bracket
from knotpy.invariants._symbols import _A, _t


def jones(k: PlanarDiagram | OrientedPlanarDiagram):
    """
    Compute the jones polynomial from the (Kauffman) bracket polynomial
    :param k:
    :return:
    """
    polynomial = bracket(k, normalize=True)

    # alternative: l = i * t^(−1),  m = i * (t^(−1/2) − t^(1/2))

    return expand(polynomial.subs({_A: _t ** Rational(-1, 4)}))


if __name__ == '__main__':
    from knotpy.notation.pd import from_pd_notation

    a = from_pd_notation("X[1,5,2,4],X[3,1,4,6],X[5,3,6,2]")  # trefoil
    b = from_pd_notation("X[5,2,4,1],X[1,4,6,3],X[3,6,2,5]")  # mirror trefoil
    k = from_pd_notation("X[1,5,2,4],X[3,9,4,8],X[5,1,6,10],X[7,3,8,2],X[9,7,10,6]]")  # 5_2 knot

    print(a, a.is_oriented())
    print(b)
    print(k)

    jones_a = jones(a)
    jones_b = jones(b)
    jones_k = jones(k)

    print(jones_a)
    print(jones_b)
    print(jones_k)




"""
t**(7/2) + t**(3/2) - sqrt(t)
-1/sqrt(t) + t**(-3/2) + t**(-7/2)
"""