import knotpy as kp
import sympy as sp

from knotpy.invariants.alexander import clear_denominators_by_columns

def test_alexander_minors_functions():
    t1, t2 = sp.symbols('t1 t2')
    variables = [t1, t2]

    M = sp.Matrix([
        [-t2, t1-1,  1,         0, 0, 0, 0, 0, 0],
        [0,     0,  -1 + 1/t1, -1/t1, 1, 0, 0, 0, 0],
        [0,     -t1, 0,         0, t2-1, 1, 0, 0, 0],
        [t1-1,  0,   0,         0, 0, 0, -t1, 1, 0],
        [0,     0,  -1/t2,      0, 0, -t1/t2 + 1/t2, 1, 0, 0],
        [1,     0,   0,         0, 0, 0, 0, t1-1, -t1],
        [0,     0,   0,         1, 0, 0, 0, -t1, t1-1],
        [0,     0,   0,         0, -t1, 0, t1-1, 0, 1],
        [0,     1,   0,         -t2/t1 + 1/t1, 0, -1/t1, 0, 0, 0],
    ])
    M_poly, colmons = clear_denominators_by_columns(M, variables)
    for j in range(M_poly.cols):  # iterate over column indices
        col = M_poly[:, j]  # take all rows in column j
        print(f"Column {j}:", col)

if __name__ == '__main__':
    test_alexander_minors_functions()