import knotpy as kp
from knotpy import sanity_check


def test_orientation():
    k = kp.PlanarDiagram("3_1")
    o = kp.orient(k)
    u = kp.unorient(o)

    assert not k.is_oriented()
    assert o.is_oriented()
    assert not u.is_oriented()
    assert k == u

    assert sanity_check(k)
    assert sanity_check(o)
    assert sanity_check(u)

if __name__ == "__main__":
    test_orientation()