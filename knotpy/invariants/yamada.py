"""
Implementation of the Yamada polynomial. The Yamada polynomial R is defined via the following relations:

  i. R(K+) = A R(K0) + A^(-1) R(K∞) + R(K•)
 ii. R(K ∪ e) = R(K / e) + R(K - e)
iii. R(K ∐ L) = R(K) * R(L)
 iv. R(K ∨ L) = - R(K) * R(L)
  v. if K has a cut edge, then R(K) = 0

Other relations (σ = A + 1 + A^(-1)):

  vi. R(loop) = σ
 vii. R(loop with other edges) = -σ R(loop removed)
viii. R(positive twist at vertex) = -A R(twist removed) - (A^2 + A) R(twist replaced by a non-edge)
  ix. R(negative twist at vertex) = -A^(-1) R(twist removed) - (A^(-2) + A^(-1)) R(twist replaced by a non-edge)
   x. R(3-valent positive twist at vertex) = -A R(twist removed)
  xi. R(3-valent negative twist at vertex) = -A^(-1) R(twist removed)
 xii. R(positive loop) = A^2 R(twist removed)
xiii. R(negative loop) = A^(-2) R(twist removed)

Additional relations
 xix. R(n-leafed bouquet) = -(σ)^n

https://en.wikipedia.org/wiki/Mathematical_operators_and_symbols_in_Unicode
"""
import sympy
from sympy import Symbol, Expr, symbols, expand

_A = symbols("A")
_sigma = (_A + 1 + _A**(-1))

print(_sigma)


#@single_variable_invariant('A')
def yamada(g, variable='A') -> Expr:
    A = variable if isinstance(variable, Symbol) else symbols(variable)

    print(sympy.expand(_sigma / A))
    return 0


print(yamada(2))