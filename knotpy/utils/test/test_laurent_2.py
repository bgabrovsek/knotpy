import knotpy as kp

def test_normalize_laurent():
    import sympy as sp

    x, y, z = sp.symbols("x y z")

    # --- constants ---
    expr1 = kp.normalize_laurent(7)
    expr2 = 7
    assert (expr1 - expr2) == 0

    expr1 = kp.normalize_laurent(-7)
    expr2 = -7
    assert (expr1 - expr2) == 0

    expr1 = kp.normalize_laurent(-7, allow_polynomial_sign_change=True)
    expr2 = 7
    assert (expr1 - expr2) == 0

    expr1 = kp.normalize_laurent(0)
    expr2 = 0
    assert (expr1 - expr2) == 0

    # --- single variable ---
    expr1 = kp.normalize_laurent(4 * x ** -3 + 8 * x ** 2, variables=[x])
    expr2 = 4 + 8 * x ** 5
    assert (expr1 - expr2) == 0

    expr1 = kp.normalize_laurent(3 * x ** 2 + 6, variables=[x])
    expr2 = 3 * x ** 2 + 6
    assert (expr1 - expr2) == 0

    expr1 = kp.normalize_laurent(x ** 2 + 3 * x ** 2 - 4, variables=[x])
    expr2 = 4 * x ** 2 - 4
    assert (expr1 - expr2) == 0

    expr1 = kp.normalize_laurent(-5 * x ** 3 + 2 * x, variables=[x], allow_polynomial_sign_change=False)
    expr2 = -5 * x ** 2 + 2
    assert (expr1 - expr2) == 0

    expr1 = kp.normalize_laurent(-5 * x ** 3 + 2 * x, variables=[x], allow_polynomial_sign_change=True)
    expr2 = 5 * x ** 2 - 2
    assert (expr1 - expr2) == 0

    # --- multiple variables ---
    expr1 = kp.normalize_laurent(3 * x ** -2 * y ** 5 + 6 * y ** 2, variables=[x, y])
    expr2 = 3 * y ** 3 + 6 * x ** 2
    assert (expr1 - expr2) == 0

    expr1 = kp.normalize_laurent(7 * x ** 2 * y ** -4 - y ** 4 + 9, variables=[x, y])
    expr2 = 7 * x ** 2 - y ** 8 + 9 * y ** 4
    assert (expr1 - expr2) == 0

    expr1 = kp.normalize_laurent(x ** 0 * y ** -1 + 2, variables=[x, y])
    expr2 = 1 + 2 * y
    assert (expr1 - expr2) == 0

    expr1 = kp.normalize_laurent(x ** -3 * y ** 5 + 2 * y, variables=[x, y])
    expr2 = y ** 4 + 2 * x ** 3
    assert (expr1 - expr2) == 0

    expr1 = kp.normalize_laurent(x ** -1 * y ** -2 + x * y, variables=[x, y])
    expr2 = kp.normalize_laurent(x ** -1 * y ** -2 + x * y, variables=[y, x])
    assert (expr1 - expr2) == 0

    # --- Poly and string inputs ---
    expr1 = kp.normalize_laurent(sp.Poly(3 * x ** 2 + 6, x), variables=[x])
    expr2 = 3 * x ** 2 + 6
    assert (expr1 - expr2) == 0

    expr1 = kp.normalize_laurent("4*x**-2 + 8", variables=[x])
    expr2 = 4 + 8 * x ** 2
    assert (expr1 - expr2) == 0

    # --- zero after expansion ---
    expr1 = kp.normalize_laurent(sp.expand(x - x), variables=[x])
    expr2 = 0
    assert (expr1 - expr2) == 0

    # --- normalize_sign with multiple vars ---
    expr1 = kp.normalize_laurent(-5 * x ** 2 * y ** 3 + 2 * x * y ** 3 + 7, variables=[x, y], allow_polynomial_sign_change=True)
    expr2 = 5 * x ** 2 * y ** 3 - 2 * x * y ** 3 - 7
    assert (expr1 - expr2) == 0

    # --- empty variables list (edge) ---
    expr1 = kp.normalize_laurent(3 * x ** -2 + 1, variables=[])
    expr2 = 3 * x ** -2 + 1
    assert (expr1 - expr2) == 0

    # Rational coefficients
    expr1 = kp.normalize_laurent(sp.Rational(3, 2) * x ** 2 + sp.Rational(5, 7), variables=[x])
    expr2 = sp.Rational(3, 2) * x ** 2 + sp.Rational(5, 7)
    assert (expr1 - expr2) == 0

    expr1 = kp.normalize_laurent(sp.Rational(-4, 9) * x ** -3 + sp.Rational(7, 5), variables=[x])
    # min exp = -3 → factor x**-3
    expr2 = sp.Rational(-4, 9) + sp.Rational(7, 5) * x ** 3
    assert (expr1 - expr2) == 0

    # Rational exponents (positive + negative)
    expr1 = kp.normalize_laurent(x ** sp.Rational(1, 2) + x ** sp.Rational(-1, 2), variables=[x])
    # min exp = -1/2 → factor x**-1/2
    expr2 = x + 1
    assert (expr1 - expr2) == 0

    expr1 = kp.normalize_laurent(sp.Rational(2, 3) * x ** sp.Rational(3, 2) + sp.Rational(5, 6) * x ** sp.Rational(1, 2),
                              variables=[x])
    # exps: 3/2, 1/2 → min = 1/2 → factor x**1/2
    expr2 = sp.Rational(2, 3) * x + sp.Rational(5, 6)
    assert (expr1 - expr2) == 0

    # Multiple variables with rational exponents
    expr1 = kp.normalize_laurent(x ** sp.Rational(1, 2) * y ** sp.Rational(-3, 2) + y ** sp.Rational(-1, 2),
                              variables=[x, y])
    # exps: (1/2,-3/2), (0,-1/2) → mins: (0, -3/2) → factor y**-3/2
    expr2 = x ** sp.Rational(1, 2) + y
    assert (expr1 - expr2) == 0

    expr1 = kp.normalize_laurent(
        sp.Rational(7, 4) * x ** sp.Rational(-5, 2) * y ** sp.Rational(3, 2) + sp.Rational(1, 2) * x ** sp.Rational(-1,
                                                                                                                    2) * y ** sp.Rational(
            5, 2), variables=[x, y])
    # exps: (-5/2, 3/2), (-1/2, 5/2) → mins: (-5/2, 3/2) → factor x**-5/2 * y**3/2
    expr2 = sp.Rational(7, 4) + sp.Rational(1, 2) * x ** 2 * y
    assert (expr1 - expr2) == 0

if __name__ == "__main__":
    test_normalize_laurent()