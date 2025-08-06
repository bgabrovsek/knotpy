import re
import sympy
from sympy import Poly, expand, symbols
from itertools import permutations
import sympy
from sympy import expand, simplify, Poly
from sympy import expand, simplify, S, symbols
from collections import defaultdict

def poly2str(poly):
    """Convert polynomial into a filename-type string"""
    s = str(poly)
    for x, y in ["/d", "*x", "+p", "-m", " _", "(o", ")z"]:
        s = s.replace(x, y)
    return s

def str2poly(s):
    """Convert a filename--type string into a polynomial"""
    for x, y in ["/d", "*x", "+p", "-m", " _", "(o", ")z"]:
        s = s.replace(y, x)
    return sympy.sympify(s)

def reciprocal(expr, var):
    if isinstance(var, str):
        var = sympy.symbols(var)
    return sympy.expand(expr.subs(var, var**(-1)))



def extract_variables(expr, prefix=None):
    """
    Extracts variables of the form <prefix><number> (e.g., x1, t2, a3) from a SymPy expression,
    and returns them sorted by the numeric index.

    Args:
        expr: A SymPy expression.
        prefix (str or None): If given, only symbols with this prefix are returned (e.g., 't' → t1, t2).
                              If None, returns all symbols matching <prefix><digits> sorted by (prefix, index).

    Returns:
        A list of SymPy symbols sorted by (prefix, index).
    """
    all_symbols = expr.free_symbols
    pattern = re.compile(r'^([a-zA-Z_]+)(\d+)$')

    extracted = []

    for sym in all_symbols:
        match = pattern.fullmatch(sym.name)
        if match:
            pfx, idx = match.groups()
            if prefix is None or pfx == prefix:
                extracted.append((pfx, int(idx), sym))

    # Sort by prefix then index
    sorted_syms = sorted(extracted, key=lambda tup: (tup[0], tup[1]))
    return [sym for _, _, sym in sorted_syms]

def laurent_polynomial_to_tuples(expr, var):
    """
    Converts a SymPy Laurent polynomial expression into a list of tuples representation.

    Args:
        expr (sympy.core.expr.Expr): The SymPy Laurent polynomial expression to convert.
        var (sympy.core.symbol.Symbol): The variable in the Laurent polynomial.

    Returns:
        list of tuples: Each tuple represents a term in the polynomial as (coefficient, exponent).
    """

    if isinstance(var, str):
        var = sympy.symbols(var)

    if not isinstance(var, sympy.Symbol):
        raise ValueError("The variable must be a SymPy Symbol")

    # Expand the expression to ensure all terms are separated
    expr = sympy.expand(expr)

    # Get the terms of the polynomial
    terms = expr.as_ordered_terms()

    # Convert the terms into tuples
    poly_tuples = []
    for term in terms:
        coeff = term.as_coeff_exponent(var)[0]
        exponent = term.as_coeff_exponent(var)[1]
        poly_tuples.append((coeff, exponent))

    return sorted(poly_tuples, key=lambda t: (t[1],t[0]))

#
#
# def normalize_positive_exponents(expr, variables=None):
#     """
#     Multiply expr by a monomial so that all exponents of each variable are ≥ 0,
#     and multiply by -1 if the leading coefficient is negative.
#     Works for Laurent polynomials (allows negative exponents).
#     """
#
#     if variables is None:
#         variables = extract_variables(expr)
#
#     expr = sympy.expand(expr)
#     terms = expr.as_ordered_terms()
#
#     # Initialize minimum exponents
#     min_exp = defaultdict(int)
#     for var in variables:
#         min_exp[var] = 0
#
#     # Determine minimal exponent for each variable across all terms
#     for term in terms:
#         powers = term.as_powers_dict()
#         for var in variables:
#             e = powers.get(var, 0)
#             min_exp[var] = min(min_exp[var], e)
#
#     # Build monomial multiplier to shift all exponents to ≥ 0
#     multiplier = 1
#     for var in variables:
#         if min_exp[var] < 0:
#             multiplier *= var**(-min_exp[var])
#
#     # Apply shift
#     shifted_expr = sympy.expand(expr * multiplier)
#
#     # Check leading coefficient
#     leading_term = shifted_expr.as_ordered_terms()[0]
#     if leading_term.could_extract_minus_sign():
#         shifted_expr *= -1
#
#     return sympy.simplify(shifted_expr)


def normalize_positive_exponents(expr, variables=None):
    """
    Normalize a (Laurent) polynomial by:
    - Dividing out the minimal powers of each variable (making all exponents ≥ 0).
    - Multiplying by -1 if the leading term has negative coefficient.

    This gives a canonical representative up to multiplication by monomials and ±1.

    Args:
        expr: A SymPy expression (e.g., Laurent polynomial).
        variables: Optional list of variables to consider. If None, auto-detects.

    Returns:
        A normalized SymPy expression.
    """
    expr = expand(expr)

    # Auto-detect variables if not provided
    if variables is None:
        variables = list(expr.free_symbols)

    if not variables:
        return simplify(expr)

    # Convert to terms and extract exponents
    terms = expr.as_ordered_terms()
    min_exp = {v: S.Infinity for v in variables}

    for term in terms:
        for v in variables:
            _, exp = term.as_coeff_exponent(v)
            min_exp[v] = min(min_exp[v], exp)

    # Build monomial to divide out
    factor = S.One
    for v in variables:
        if min_exp[v] != 0 and min_exp[v] != S.Infinity:
            factor *= v**min_exp[v]

    expr = expand(expr / factor)

    # Normalize sign: make leading coefficient positive
    lead = expr.as_ordered_terms()[0]
    coeff = lead.as_coeff_Mul()[0]
    if coeff.could_extract_minus_sign():
        expr *= -1

    return simplify(expr)

def normalize_symmetric(expr, variable):
    """
    Normalize a Laurent polynomial by shifting exponents so it's centered
    and symmetric under variable ↔ 1/variable. Also ensures leading coefficient is positive.
    """
    expr = sympy.expand(expr)
    terms = expr.as_ordered_terms()

    # Step 1: Get all exponents of the variable
    powers = []
    for term in terms:
        exp = term.as_powers_dict().get(variable, 0)
        powers.append(exp)

    # Step 2: Find min and max exponent
    min_exp, max_exp = min(powers), max(powers)

    # Step 3: Compute shift to center polynomial
    shift = -(max_exp + min_exp) // 2
    expr_shifted = sympy.expand(variable**shift * expr)

    # Step 4: Symmetrize: (f(t) + f(t^-1)) / 2
    expr_sym = sympy.expand((expr_shifted + expr_shifted.subs(variable, 1 / variable)) / 2)

    # Step 5: Ensure leading coefficient is positive
    leading_term = expr_sym.as_ordered_terms()[0]
    if leading_term.could_extract_minus_sign():
        expr_sym = -expr_sym

    return sympy.simplify(expr_sym)


def canonicalize_under_variable_permutation(expr, variables=None):
    """
    Canonicalize a polynomial expression up to permutation of variables.

    Args:
        expr: A SymPy expression
        variables: List of SymPy symbols to permute

    Returns:
        Canonical expression (minimal under lex order over all permutations)
    """
    if variables is None:
        variables = extract_variables(expr)
    expr = expand(expr)
    if not variables:
        return expr

    # Create temporary dummy variables (s1, s2, ...)
    dummy_vars = symbols(f's1:{len(variables) + 1}')

    # Mapping from variables to dummy and back
    to_dummy = dict(zip(variables, dummy_vars))
    expr_dummy = expr.subs(to_dummy)

    best_expr = None
    best_repr = None

    for perm in permutations(dummy_vars):
        # Map permuted dummy variables back to original t_i
        back_subs = {s: t for s, t in zip(perm, variables)}
        expr_perm = expand(expr_dummy.subs(back_subs))

        # Create polynomial in canonical variable order for comparison
        poly = Poly(expr_perm, *variables)
        #print("pol", poly)
        # Canonical representation: sorted monomial exponent+coefficient pairs
        monomial_repr = tuple(sorted(poly.as_dict().items()))

        if best_repr is None or monomial_repr < best_repr:
            best_repr = monomial_repr
            best_expr = expr_perm

    return best_expr

