from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.freezing import freeze

def test_freeze():
    k = PlanarDiagram("3_1")

    assert not k.is_frozen()
    freeze(k)
    assert k.is_frozen()

    try:
        k.add_vertex("z")
        assert False
    except RuntimeError:
        assert True

    try:
        k.set_endpoint(("a", 0), ("a", 1))
        assert False
    except RuntimeError:
        assert True

    try:
        k.framing = 1
        assert False
    except RuntimeError:
        assert True

    q = k.copy()
    assert not q.is_frozen()

    assert k == q
    assert k is not q

if __name__ == "__main__":
    test_freeze()