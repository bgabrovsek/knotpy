from knotpy.utils.laurent import canonicalize_under_variable_permutation, extract_variables
from sympy import symbols
def test_canonical_laurent():
    from sympy import symbols

    t1, t2 = symbols('t1 t2')
    expr = 1 + t1 + t1 * t2 ** 6

    print(extract_variables(expr))
    print(canonicalize_under_variable_permutation(expr, [t1, t2]))


if __name__ == "__main__":
    test_canonical_laurent()