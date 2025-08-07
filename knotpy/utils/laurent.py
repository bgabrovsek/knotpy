import re
from itertools import permutations
from sympy import expand, simplify, S, symbols, Expr, Poly, Symbol

# def poly2str(poly):
#     """Convert polynomial into a filename-type string"""
#     s = str(poly)
#     for x, y in ["/d", "*x", "+p", "-m", " _", "(o", ")z"]:
#         s = s.replace(x, y)
#     return s
#
# def str2poly(s):
#     """Convert a filename--type string into a polynomial"""
#     for x, y in ["/d", "*x", "+p", "-m", " _", "(o", ")z"]:
#         s = s.replace(y, x)
#     return sympify(s)

def reciprocal(expr, var):
    if isinstance(var, str):
        var = symbols(var)
    return expand(expr.subs(var, var**(-1)))


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
        expr (core.expr.Expr): The SymPy Laurent polynomial expression to convert.
        var (core.symbol.Symbol): The variable in the Laurent polynomial.

    Returns:
        list of tuples: Each tuple represents a term in the polynomial as (coefficient, exponent).
    """

    if isinstance(var, str):
        var = symbols(var)

    if not isinstance(var, Symbol):
        raise ValueError("The variable must be a SymPy Symbol")

    # Expand the expression to ensure all terms are separated
    expr = expand(expr)

    # Get the terms of the polynomial
    terms = expr.as_ordered_terms()

    # Convert the terms into tuples
    poly_tuples = []
    for term in terms:
        coeff = term.as_coeff_exponent(var)[0]
        exponent = term.as_coeff_exponent(var)[1]
        poly_tuples.append((coeff, exponent))

    return sorted(poly_tuples, key=lambda t: (t[1],t[0]))


def normalize_polynomial(poly: Poly) -> Poly:
    """
    Normalize a multivariate polynomial by dividing out the minimal exponent of each variable,
    so that the result has the minimal possible support (lowest exponents starting at 0).

    Args:
        poly (Poly): A SymPy Poly object with positive exponents.

    Returns:
        Poly: The normalized Poly object.
    """
    gens = poly.gens
    monoms = poly.monoms()

    if not monoms:
        return poly  # Zero polynomial

    # Find minimum exponent for each variable across all monomials
    min_exps = [min(m[i] for m in monoms) for i in range(len(gens))]

    # Build the monomial factor to divide out
    shift_monomial = {gen: exp for gen, exp in zip(gens, min_exps)}
    factor = S.One
    for g, e in shift_monomial.items():
        if e:
            factor *= g ** e

    return Poly(poly.as_expr() / factor, *gens)

def normalize_laurent_polynomial(expr: Expr, variables=None, normalize_sign: bool = True) -> Expr:
    """
    Normalize a (Laurent) polynomial by:
    - Making all exponents of the specified variables non-negative.
    - Optionally flipping the sign so that the leading term has a positive coefficient.

    This produces a canonical form up to multiplication by monomials and ±1.

    Args:
        expr (Expr): The SymPy expression to normalize.
        variables (Optional[Iterable]): Variables to consider.
            If None, all free symbols in `expr` are used.
        normalize_sign (bool): If True, ensures the leading term has a positive coefficient.

    Returns:
        Expr: The normalized polynomial.
    """
    expr = expand(expr)

    if variables is None:
        variables = list(expr.free_symbols)

    if not variables:
        return expr

    terms = expr.as_ordered_terms()
    min_exp = {v: S.Infinity for v in variables}

    for term in terms:
        for v in variables:
            _, exp = term.as_coeff_exponent(v)
            min_exp[v] = min(min_exp[v], exp)

    factor = S.One
    for v in variables:
        exp = min_exp[v]
        if exp != 0 and exp != S.Infinity:
            factor *= v ** exp

    expr = expand(expr / factor)

    if normalize_sign:
        lead_coeff = expr.as_ordered_terms()[0].as_coeff_Mul()[0]
        if lead_coeff.could_extract_minus_sign():
            expr = -expr

    return expr

def normalize_symmetric(expr, variable):
    """
    Normalize a Laurent polynomial by shifting exponents so it's centered
    and symmetric under variable ↔ 1/variable. Also ensures leading coefficient is positive.
    """
    expr = expand(expr)
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
    expr_shifted = expand(variable**shift * expr)

    # Step 4: Symmetrize: (f(t) + f(t^-1)) / 2
    expr_sym = expand((expr_shifted + expr_shifted.subs(variable, 1 / variable)) / 2)

    # Step 5: Ensure leading coefficient is positive
    leading_term = expr_sym.as_ordered_terms()[0]
    if leading_term.could_extract_minus_sign():
        expr_sym = -expr_sym

    return simplify(expr_sym)


def canonicalize_under_variable_permutation(expr, variables=None, allow_sign_change=False):
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
    variables = sorted(variables, key=str)
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

        if best_repr is None or monomial_repr > best_repr:
            best_repr = monomial_repr
            best_expr = expr_perm

        if allow_sign_change:
            # Canonical representation: sorted monomial exponent+coefficient pairs
            expr_perm = expand(-expr_perm)
            poly = Poly(expr_perm, *variables)
            monomial_repr = tuple(sorted(poly.as_dict().items()))
            if monomial_repr > best_repr:
                best_repr = monomial_repr
                best_expr = expr_perm
        #print("bestest", best_expr)
    return best_expr
