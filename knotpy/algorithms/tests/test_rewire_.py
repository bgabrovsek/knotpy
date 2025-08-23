import pytest

from knotpy import PlanarDiagram, Crossing, sanity_check
from knotpy.algorithms.rewire import pull_and_plug_endpoint


def test_pull_and_plug_endpoint_sanity():
    k = PlanarDiagram()
    # initial diagram
    k.set_arcs_from("x0a0,x1y2,x2d0,y0e0,y1f0,y3g0,y4h0,f1d1")

    # must be sane before
    assert sanity_check(k)

    # move endpoint ("x",1) to position ("y",2)
    pull_and_plug_endpoint(k, source_endpoint=("x", 1), destination_endpoint=("y", 2))

    # and still be sane after
    assert sanity_check(k)

if __name__ == "__main__":
    pass
