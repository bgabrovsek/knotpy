from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.catalog.knot_tables import get_knot_from_name
def test_knot_name():
    k = PlanarDiagram("3_1")
    assert k.name == "3_1"
    assert len(k) == 3

    l = get_knot_from_name("3_1")
    ll = get_knot_from_name("3_1")
    assert not (l is k)
    assert not (l is ll)

if __name__ == "__main__":
    test_knot_name()