# tests/test_laurent.py

import sympy as sp

from knotpy.utils.laurent import (
    reciprocal,
    normalize_laurent,
    normalize_symmetric,
    extract_variables,
    #canonicalize_under_variable_permutation,
    # tuples_to_laurent,
)


def test_reciprocal_roundtrip():
    x, y = sp.symbols("x y")
    expr = x**2 + x*y + 3
    r = reciprocal(expr, x)
    assert sp.simplify(r - (x**-2 + x**-1*y + 3)) == 0

    # Involutive in a single variable: recip(recip(f, x), x) == f
    rr = reciprocal(r, x)
    assert sp.simplify(rr - expr) == 0


def test_normalize_laurent_basic():
    x, y = sp.symbols("x y")
    poly = sp.Poly(x**3*y**2 + 2*x**2*y**5, x, y)
    norm = normalize_laurent(poly)
    # Divide by x^2 * y^2 → x*y^0 + 2*y^3
    assert sp.simplify(norm.as_expr() - (x + 2*y**3)) == 0


def test_normalize_laurent_polynomial_make_nonnegative():
    x, y = sp.symbols("x y")
    expr = x**-3 * y**2 + 2*x**-1
    norm = normalize_laurent(expr, variables=[x, y])
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

    canon = normalize_laurent(expr, variables=vars_, allow_variable_permutation=True)

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
    canon = normalize_laurent(expr, variables=vars_, allow_variable_permutation=True, allow_polynomial_sign_change=True)

    assert canon == 2*t1 - t2



def test_normalize_laurent_polynomial():
    from sympy import symbols, simplify
    x, y = symbols("x y")

    # Mixed positive and negative exponents
    expr1 = x * y**-2 + y**4 / x
    expected1 = simplify("x**2 + y**6")
    assert simplify(normalize_laurent(expr1, [x, y])) == expected1

    # Negative and positive exponents in one variable
    expr2 = -x**-3 + x**2
    expected2 = simplify("x**5 - 1")
    assert simplify(normalize_laurent(expr2, [x])) == expected2

    # Already a polynomial
    expr3 = x + 1
    expected3 = simplify("x + 1")
    assert normalize_laurent(expr3, [x]) == expected3

    # All negative exponents
    expr4 = x**-2 + x**-5
    expected4 = simplify("x**3 + 1")
    assert simplify(normalize_laurent(expr4, [x])) == expected4

    # All large positive exponents
    expr5 = x**10 * y**8 + x**7 * y**5
    expected5 = simplify("x**3 * y**3 + 1")  # already normalized
    assert normalize_laurent(expr5, [x, y]) == expected5, f"{normalize_laurent(expr5, [x, y])}"

    # All large negative exponents
    expr6 = x**-10 * y**-8 + x**-7 * y**-5
    expected6 = simplify("1 + x**3 * y**3")
    assert simplify(normalize_laurent(expr6, [x, y])) == expected6

    # Multiple variables with all negative exponents
    expr7 = x**-3 * y**-2 + x**-4 * y**-3
    expected7 = simplify("1 + x * y")
    assert simplify(normalize_laurent(expr7, [x, y])) == expected7


def test_laurent_tuples():
    p1 = sp.sympify("-t1*t2*(t3**-1) - t1 + 2*t2**2*t3 - t3 + 1")
    p2 = sp.Integer(9)
    p3 = sp.Rational(8,7)
    p4 = -1
    p5 = 0
    p6 = sp.sympify("2*x")

    from knotpy.utils.laurent import laurent_to_tuples, tuples_to_laurent



    t1,_ = laurent_to_tuples(p1)
    t2,_ = laurent_to_tuples(p2)
    t3,_ = laurent_to_tuples(p3)
    t4,_ = laurent_to_tuples(p4)
    t5,_ = laurent_to_tuples(p5)
    t6,_ = laurent_to_tuples(p6)


    assert set(t1) == { ((1,1,-1), -1), ((1,0,0), -1), ((0,2,1), 2), ((0,0,1), -1),  ((0,0,0), 1)}
    assert t2 == [((), 9)]
    assert t3 == [((), sp.Rational(8,7))]
    assert t4 == [((),-1)]
    assert t5 == [((), 0)]
    assert t6 == [((1,), 2)]

    assert tuples_to_laurent(t1, sp.symbols('t1 t2 t3')) == p1
    assert tuples_to_laurent(t2, ()) == p2
    assert tuples_to_laurent(t3,()) == p3
    assert tuples_to_laurent(t4,()) == p4
    assert tuples_to_laurent(t5,()) == p5
    assert tuples_to_laurent(t6,sp.symbols("x")) == p6


def test_alexander_cases():
    p1 = sp.sympify("-t1*t2*t3 + t1*t2 - t1 + t2*t3 - t3 + 1")
    p2 = sp.sympify("-t1*t2*t3 + t1*t2 + t1*t3 - t2 - t3 + 1")
    p3 = sp.sympify("-t1*t2*t3 + t1*t3 - t1 + t2*t3 - t2 + 1")
    p4 = sp.sympify("-t1*t2 - t1*t3 + t1 - t2*t3 + t2 + t3")

    q1 = normalize_laurent(p1, allow_variable_permutation=True, allow_variable_sign_change=True)
    q2 = normalize_laurent(p2, allow_variable_permutation=True, allow_variable_sign_change=True)
    q3 = normalize_laurent(p3, allow_variable_permutation=True, allow_variable_sign_change=True)
    q4 = normalize_laurent(p4, allow_variable_permutation=True, allow_variable_sign_change=True)


def test_laurent_div_2():
    t1, t2 = sp.symbols("x y")
    expr = 2*t1*t2 - 2*t1 - 2*t2 + 2
    result = normalize_laurent(expr, [t1, t2])
    assert result == expr

if __name__ == "__main__":
    test_laurent_tuples()
    test_alexander_cases()
    test_laurent_div_2()

    # Manual run support
    test_reciprocal_roundtrip()
    test_normalize_laurent_basic()
    test_normalize_laurent_polynomial_make_nonnegative()
    test_normalize_symmetric_centering_and_sign()
    test_extract_variables_with_and_without_prefix()
    test_canonicalize_under_variable_permutation_minimal_rep()
    test_canonicalize_under_permutation_with_sign_change()
    test_normalize_laurent_polynomial()
    print("All laurent tests passed.")
