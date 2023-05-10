import sympy
from sympy import Symbol, Expr, symbols, expand
from knotpy.utils.decorators import single_variable_invariant

a = symbols("a")
b = symbols("a")


@single_variable_invariant('A')
def yamada(g, variable='A') -> Expr:

    return 0

v = a*a + 5*a*b + 7/a/b-1
#print(v, isinstance(v, sympy.core.Expr))

from sympy import symbols
x = symbols('x')

print(expand((3+x)/x/x))
print(expand((1+x)/x/x))