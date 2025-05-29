from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.notation.native import from_knotpy_notation
from knotpy.algorithms.sanity import sanity_check

def test_faces():
    code = "a=V(c1 c0 b0) b=V(a2 b2 b1) c=X(a1 a0 c3 c2)"
    k = from_knotpy_notation(code)
    assert sanity_check(k)
    length = sorted(list(len(f) for f in k.faces))
    assert length == [1, 1, 2, 6], f"Faces are of lengths {length}"

def test_hopf():
    k = from_knotpy_notation("b → X(c3 c2 c1 c0), c → X(b3 b2 b1 b0)")
    assert sanity_check(k)
    length = sorted(list(len(f) for f in k.faces))
    assert length == [2,2,2,2], f"Faces are of lengths {length}"

if __name__ == '__main__':
    test_faces()
    test_hopf()