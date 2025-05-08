from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.notation.native import from_knotpy_notation
from knotpy.algorithms.sanity import sanity_check

def test_faces():
    code = "a=V(c1 c0 b0) b=V(a2 b2 b1) c=X(a1 a0 c3 c2)"
    k = from_knotpy_notation(code)
    assert sanity_check(k)
    for f in k.faces:
        print(f)


if __name__ == '__main__':
    test_faces()