__all__ = ['alexander', 'multivariable_alexander', 'alexander_multivariable']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

from sympy import expand, Rational, Integer, simplify, gcd, Poly, fraction
from functools import reduce
from collections import defaultdict
from itertools import permutations

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.invariants.homflypt import homflypt_xyz
from knotpy.algorithms.orientation import orient
from knotpy.algorithms.components_link import link_components_endpoints
from knotpy.invariants.fundamental_group import fundamental_group, alexander_fox_matrix, collapse_generators_by_components, gcd_of_minors, minors
from knotpy.invariants._symbols import _t, _x, _y, _z
from knotpy.utils.laurent import normalize_symmetric, normalize_positive_exponents, canonicalize_under_variable_permutation


def alexander(k: PlanarDiagram | OrientedPlanarDiagram, symmetric=False):
    """Return the Alexander polynomial of a knot."""
    polynomial = homflypt_xyz(k)
    polynomial = expand(polynomial.subs({_x: Integer(1), _y: Integer(-1), _z: -_t ** Rational(1, 2) + _t ** Rational(-1, 2)}))
    polynomial = normalize_symmetric(polynomial) if symmetric else normalize_positive_exponents(polynomial, variables=[_t])
    return polynomial


def alexander_multivariable(k: PlanarDiagram | OrientedPlanarDiagram):
    """
    Compute the Alexander polynomial from the abelianized Alexander matrix.
    Returns the gcd of all (n-1)x(n-1) minors (up to units).
    """

    k = k.copy() if k.is_oriented() else orient(k)

    G, eps_gen_dict = fundamental_group(k, return_dict=True)

    matrix = alexander_fox_matrix(G)
    component_endpoints = link_components_endpoints(k)
    matrix, variables = collapse_generators_by_components(matrix, eps_gen_dict, component_endpoints)

    all_minors = minors(matrix)

    if not all_minors:
        return Integer(1)  # trivial case

    factor, poly_gcd = gcd_of_minors(all_minors, variables)

    # print("P", poly_gcd)
    poly_gcd = normalize_positive_exponents(poly_gcd, variables)
    # print("P", poly_gcd)
    poly_gcd = canonicalize_under_variable_permutation(poly_gcd, variables, allow_sign_change=True)
    # print("P", poly_gcd)

    # Return normalized form (up to units: sign and monomials)
    return expand(poly_gcd)

def multivariable_alexander(k: PlanarDiagram | OrientedPlanarDiagram):
    """
    Compute the Alexander polynomial from the abelianized Alexander matrix.
    Returns the gcd of all (n-1)x(n-1) minors (up to units).
    """
    return alexander_multivariable(k)



if __name__ == '__main__':
    a = "a → X(b3i c0i c3o b0o), b → X(a3i d0i d3o a0o), c → X(a1o d2o d1i a2i), d → X(b1o c2o c1i b2i)"
    b = "a → X(b3i c0o c3o b0i), b → X(a3o d0i d3i a0o), c → X(a1i d2o d1o a2i), d → X(b1o c2i c1i b2o)"
    from knotpy import from_knotpy_notation
    a = from_knotpy_notation(a)
    b = from_knotpy_notation(b)

    print(a)

    ap = alexander_multivariable(a)
    print(ap)
    print()

    bp = alexander_multivariable(b)
    print(bp)
    import knotpy as kp
    #l = kp.link("L8a15")
    # k = kp.knot("3_1")
    # k = kp.link("L4a1{1}")
    #print(alexander(l))
    # print(multivariable_alexander(k))