import sympy


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