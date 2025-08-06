import knotpy as kp


def test_get_knots():

    # get one knot
    k = kp.knot("3_1")
    assert k.name == "3_1" and len(k) == 3 and isinstance(k, kp.PlanarDiagram)
    q = kp.knot("trefoil")
    assert q == k
    assert not k.is_frozen()
    assert q is not k

    # get more knots
    ks = kp.knots(crossings=6)
    assert all(len(k)==6 for k in ks)


def test_get_thetas():
    # get one knot
    k = kp.theta("T3_1")
    print(k, len(k), k.name)
    print(k.name == "T3_1", len(k) == 5 , isinstance(k, kp.PlanarDiagram))
    assert k.name == "T3_1" and len(k) == 5 and isinstance(k, kp.PlanarDiagram)
    q = kp.theta("theta")
    assert q != k
    assert not k.is_frozen()
    assert q is not k

    # get more knots
    ks = kp.thetas(crossings=5)
    assert all(len(k) == 7 for k in ks)


#
# def test_get_links():
#
#     # get one knot
#
#     k = kp.link("L6a1")
#     assert len(k) == 6 and isinstance(k, kp.PlanarDiagram)
#
#     assert not k.is_frozen()
#
#     # get more knots
#
#     ks = kp.links(crossings=6)
#     print(ks)
#     assert all(len(k)==6 for k in ks)


if __name__ == "__main__":
    test_get_knots()
    test_get_thetas()
    #test_get_links()