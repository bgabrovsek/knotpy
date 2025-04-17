from knotpy.catalog.knot_tables import get_knot_from_name

def test_get_knot_from_name():

    # test links
    k = get_knot_from_name("L4a1{0}")
    assert len(k) == 4
    k = get_knot_from_name("L10a174{0;0;0;1}")
    assert len(k) == 10
    k = get_knot_from_name("L6a5")
    assert len(k) == 6
    k = get_knot_from_name("L8n1{0}")
    assert len(k) == 8
    k = get_knot_from_name("L10a174")
    assert len(k) == 10

    # test knots
    k = get_knot_from_name("3_1")
    assert len(k) == 3
    k = get_knot_from_name("10_136")
    assert len(k) == 10
    k = get_knot_from_name("12a_831")
    assert len(k) == 12
    k = get_knot_from_name("12n_127")
    assert len(k) == 12

    # test thetas, handcuffs
    k = get_knot_from_name("+t5_6")
    assert len(k) == 7
    k = get_knot_from_name("t6_15.2")
    assert len(k) == 10  # why 10?
    k = get_knot_from_name("h0_1")
    assert len(k) == 2
    k = get_knot_from_name("h2_1.1")
    assert len(k) == 4

    k = get_knot_from_name("0_1")
    assert len(k) == 1

    k = get_knot_from_name("unknot")
    assert len(k) == 1

    k = get_knot_from_name("trefoil")
    assert len(k) == 3

    k = get_knot_from_name("hopf")
    assert len(k) == 2

if __name__ == "__main__":
    test_get_knot_from_name()