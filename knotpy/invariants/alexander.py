# knotpy/invariants/alexander.py
"""
Alexander polynomials (one-variable and multivariable).
"""

from __future__ import annotations

__all__ = ["alexander", "multivariable_alexander", "alexander_multivariable"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

import sympy as sp
from itertools import combinations
from functools import reduce

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.invariants.homflypt import homflypt_xyz
from knotpy.algorithms.orientation import orient
from knotpy.algorithms.components_link import link_components_endpoints
from knotpy.invariants.fundamental_group import fundamental_group, alexander_fox_matrix
from knotpy.invariants._symbols import _t, _x, _y, _z
from knotpy.utils.laurent import (
    normalize_symmetric,
    normalize_laurent_polynomial,
    canonicalize_under_variable_permutation,
    normalize_polynomial,
)


def alexander(k: PlanarDiagram | OrientedPlanarDiagram, symmetric: bool = False) -> sp.Expr:
    """Compute the one-variable Alexander polynomial via HOMFLY-PT specialization.

    Args:
        k: Planar diagram of a knot or link. If not oriented, it will be oriented internally.
        symmetric: If True, normalize to a symmetric (palindromic) representative.

    Returns:
        A SymPy expression in ``t`` representing the Alexander polynomial.

    Notes:
        Uses the substitution ``x=1``, ``y=-1``, ``z=-(t**1/2) + (t**(-1/2))`` on HOMFLY-PT.

    Examples:
        >>> # K is a diagram of the trefoil (example; adjust to your construction)
        >>> # alexander(K)
        t**2 - t + 1
    """
    polynomial = homflypt_xyz(k)
    polynomial = sp.expand(
        polynomial.subs(
            {
                _x: sp.Integer(1),
                _y: sp.Integer(-1),
                _z: -_t ** sp.Rational(1, 2) + _t ** sp.Rational(-1, 2),
            }
        )
    )
    if symmetric:
        return normalize_symmetric(polynomial)
    return normalize_laurent_polynomial(polynomial, variables=[_t])


def collapse_generators_by_components(
    matrix: sp.Matrix,
    eps_gen_dict: dict[object, object],
    component_endpoints: list[set[object]],
) -> tuple[sp.Matrix, list[sp.Symbol]]:
    """Collapse multiple free-group generators to one symbol per component.

    Args:
        matrix: Alexander–Fox matrix (entries are SymPy expressions).
        eps_gen_dict: Map from endpoints to generator symbols.
        component_endpoints: One set of endpoints per link component.

    Returns:
        A tuple ``(new_matrix, variables)`` where:
        - ``new_matrix`` is the matrix with generators substituted by ``t1, t2, ...``.
        - ``variables`` is the list ``[t1, t2, ...]`` used in the substitution.
    """
    # Create a substitution dictionary mapping each generator to a t-variable
    subs: dict[object, sp.Symbol] = {}
    for idx, endpoint_set in enumerate(component_endpoints):
        t = sp.symbols(f"t{idx + 1}")
        for ep in endpoint_set:
            subs[eps_gen_dict[ep]] = t

    # Replace FreeGroupElement keys with their base generator symbol
    FreeGroupElement = sp.combinatorics.free_groups.FreeGroupElement
    subs = {
        (k.array_form[0][0] if isinstance(k, FreeGroupElement) else k): v
        for k, v in subs.items()
    }

    # Apply the substitution to each entry in the matrix
    M = matrix.applyfunc(lambda e: e.subs(subs))
    variables = list(set(subs.values()))
    return M, variables


def alexander_multivariable(k: PlanarDiagram | OrientedPlanarDiagram) -> sp.Expr:
    """Compute the multivariable Alexander polynomial from the abelianized Alexander matrix.

    This returns the gcd (up to units) of all ``(n-1)×(n-1)`` minors of the Alexander–Fox
    matrix after collapsing generators to one variable per link component.

    Args:
        k: Planar diagram (knot or link). If not oriented, it will be oriented internally.

    Returns:
        A SymPy expression in variables ``t1, t2, ...`` (one per component).

    Raises:
        ValueError: If minors cannot be computed due to matrix shape.
    """
    k = k.copy() if k.is_oriented() else orient(k)

    G, eps_gen_dict = fundamental_group(k, return_dict=True)
    A = alexander_fox_matrix(G)

    component_endpoints = link_components_endpoints(k)
    matrix, variables = collapse_generators_by_components(A, eps_gen_dict, component_endpoints)

    all_minors = minors(matrix, variables)

    if not all_minors:
        return sp.Integer(0)

    # Polynomial gcd over Poly objects
    poly_gcd = reduce(sp.polys.polytools.gcd, all_minors)
    poly_gcd = normalize_polynomial(poly_gcd)

    # Convert to Expr for canonicalization under variable permutations
    expr = sp.expand(poly_gcd.as_expr())
    expr = canonicalize_under_variable_permutation(expr, variables, allow_sign_change=True)
    return sp.expand(expr)


def minors(
    matrix: sp.Matrix | list[list[sp.Expr]],
    variables: list[sp.Symbol],
    normalize: bool = True,
) -> set[sp.Poly]:
    """Compute all ``(n-1)×(n-1)`` minors of an ``n×m`` matrix.

    Args:
        matrix: Matrix or list-of-lists of SymPy expressions.
        variables: Variables to check/normalize as Laurent polynomials.
        normalize: If True, normalize each determinant as a Laurent polynomial in ``variables``.

    Returns:
        A set of ``sp.Poly`` objects representing the minors.

    Raises:
        ValueError: If there are too few columns to form ``(n-1)×(n-1)`` minors.
        ValueError: If some determinant is not a polynomial in ``variables``.
    """
    M = matrix if isinstance(matrix, sp.Matrix) else sp.Matrix(matrix)

    n = M.rows
    m = M.cols
    if m < n - 1:
        raise ValueError("Cannot compute matrix minors (too few columns).")

    result: set[sp.Poly] = set()

    row_combinations = list(combinations(range(n), n - 1))
    col_combinations = list(combinations(range(m), n - 1))
    extract = M.extract

    for row_idx in row_combinations:
        for col_idx in col_combinations:
            submatrix = extract(row_idx, col_idx)
            det = submatrix.det(method="berkowitz")
            det = sp.simplify(det)
            if det:
                poly_expr = normalize_laurent_polynomial(det, variables) if normalize else det
                if poly_expr:
                    poly = sp.Poly(poly_expr)
                    result.add(poly)

    variables_set = set(variables)
    for det_poly in result:
        if not variables_set.issuperset(det_poly.gens):
            raise ValueError("Minors are not polynomials in the provided variables.")

    return result


def multivariable_alexander(k: PlanarDiagram | OrientedPlanarDiagram) -> sp.Expr:
    """Alias for :func:`alexander_multivariable`."""
    return alexander_multivariable(k)


if __name__ == "__main__":
    pass
