import knotpy as kp

def test_nothing():
    f = kp.PlanarDiagram
    g = kp.OrientedPlanarDiagram
    assert f != g


if __name__ == "__main__":
    test_nothing()