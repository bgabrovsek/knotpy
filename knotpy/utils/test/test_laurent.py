from knotpy.utils.laurent import canonicalize_under_variable_permutation, extract_variables
from sympy import symbols, simplify

import knotpy as kp

def test_canonical_laurent():
    from sympy import symbols

    t1, t2 = symbols('t1 t2')
    expr = 1 + t1 + t1 * t2 ** 6

    print(extract_variables(expr))
    print(canonicalize_under_variable_permutation(expr, [t1, t2]))


def test_normalize_laurent_polynomial():
    x, y = symbols("x y")

    # Mixed positive and negative exponents
    expr1 = x * y**-2 + y**4 / x
    expected1 = simplify("x**2 + y**6")
    assert simplify(kp.normalize_laurent_polynomial(expr1, [x, y])) == expected1

    # Negative and positive exponents in one variable
    expr2 = -x**-3 + x**2
    expected2 = simplify("x**5 - 1")
    assert simplify(kp.normalize_laurent_polynomial(expr2, [x])) == expected2

    # Already a polynomial
    expr3 = x + 1
    expected3 = simplify("x + 1")
    assert kp.normalize_laurent_polynomial(expr3, [x]) == expected3

    # All negative exponents
    expr4 = x**-2 + x**-5
    expected4 = simplify("x**3 + 1")
    assert simplify(kp.normalize_laurent_polynomial(expr4, [x])) == expected4

    # All large positive exponents
    expr5 = x**10 * y**8 + x**7 * y**5
    expected5 = simplify("x**3 * y**3 + 1")  # already normalized
    assert kp.normalize_laurent_polynomial(expr5, [x, y]) == expected5, f"{kp.normalize_laurent_polynomial(expr5, [x, y])}"

    # All large negative exponents
    expr6 = x**-10 * y**-8 + x**-7 * y**-5
    expected6 = simplify("1 + x**3 * y**3")
    assert simplify(kp.normalize_laurent_polynomial(expr6, [x, y])) == expected6

    # Multiple variables with all negative exponents
    expr7 = x**-3 * y**-2 + x**-4 * y**-3
    expected7 = simplify("1 + x * y")
    assert simplify(kp.normalize_laurent_polynomial(expr7, [x, y])) == expected7

    print("All extended tests passed.")
if __name__ == "__main__":
    test_canonical_laurent()
    test_normalize_laurent_polynomial()