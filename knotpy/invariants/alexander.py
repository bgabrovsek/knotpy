__all__ = ['alexander', 'multivariable_alexander', 'alexander_multivariable']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

from sympy import Rational, Integer, symbols, expand, gcd, Matrix, Poly, simplify
from sympy.combinatorics.free_groups import free_group, FreeGroupElement

from itertools import combinations
from functools import reduce

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.invariants.homflypt import homflypt_xyz
from knotpy.algorithms.orientation import orient
from knotpy.algorithms.components_link import link_components_endpoints
from knotpy.invariants.fundamental_group import fundamental_group, alexander_fox_matrix
from knotpy.invariants._symbols import _t, _x, _y, _z
from knotpy.utils.laurent import normalize_symmetric, normalize_laurent_polynomial, canonicalize_under_variable_permutation, normalize_polynomial


def alexander(k: PlanarDiagram | OrientedPlanarDiagram, symmetric=False):
    """Return the one-vaiable Alexander polynomial of a knot or link."""
    polynomial = homflypt_xyz(k)
    polynomial = expand(polynomial.subs({_x: Integer(1), _y: Integer(-1), _z: -_t ** Rational(1, 2) + _t ** Rational(-1, 2)}))
    polynomial = normalize_symmetric(polynomial) if symmetric else normalize_laurent_polynomial(polynomial, variables=[_t])
    return polynomial


def collapse_generators_by_components(matrix, eps_gen_dict, component_endpoints):
    """
    Collapse multiple generators in the matrix to one symbol per component.

    Args:
        matrix: list of list of sympy expressions
        eps_gen_dict: dict mapping endpoints to generator symbols (e.g. {"ep1": x1})
        component_endpoints: list of sets of endpoints, one set per link component

    Returns:
        matrix with generators substituted to t1, t2, ..., one per component
    """

    # Step 1: Create a substitution dictionary {x_i: t_j}
    subs = {}
    for idx, endpoint_set in enumerate(component_endpoints):
        t = symbols(f"t{idx + 1}")  # creates t1, t2, ...
        for ep in endpoint_set:
            gen = eps_gen_dict[ep]
            subs[gen] = t

    subs = {key.array_form[0][0] if isinstance(key, FreeGroupElement) else key: value for key, value in subs.items()}

    new_matrix = [[expr.subs(subs) for expr in row] for row in matrix]
    variables = list(set(subs.values()))

    return new_matrix, variables


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

    all_minors = minors(matrix, variables)

    if not all_minors:
        return Integer(0)  # trivial case

    poly_gcd = reduce(gcd, all_minors)
    poly_gcd = normalize_polynomial(poly_gcd)
    poly_gcd = expand(poly_gcd.as_expr())  # convert to expression, TODO: make canonical work for Poly.
    poly_gcd = canonicalize_under_variable_permutation(poly_gcd, variables, allow_sign_change=True)

    return expand(poly_gcd)



def minors(matrix, variables, normalize=True):
    """Compute all (n-1)x(n-1) minors of an n x m matrix."""

    if not isinstance(matrix, Matrix):
        matrix = Matrix(matrix)

    n = matrix.rows
    m = matrix.cols

    if m < n - 1:
        raise ValueError("Cannot compute matrix minors (too few columns)")

    result = set()

    row_combinations = list(combinations(range(n), n - 1))
    col_combinations = list(combinations(range(m), n - 1))
    extract = matrix.extract

    for row_idx in row_combinations:
        for col_idx in col_combinations:
            submatrix = extract(row_idx, col_idx)
            det = submatrix.det(method='berkowitz')
            det = simplify(det)
            if det:
                poly = normalize_laurent_polynomial(det, variables)
                if poly:
                    poly = Poly(poly)
                    result.add(poly)

    variables_set = set(variables)
    for det in result:
        if not variables_set.issuperset(det.gens):
            raise ValueError("Minors are not polynomials")

    return result


def multivariable_alexander(k: PlanarDiagram | OrientedPlanarDiagram):
    """
    Compute the Alexander polynomial from the abelianized Alexander matrix.
    Returns the gcd of all (n-1)x(n-1) minors (up to units).
    """
    return alexander_multivariable(k)



if __name__ == '__main__':
    import knotpy as kp
    from time import time
    k = kp.from_pd_notation("PD[X[20, 2, 21, 1], X[7, 17, 8, 16], X[5, 1, 6, 10], X[3, 7, 4, 6], X[9, 5, 10, 4], X[14, 20, 15, 19], X[22, 14, 11, 13], X[12, 17, 13, 18], X[18, 11, 19, 12], X[2, 22, 3, 21], X[15, 9, 16, 8]]")

    t = time()
    p = alexander_multivariable(k)
    print(time() - t)


    t = time()
    p = alexander_multivariable(k)
    print(time() - t)

    print(p)
