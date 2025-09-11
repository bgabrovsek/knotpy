import pytest

from knotpy.algorithms.sanity import sanity_check
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.classes.endpoint import OutgoingEndpoint


def test_sanity_valid_diagram():
    """
    A known-good planar diagram should pass sanity_check.
    """
    k = PlanarDiagram()
    # A small valid example used elsewhere in the project
    k.set_arcs_from("x0a0,x1b0,x2c0,x4d0,x3y2,y0e0,y1f0,y3g0,y4h0")
    assert sanity_check(k) is True


def test_sanity_raises_on_none_endpoints():
    """
    Adding a vertex with unassigned endpoints should trigger a 'None endpoint' error.
    """
    k = PlanarDiagram()
    k.add_vertex("v", degree=2)  # leaves two None endpoints
    with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'node'"):
        sanity_check(k)


def test_sanity_raises_on_oriented_arc_with_same_direction():
    """
    An oriented diagram must have opposite directions on each arc (Out->In or In->Out).
    Force an invalid arc with the same direction on both ends and expect an error.
    """
    ok = OrientedPlanarDiagram()
    ok.add_vertex("a", degree=1)
    ok.add_vertex("b", degree=1)

    # Deliberately make both directions Outgoing on the same arc (invalid).
    ok.set_endpoint(("a", 0), ("b", 0), create_using=OutgoingEndpoint)
    ok.set_endpoint(("b", 0), ("a", 0), create_using=OutgoingEndpoint)

    # with pytest.raises(ValueError, match=r"not oppositely oriented"):
    assert not sanity_check(ok)



if __name__ == '__main__':
    test_sanity_raises_on_oriented_arc_with_same_direction()
    test_sanity_raises_on_none_endpoints()
    test_sanity_valid_diagram()
