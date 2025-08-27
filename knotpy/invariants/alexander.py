# knotpy/invariants/alexander.py
"""
Alexander polynomials (one-variable and multivariable).
"""

from __future__ import annotations

__all__ = ["alexander", "multivariable_alexander", "alexander_multivariable"]
__version__ = "0.2"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

import sympy as sp
from collections import deque
from itertools import combinations
from functools import reduce

from knotpy.notation.native import to_knotpy_notation
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.invariants.homflypt import homflypt
from knotpy.algorithms.orientation import orient
from knotpy.algorithms.components_link import link_components_endpoints
from knotpy.invariants.fundamental_group import fundamental_group, alexander_fox_matrix
from knotpy.invariants._symbols import _t, _x, _y, _z, _T
from knotpy.utils.laurent import normalize_symmetric,   normalize_laurent
from knotpy.reidemeister.simplify import simplify_decreasing
from knotpy.algorithms.components_link import enumerate_link_components
from knotpy.invariants.homflypt import _choose_crossing_for_switching
from knotpy.invariants.skein import smoothen_crossing
from knotpy.algorithms.symmetry import mirror

_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]

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
    polynomial = homflypt(k, variables="xyz")
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
    return normalize_laurent(polynomial, variables=[_t])


def _check_component_consistency(k:OrientedPlanarDiagram):
    comp = link_components_endpoints(k)
    for c in comp:
        enum = {ep.attr["component"] for ep in c}
        if len(enum) != 1:
            raise ValueError(f"Error joining link components: {len(enum)} distinct enumerations found on one component")


# def _multivariate_alexander_skein(k: OrientedPlanarDiagram) -> sp.Expr:
#     """Compute the multivariate Alexander polynomial via skein relations algorithm."""
#     k = enumerate_link_components(k, inplace=False)
#
#     k.attr["_coefficient"] = sp.Integer(1)
#     stack: deque[OrientedPlanarDiagram] = deque([k])
#     polynomial = sp.Integer(0)
#
#     while stack:
#         k = stack.pop()
#         print(k)
#         #k = simplify_decreasing(k, inplace=True)
#
#         k, crossing = _choose_crossing_for_switching(k, sum_coefficient=sp.Integer(0))
#
#         if crossing is not None:
#             print("crossing", crossing)
#             crossing_enums = [k.nodes[crossing][i].attr["component"] for i in range(4)]  # get component enumerations
#             if crossing_enums[0] != crossing_enums[2] or crossing_enums[1] != crossing_enums[3]:  # check if the enumeration it is consistent
#                 raise ValueError(f"Crossing {crossing} is not a symmetry point")
#
#             # make the skein switches
#             k_switch = mirror(k, [crossing], inplace=False)
#             k_smooth = smoothen_crossing(k, crossing, method="O", inplace=False)
#
#             # in the smoothened state, we join enumeration of the i and j components, both to either t_i or t_j
#             lce = link_components_endpoints(k_smooth)
#             for component in lce:
#                 enums = {ep.attr["component"] for ep in component}
#                 if len(enums) == 2:
#                     new_index = min(enums)
#                     for ep in component:
#                         ep.attr["component"] = new_index
#                 elif len(enums) != 1:
#                     raise ValueError(f"Error joining link components: {len(enums)} distinct enumerations found")
#
#             _check_component_consistency(k_smooth)
#             _check_component_consistency(k_switch)
#
#
#         else:
#             pass

#
# def collapse_generators_by_components(
#     matrix: sp.Matrix,
#     eps_gen_dict: dict[object, object],
#     component_endpoints: list[set[object]],
# ) -> tuple[sp.Matrix, list[sp.Symbol]]:
#     """Collapse multiple free-group generators to one symbol per component.
#
#     Args:
#         matrix: Alexander–Fox matrix (entries are SymPy expressions).
#         eps_gen_dict: Map from endpoints to generator symbols.
#         component_endpoints: One set of endpoints per link component.
#
#     Returns:
#         A tuple ``(new_matrix, variables)`` where:
#         - ``new_matrix`` is the matrix with generators substituted by ``t1, t2, ...``.
#         - ``variables`` is the list ``[t1, t2, ...]`` used in the substitution.
#     """
#     # Create a substitution dictionary mapping each generator to a t-variable
#     subs: dict[object, sp.Symbol] = {}
#     for idx, endpoint_set in enumerate(component_endpoints):
#         t = sp.symbols(f"t{idx + 1}")
#         for ep in endpoint_set:
#             subs[eps_gen_dict[ep]] = t
#
#     # Replace FreeGroupElement keys with their base generator symbol
#     FreeGroupElement = sp.combinatorics.free_groups.FreeGroupElement
#     subs = {
#         (k.array_form[0][0] if isinstance(k, FreeGroupElement) else k): v
#         for k, v in subs.items()
#     }
#
#     # Apply the substitution to each entry in the matrix
#     M = matrix.applyfunc(lambda e: e.subs(subs))
#     variables = list(set(subs.values()))
#     return M, variables
#

def collapse_generators_by_components(
    matrix: sp.Matrix,
    eps_gen_dict: dict[object, object],
    component_endpoints: list[set[object]],
) -> tuple[sp.Matrix, list[sp.Symbol]]:
    """Collapse multiple free-group generators to one symbol per component."""
    # deterministic variables t1, t2, ...
    variables: list[sp.Symbol] = [sp.symbols(f"t{i+1}") for i in range(len(component_endpoints))]

    # map endpoints -> their component variable
    subs: dict[object, sp.Symbol] = {}
    for idx, endpoint_set in enumerate(component_endpoints):
        t = variables[idx]
        for ep in endpoint_set:
            subs[eps_gen_dict[ep]] = t

    # unwrap FreeGroupElement keys if present
    FreeGroupElement = sp.combinatorics.free_groups.FreeGroupElement
    subs = {(k.array_form[0][0] if isinstance(k, FreeGroupElement) else k): v for k, v in subs.items()}

    # substitute in the matrix
    M = matrix.applyfunc(lambda e: e.subs(subs))

    # sanity: only our t_i’s should remain
    extra = M.free_symbols - set(variables)
    if extra:
        raise ValueError(f"Unexpected symbols after collapse: {sorted(extra, key=str)}")

    return M, variables


def _monomial_power_in_den(expr, v):
    den = sp.together(expr).as_numer_denom()[1]
    return int(den.as_powers_dict().get(v, 0))

def clear_denominators_by_columns(M, variables):
    """
    Multiply each column j by a monomial in `variables` so all entries
    become polynomials in those variables.
    """
    ncols = M.cols
    colmons = []
    for j in range(ncols):
        mon = sp.Integer(1)
        for v in variables:
            emax = 0
            for i in range(M.rows):
                emax = max(emax, _monomial_power_in_den(M[i, j], v))
            if emax:
                mon *= v**emax
        colmons.append(sp.simplify(mon))

    D = sp.diag(*colmons)
    M_poly = (M * D).applyfunc(sp.together).applyfunc(sp.cancel)
    return M_poly, colmons

# def _monomial_power_in_den(expr, v):
#     """Exponent of variable v appearing in the denominator of expr."""
#     den = sp.together(expr).as_numer_denom()[1]
#     return int(den.as_powers_dict().get(v, 0))
#
# def clear_denominators_by_columns(M, variables):
#     """
#     Multiply each column j by a monomial in `variables` so all entries
#     become polynomials in those variables.
#     """
#     ncols = M.cols
#     colmons = []
#     for j in range(ncols):
#         exps = []
#         for v in variables:
#             emax = 0
#             for i in range(M.rows):
#                 emax = max(emax, _monomial_power_in_den(M[i, j], v))
#             exps.append((v, emax))
#         mon = sp.Integer(1)
#         for v, e in exps:
#             if e:
#                 mon *= v**e
#         colmons.append(sp.simplify(mon))
#
#     D = sp.diag(*colmons)             # right-multiply → scales columns
#     M_poly = (M * D).applyfunc(sp.together).applyfunc(sp.cancel)
#     return M_poly, colmons

def normalize_up_to_monomial(expr, variables):
    """
    Remove a global monomial factor in `variables` from a (Laurent) polynomial.
    Expressions differing by t1^a * t2^b * ... normalize to the same form.
    """
    if expr == 0:
        return sp.Integer(0)
    poly = sp.Poly(expr, *variables, domain=sp.QQ)
    mins = [min(e[i] for e in poly.monoms()) for i in range(len(variables))]
    mon = sp.Integer(1)
    for v, m in zip(variables, mins):
        if m:
            mon *= v**m
    return sp.simplify(expr / mon)

def all_n_minus_1_minors_up_to_monomial(M, variables, method="bareiss"):
    """
    Compute all (n-1)x(n-1) minors of a square matrix M, after clearing
    denominators ONCE by column scaling, and return the set of unique
    determinants normalized up to monomials in `variables`.
    """
    n, m = M.shape
    if n != m:
        raise ValueError("Matrix must be square to compute (n-1)x(n-1) minors.")
    if n <= 1:
        return set()

    # 1) Clear denominators once
    M_poly, _ = clear_denominators_by_columns(M, variables)

    # 2) Compute all (n-1)x(n-1) minors
    unique_minors = set()
    extract = M_poly.extract
    for i in range(n):
        rows = [r for r in range(n) if r != i]
        for j in range(n):
            cols = [c for c in range(n) if c != j]
            sub = extract(rows, cols)
            det = sp.simplify(sp.Matrix(sub).det(method=method))
            if det:
                det_norm = normalize_laurent(det, variables)   # <— YOUR normalizer
                if det_norm:
                    unique_minors.add(sp.simplify(det_norm))
    return unique_minors


def _to_ZZ_poly(expr: sp.Expr, vars_: list[sp.Symbol]) -> sp.Poly:
    """
    Convert an expression into a ZZ polynomial in vars_,
    clearing rational denominators across all coefficients.
    """
    # Expand into sum of monomials
    expr = sp.expand(expr)
    terms = sp.Add.make_args(expr)

    # collect all denominators of coefficients
    dens = []
    for term in terms:
        coeff, _ = term.as_coeff_mul(*vars_)
        if coeff.is_Rational:
            dens.append(coeff.q)   # denominator
    lcm_den = sp.ilcm(*dens) if dens else 1

    # clear denominators
    Ez = sp.expand(expr * lcm_den)
    return sp.Poly(Ez, *vars_, domain="ZZ")

def stream_n_minus_1_minors_gcd(
    matrix: sp.Matrix | list[list[sp.Expr]],
    variables: list[sp.Symbol],
    *,
    method: str = "bareiss",
    debug: bool = False,
) -> sp.Poly:
    """Streaming gcd of all (n-1)x(n-1) minors over ZZ[variables], preserving integer content."""
    M = matrix if isinstance(matrix, sp.Matrix) else sp.Matrix(matrix)
    M, _ = clear_denominators_by_columns(M, variables)

    n, m = M.rows, M.cols
    if m < n - 1:
        raise ValueError("Cannot compute matrix minors (too few columns).")

    poly_gcd: sp.Poly | None = None
    extract = M.extract
    row_combos = combinations(range(n), n - 1)
    col_combos_all = list(combinations(range(m), n - 1))

    for rows in row_combos:
        for cols in col_combos_all:
            sub = extract(rows, cols)
            # det
            try:
                from sympy.polys.matrices import DomainMatrix
                from sympy.polys.domains import ZZ
                R = ZZ.poly_ring(*variables)
                det_expr = DomainMatrix.from_Matrix(sub, domain=R).det().to_sympy()
            except Exception:
                det_expr = sp.Matrix(sub).det(method=method)

            if det_expr == 0:
                continue

            det_expr = normalize_laurent(det_expr, variables)  # your normalizer
            if det_expr == 0:
                continue

            Pz = _to_ZZ_poly(det_expr, variables)  # <-- integer polynomial
            if poly_gcd is None:
                poly_gcd = Pz
            else:
                poly_gcd = sp.polys.polytools.gcd(poly_gcd, Pz)

            if debug:
                print(f"gcd deg={poly_gcd.total_degree()} LC={poly_gcd.LC()}")

            # Early exit if gcd is ±1 in ZZ
            if poly_gcd.total_degree() == 0 and abs(int(poly_gcd.LC())) == 1:
                return poly_gcd

    return poly_gcd if poly_gcd is not None else sp.Poly(0, *variables, domain='ZZ')

# def all_n_minus_1_minors_up_to_monomial(M, variables, method="bareiss"):
#     """
#     Compute all (n-1)x(n-1) minors of a square matrix M, after clearing
#     denominators ONCE by column scaling, and return the set of unique
#     determinants normalized up to monomials in `variables`.
#     """
#     n, m = M.shape
#     if n != m:
#         raise ValueError("Matrix must be square to compute (n-1)x(n-1) minors.")
#     if n <= 1:
#         return set()
#
#     # 1) Clear denominators once
#     M_poly, _ = clear_denominators_by_columns(M, variables)
#
#     # 2) Compute all (n-1)x(n-1) minors
#     unique_minors = set()
#     for i in range(n):
#         rows = [r for r in range(n) if r != i]
#         for j in range(n):
#             cols = [c for c in range(n) if c != j]
#             sub = M_poly.extract(rows, cols)
#             det = sub.det(method=method)
#             det_norm = normalize_up_to_monomial(det, variables)
#             unique_minors.add(sp.simplify(det_norm))
#
#     return unique_minors


def all_unique_n_minus_1_minors(matrix, variables, normalize=True, debug=False):
    """
    Compute all unique (n-1)x(n-1) minors of `matrix`, up to multiplication by a monomial
    in `variables` (if `normalize=True`). Returns a set of `sympy.Poly` objects.

    Parameters
    ----------
    matrix : sympy.Matrix | array-like
        Input matrix (possibly with rational functions in `variables`).
    variables : sequence of sympy.Symbol
        The variables used for normalization / domain.
    normalize : bool
        If True, normalize each determinant up to a monomial factor in variables.
    debug : bool
        If True, prints minimal progress info.

    Returns
    -------
    set[sympy.Poly]
        Set of unique minors as Polys in the given `variables`.
    """
    from sympy.polys.matrices import DomainMatrix
    from sympy.polys.domains import QQ

    M = matrix if isinstance(matrix, sp.Matrix) else sp.Matrix(matrix)

    # 1) Clear denominators once (by columns) to get polynomial entries
    M, _ = clear_denominators_by_columns(M, variables)
    if debug:
        print("Denominators cleared.")

    n, m = M.rows, M.cols
    if m < n - 1:
        raise ValueError("Cannot compute matrix minors (too few columns).")

    # polynomial ring QQ[variables]
    R = QQ.poly_ring(*variables)

    # Pre-bind for speed
    extract = M.extract
    result: set[sp.Poly] = set()

    row_combinations = list(combinations(range(n), n - 1))
    col_combinations = list(combinations(range(m), n - 1))

    for row_idx in row_combinations:
        for col_idx in col_combinations:
            sub = extract(row_idx, col_idx)

            # 2) determinant over the polynomial ring via DomainMatrix
            try:
                DM = DomainMatrix.from_Matrix(sub, domain=R)
                det_dom = DM.det()                 # element of the ring
                det = det_dom.to_sympy()
            except Exception:
                # Fallback to fraction-free Bareiss on the polynomial matrix
                det = sp.Matrix(sub).det(method="bareiss")

            if det == 0:
                continue

            # 3) optional normalization "up to monomial"
            if normalize:
                det = normalize_laurent(det, variables)

            if det == 0:
                continue

            # 4) store as Poly with fixed generators for consistent hashing
            poly = sp.Poly(det, *variables, domain=QQ)
            result.add(poly)

            if debug:
                print("minor ok")

    return result

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
    M, _ = clear_denominators_by_columns(M, variables)
    print("clear denoms")
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
            print("det...")
            print("*submatrix")
            print(submatrix)
            det = submatrix.det(method="berkowitz") # test berkowitz and bareiss
            print("* det", det)
            det = sp.simplify(det)
            print("* simplify", det)
            if det:
                poly_expr = normalize_laurent(det, variables) if normalize else det
                if poly_expr:
                    poly = sp.Poly(poly_expr)
                    result.add(poly)
    variables_set = set(variables)
    for det_poly in result:
        if not variables_set.issuperset(det_poly.gens):
            raise ValueError("Minors are not polynomials in the provided variables.")

    return result


def multivariable_alexander(k: "PlanarDiagram | OrientedPlanarDiagram") -> sp.Expr:
    k = k.copy() if k.is_oriented() else orient(k)
    G, eps_gen_dict = fundamental_group(k, return_dict=True)
    A = alexander_fox_matrix(G)

    component_endpoints = link_components_endpoints(k)
    M, variables = collapse_generators_by_components(A, eps_gen_dict, component_endpoints)

    poly_gcd = stream_n_minus_1_minors_gcd(M, variables, method="bareiss", debug=False)
    if poly_gcd.is_zero:
        return sp.Integer(0)

    # DO NOT primitive(); keep the common integer factor, e.g., 2
    expr = normalize_laurent(
        poly_gcd.as_expr(),
        variables,
        allow_variable_permutation=True,
        allow_polynomial_sign_change=True,
    )
    return sp.expand(expr)

alexander_multivariable = multivariable_alexander

if __name__ == "__main__":
    import knotpy as kp
    k = kp.link("L8a1+")
    print(k)
    # k = kp.from_pd_notation("PD[X[6, 1, 7, 2], X[12, 7, 13, 8], X[4, 13, 1, 14], X[9, 18, 10, 15], X[8, 4, 9, 3], X[5, 17, 6, 16], X[17, 5, 18, 14], X[15, 10, 16, 11], X[2, 12, 3, 11]]")
    # k = kp.orient(k)
    #draw(k, label_endpoints=True, label_nodes=True)
    poly = multivariable_alexander(k)
    print("poly FOX", poly)


    # t = time()
    # poly = multivariable_alexander_interpolation(k)
    # print("poly FOX", poly)
    # print("time FOX", time() - t)
    #
    # #_multivariate_alexander_skein(k)
    # pass
