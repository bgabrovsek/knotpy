from knotpy.tables.knot import knot

def DO_NOT_test_get_link_from_name():
    # test links
    k = link("L4a1{0}")
    assert len(k) == 4
    k = link("L10a174{0;0;0;1}")
    assert len(k) == 10
    k = link("L6a5")
    assert len(k) == 6
    k = link("L8n1{0}")
    assert len(k) == 8
    k = link("L10a174")
    assert len(k) == 10

    k = link("hopf")
    assert len(k) == 2

def DO_NOTtest_get_theta_from_name():
    #test thetas, handcuffs
    k = theta("+t5_6")
    assert len(k) == 7
    k = theta("t6_15.2")
    assert len(k) == 10  # why 10?
    k = theta("h0_1")
    assert len(k) == 2
    k = theta("h2_1.1")
    assert len(k) == 4


def test_get_knot_from_name():



    # test knots
    k = knot("3_1")
    assert len(k) == 3
    k = knot("10_136")
    assert len(k) == 10
    k = knot("12a_831")
    assert len(k) == 12
    k = knot("12n_127")
    assert len(k) == 12


    k = knot("0_1")
    assert len(k) == 1

    k = knot("unknot")
    assert len(k) == 1

    k = knot("trefoil")
    assert len(k) == 3



if __name__ == "__main__":
    test_get_knot_from_name()