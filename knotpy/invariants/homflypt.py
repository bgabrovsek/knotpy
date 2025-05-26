from sympy import symbols, Symbol

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.orientation import orient

def homflypt_polynomial(k:PlanarDiagram):
    """Return the HOMFLYPT polynomial of a knot k."""
    l, m = symbols(("l", "m"))

    if not k.is_oriented():
        k = orient(k)



    pass

if __name__ == '__main__':
    import knotpy as kp
    k = kp.PlanarDiagram("3_1")
    print(k)
    o = orient(k)
    for o in orient(k):
        print(o)