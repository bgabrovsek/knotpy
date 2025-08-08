# tests/test_laurent.py

import sympy as sp

from knotpy.utils.laurent import (
    reciprocal,
    normalize_polynomial,
    normalize_laurent_polynomial,
    normalize_symmetric,
    extract_variables,
    canonicalize_under_variable_permutation,
)


def test_reciprocal_roundtrip():
    x, y = sp.symbols("x y")
    expr = x**2 + x*y + 3
    r = reciprocal(expr, x)
    assert sp.simplify(r - (x**-2 + x**-1*y + 3)) == 0

    # Involutive in a single variable: recip(recip(f, x), x) == f
    rr = reciprocal(r, x)
    assert sp.simplify(rr - expr) == 0


def test_normalize_polynomial_basic():
    x, y = sp.symbols("x y")
    poly = sp.Poly(x**3*y**2 + 2*x**2*y**5, x, y)
    norm = normalize_polynomial(poly)
    # Divide by x^2 * y^2 → x*y^0 + 2*y^3
    assert norm.gens == (x, y)
    assert sp.simplify(norm.as_expr() - (x + 2*y**3)) == 0


def test_normalize_laurent_polynomial_make_nonnegative():
    x, y = sp.symbols("x y")
    expr = x**-3 * y**2 + 2*x**-1
    norm = normalize_laurent_polynomial(expr, variables=[x, y])
    # Minimal exponents: x: -3, y: 0 → multiply by x^-3 → divide by x**-3 → multiply by x**3
    # Expected: y**2 + 2*x**2
    assert sp.simplify(norm - (y**2 + 2*x**2)) == 0

    # Ensure leading term is positive
    lead_coeff = norm.as_ordered_terms()[0].as_coeff_Mul()[0]
    assert not lead_coeff.could_extract_minus_sign()


def test_normalize_symmetric_centering_and_sign():
    t = sp.symbols("t")
    # Already symmetric w.r.t. t ↔ 1/t, but with a potential shift
    expr = t**-2 + 3 + 2*t**2
    out = normalize_symmetric(expr, t)
    # Result should be symmetric and same up to overall sign; check symmetry:
    assert sp.simplify(out - out.subs(t, 1/t)) == 0

    # Leading term positive:
    lead_coeff = out.as_ordered_terms()[0].as_coeff_Mul()[0]
    assert not lead_coeff.could_extract_minus_sign()


def test_extract_variables_with_and_without_prefix():
    t1, t2, t10 = sp.symbols("t1 t2 t10")
    x2, a3 = sp.symbols("x2 a3")
    expr = 2*t2 + t10 + 5*x2 + a3

    ts = extract_variables(expr, prefix="t")
    # Sorted by numeric index → [t2, t10]
    assert ts == [t2, t10]

    all_idx = extract_variables(expr)
    # Mixed prefixes allowed, sorted by (prefix, index) → [a3, t2, t10, x2]
    assert all_idx == [a3, t2, t10, x2]


def _poly_repr_for_compare(expr, vars_):
    """Helper: canonical representation used in canonicalization test."""
    poly = sp.Poly(sp.expand(expr), *vars_)
    return tuple(sorted(poly.as_dict().items()))


def test_canonicalize_under_variable_permutation_minimal_rep():
    # Intentionally asymmetric to force a choice
    t1, t2 = sp.symbols("t1 t2")
    expr = 3*t1**2 + 2*t1*t2 + t2  # asymmetric in t1, t2
    vars_ = (t1, t2)

    canon = canonicalize_under_variable_permutation(expr, variables=vars_, allow_sign_change=False)

    # Compute both permutations (identity and swap), pick lexicographically minimal monomial representation
    expr_id = sp.expand(expr)
    expr_swapped = sp.expand(expr.subs({t1: t2, t2: t1}))

    rep_id = _poly_repr_for_compare(expr_id, vars_)
    rep_swapped = _poly_repr_for_compare(expr_swapped, vars_)

    rep_min = min(rep_id, rep_swapped)
    rep_canon = _poly_repr_for_compare(canon, vars_)

    assert rep_canon == rep_min
    # And canon should equal one of the permutations exactly
    assert sp.simplify(canon - expr_id) == 0 or sp.simplify(canon - expr_swapped) == 0


def test_canonicalize_under_permutation_with_sign_change():
    t1, t2 = sp.symbols("t1 t2")
    expr = t1 - 2*t2
    vars_ = (t1, t2)

    canon = canonicalize_under_variable_permutation(expr, variables=vars_, allow_sign_change=True)

    # Consider {id, swap} × {±1}
    candidates = [
        expr,
        -expr,
        expr.subs({t1: t2, t2: t1}),
        -expr.subs({t1: t2, t2: t1}),
    ]
    reps = [_poly_repr_for_compare(e, vars_) for e in candidates]
    rep_best = min(reps)

    assert _poly_repr_for_compare(canon, vars_) == rep_best



def test_normalize_laurent_polynomial():
    from sympy import symbols, simplify
    x, y = symbols("x y")

    # Mixed positive and negative exponents
    expr1 = x * y**-2 + y**4 / x
    expected1 = simplify("x**2 + y**6")
    assert simplify(normalize_laurent_polynomial(expr1, [x, y])) == expected1

    # Negative and positive exponents in one variable
    expr2 = -x**-3 + x**2
    expected2 = simplify("x**5 - 1")
    assert simplify(normalize_laurent_polynomial(expr2, [x])) == expected2

    # Already a polynomial
    expr3 = x + 1
    expected3 = simplify("x + 1")
    assert normalize_laurent_polynomial(expr3, [x]) == expected3

    # All negative exponents
    expr4 = x**-2 + x**-5
    expected4 = simplify("x**3 + 1")
    assert simplify(normalize_laurent_polynomial(expr4, [x])) == expected4

    # All large positive exponents
    expr5 = x**10 * y**8 + x**7 * y**5
    expected5 = simplify("x**3 * y**3 + 1")  # already normalized
    assert normalize_laurent_polynomial(expr5, [x, y]) == expected5, f"{normalize_laurent_polynomial(expr5, [x, y])}"

    # All large negative exponents
    expr6 = x**-10 * y**-8 + x**-7 * y**-5
    expected6 = simplify("1 + x**3 * y**3")
    assert simplify(normalize_laurent_polynomial(expr6, [x, y])) == expected6

    # Multiple variables with all negative exponents
    expr7 = x**-3 * y**-2 + x**-4 * y**-3
    expected7 = simplify("1 + x * y")
    assert simplify(normalize_laurent_polynomial(expr7, [x, y])) == expected7

if __name__ == "__main__":
    # Manual run support
    test_reciprocal_roundtrip()
    test_normalize_polynomial_basic()
    test_normalize_laurent_polynomial_make_nonnegative()
    test_normalize_symmetric_centering_and_sign()
    test_extract_variables_with_and_without_prefix()
    test_canonicalize_under_variable_permutation_minimal_rep()
    test_canonicalize_under_permutation_with_sign_change()
    test_normalize_laurent_polynomial()
    print("All laurent tests passed.")
