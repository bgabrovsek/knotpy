from sympy.combinatorics.fp_groups import FpGroup
from sympy.combinatorics.free_groups import free_group, FreeGroupElement
from sympy import Integer, symbols, simplify, expand, fraction, gcd, Poly, Matrix
from itertools import combinations
from functools import reduce

from knotpy.classes.endpoint import IngoingEndpoint
from knotpy.classes.planardiagram import OrientedPlanarDiagram
from knotpy.algorithms.topology import overstrands as get_overstrands

"""
Relations
Positive crossing: xi * xj * x(i+1)**-1 * xj**-1 = 1
Negative crossing: xi * xj**-1 * x(i+1)**-1 * xj = 1
Vertex: x1**s1 * x2**s1 * ..., where s1 == 1 if the arc is directed into the vertex, -1 if out of the vertex


"""

def alexander_fox_matrix(G: FpGroup):
    """Compute the Fox Jacobian of the finitely presented group G."""
    return [[fox_derivative(relator, generator) for generator in G.generators] for relator in G.relators]

def get_monomial_to_clear_negatives(expressions, variables):
    """
    Compute the monomial needed to eliminate all negative exponents across
    a list of Laurent polynomials. Returns a product of variables raised
    to positive powers as needed.
    """
    min_exponents = {v: 0 for v in variables}

    for expr in expressions:
        for term in expand(expr).as_ordered_terms():
            powers = term.as_powers_dict()
            for v in variables:
                exp = powers.get(v, 0)
                if exp < min_exponents[v]:
                    min_exponents[v] = exp

    factor = 1
    for v in variables:
        e = min_exponents[v]
        if e < 0:
            factor *= v ** (-e)

    return factor


def normalize_minors(minors_list, variables):
    """
    Normalize a list of Laurent polynomials by multiplying all expressions
    by a single monomial to remove all negative exponents.

    No simplification is performed, only expansion.
    """
    factor = get_monomial_to_clear_negatives(minors_list, variables)
    normalized = [expand(factor * expr) for expr in minors_list]
    return normalized, factor

# def get_common_denominator_factor(expressions, variables):
#     """Find monomial t1^n * t2^m * ... to clear all denominators."""
#     max_exponents = {v: 0 for v in variables}
#     for expr in expressions:
#         for term in expand(expr).as_ordered_terms():
#             _, denom = fraction(term)
#             for var in variables:
#                 exp = denom.as_powers_dict().get(var, 0)
#                 if exp < 0:
#                     max_exponents[var] = max(max_exponents[var], -exp)
#                 else:
#                     max_exponents[var] = max(max_exponents[var], exp)
#     factor = 1
#     for var, exp in max_exponents.items():
#         factor *= var**exp
#     return factor
#
# def normalize_minors(minors_list, variables):
#     """Multiply all minors by the same factor to make them polynomials."""
#     F = get_common_denominator_factor(minors_list, variables)
#     return [simplify(expand(F * expr)) for expr in minors_list], F

def gcd_of_minors(minors_list, variables):
    poly_minors, factor = normalize_minors(minors_list, variables)
    return factor, reduce(gcd, poly_minors)

def minors(matrix):
    """Compute all (n-1)x(n-1) minors of an n x m matrix."""
    if not isinstance(matrix, Matrix):
        matrix = Matrix(matrix)

    n = matrix.rows
    m = matrix.cols

    if m < n - 1:
        raise ValueError("Cannot compute matrix minors (too few columns)")

    result = []

    row_combos = list(combinations(range(n), n - 1))
    col_combos = list(combinations(range(m), n - 1))

    # Use local variable to avoid attribute lookup in loop
    extract = matrix.extract
    append = result.append

    for row_idx in row_combos:
        for col_idx in col_combos:
            submatrix = extract(row_idx, col_idx)
            append(submatrix.det(method='berkowitz'))  # faster symbolic method

    return result

def old_minors(matrix):
    """Compute n-1 minors."""
    if not isinstance(matrix, Matrix):
        matrix = Matrix(matrix)

    n = matrix.rows  # number of rows
    m = matrix.cols  # number of columns
    if m < n - 1:
        raise ValueError("Cannot compute matrix minors (too few rows)")

    result = []
    row_combos = list(combinations(range(n), n - 1))
    col_combos = list(combinations(range(m), n - 1))

    for rows in row_combos:
        for cols in col_combos:
            result.append(matrix.extract(rows, cols).det())

    return result

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

def fox_derivative(relator: FreeGroupElement, variable, abelize=True):
    """
    ∂x_j/∂x_i = 1 if i == j else 0
    ∂e/∂x_i = 0
    ∂(uv)/∂x_i = ∂u/∂x_i + u * ∂v/∂x_i
    ∂(u**-1)/∂x_i = - u**-1 *  ∂u/∂x_i

    Exanmple:
    d(x * y * x * y**-1 * x**-1 * y**-1)/dx = 1 + xy - xyxy^-1 x^-1
    Args:
        relator:
        variable:

    Returns:

    """
    # print("relator", relator, type(relator))
    # print("variable", variable, type(variable))

    if not abelize:
        raise NotImplementedError("Non-abelized fox derivative not implemented.")

    if isinstance(variable, FreeGroupElement):
        variable = variable.array_form[0][0]

    derivative = Integer(0)
    multiplier = Integer(1)
    for var, exp in relator.array_form:
        if var == variable:
            if exp not in [-1, 1]:
                raise ValueError("Exponent expected to be +1 or -1")
            derivative += multiplier if exp == 1 else - multiplier * (var ** -1)
        multiplier *= var ** exp
    return derivative
#
#
# def fox_derivative(word, generator):
#     result = 0
#     coeff = 1
#     print(type(generator))
#     for symb, power in word.array_form:
#         if symb == generator:
#             result += coeff if power == 1 else -coeff * generator**(-1)
#         coeff *= generator**power  # This only works if 'generator' supports arithmetic as in group ring
#
#     return result


def fundamental_group(k: OrientedPlanarDiagram, return_dict=False):
    """Return a presentation of the fundamental group of the complement of k in S^3."""
    if not k.is_oriented():
        raise TypeError("Cannot compute the fundamental group of an unoriented planar diagram")
    overstrands = sorted(get_overstrands(k))
    F, *generators = free_group(" ".join(f"x{i}" for i in range(len(overstrands))))  # generators are 'x1', 'x2', ...
    overstrand_generator = {ep: generator for strand, generator in zip(overstrands, generators) for ep in strand}
    # print(overstrand_generator)
    relators = []
    for c in k.crossings:
        ep0, ep1, ep2, ep3 = k.endpoints[c]
        # TODO: the relation can be simplified
        if k.sign(c) > 0:
            if isinstance(ep0, IngoingEndpoint):
                relators.append(overstrand_generator[ep0] * overstrand_generator[ep1] * (overstrand_generator[ep2] ** -1) * (overstrand_generator[ep3]**-1))
            else:
                relators.append(overstrand_generator[ep2] * overstrand_generator[ep1] * (overstrand_generator[ep0] ** -1) * (overstrand_generator[ep3]**-1))
        else:
            if isinstance(ep0, IngoingEndpoint):
                relators.append(overstrand_generator[ep0] * (overstrand_generator[ep1]**-1) * (overstrand_generator[ep2] ** -1) * overstrand_generator[ep3])
            else:
                relators.append(overstrand_generator[ep2] * (overstrand_generator[ep1]**-1) * (overstrand_generator[ep0] ** -1) * overstrand_generator[ep3])

    for v in k.vertices:
        eps = k.endpoints[v]
        relator = overstrand_generator[eps[0]] ** (-1 if isinstance(eps[0], IngoingEndpoint) else 1)
        for ep in eps[1:]:
            relator *= overstrand_generator[ep] ** (-1 if isinstance(ep, IngoingEndpoint) else 1)
        relators.append(relator)

    if return_dict:
        return FpGroup(F, relators), overstrand_generator
    else:
        return FpGroup(F, relators)

if __name__ == '__main__':
    pass