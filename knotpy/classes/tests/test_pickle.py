import pickle
import knotpy as kp

def test_pickability():
    k1 = kp.knot("3_1")
    k2 = kp.knot("10_10")
    k3 = kp.from_knotpy_notation("a=V(b0) b=X(a0 c0 d3 c1) c=X(b1 b3 d2 e0) d=X(f3 e1 c2 b2) e=X(c3 d1 f2 g3) f=X(g2 h3 e2 d0) g=X(h2 h0 f0 e3) h=X(g1 i0 g0 f1) i=V(h1)")
    k4 = kp.from_knotpy_notation("a=V(b3) b=X(c0 d0 c1 a0) c=X(b0 b2 d3 e3) d=X(b1 f0 f3 c2) e=X(g0 h0 h3 c3) f=X(d1 h2 h1 d2) g=V(e0) h=X(e1 f2 f1 e2)")
    k4.attr["color"] = "blue"

    for obj in [k1, k2, k3, k4]:
        pickled = pickle.dumps(obj)
        unpickled = pickle.loads(pickled)
        assert obj == unpickled, "Unpickled object is not equal to the original"


if __name__ == "__main__":
    test_pickability()