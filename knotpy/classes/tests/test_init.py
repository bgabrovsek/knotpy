from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.tables.knot import knot

def test_knot_name():
    k = PlanarDiagram("3_1")
    print(k)
    assert k.name == "3_1"
    assert len(k) == 3

    l = knot("3_1")
    ll = knot("3_1")
    assert not (l is k)
    assert not (l is ll)

if __name__ == "__main__":
    test_knot_name()