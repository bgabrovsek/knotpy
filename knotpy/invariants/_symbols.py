# TODO: initialize the variables only if needed
from sympy import symbols

_a, _A, _l, _m, _t, _T, _v, _w, _x, _y, _z, _tmp = symbols("a A l m t T v w x y z tmp")  # assume them positive, so simplification works better.
_YAMADA_SIGMA = _A + 1 + _A ** (-1)
_KAUFFMAN_TERM = -_A ** 2 - _A ** (-2)
_HOMFLYPT_SUM_XYZ = -_x / _z - _y / _z  # P(A u B) = ((-_X - _Y) / _Z) P(A) * P(B)
_KAUFFMAN_2_VARIABLE_SUM = _a * _z ** (-1) + _a ** (-1) * _z ** (-1) - 1

SYMBOL_LOCALS = {"a": _a, "A": _A, "l": _l, "m": _m, "t": _t, "T": _T, "v": _v, "w": _w, "x": _x, "y": _y, "z": _z, "tmp": _tmp}