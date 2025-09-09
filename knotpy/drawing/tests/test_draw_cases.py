import knotpy as kp

def test_oriented():
    return
    a = kp.knot("+3_1")
    kp.draw(a, show=True)

def test_connected_sum():
    return
    a = kp.knot("3_1")
    b = kp.knot("4_1")
    c = kp.connected_sum(a, b)
    kp.draw(c, show=True)

def test_disjoint_union():
    return
    a = kp.knot("3_1")
    b = kp.knot("4_1")
    c = kp.disjoint_union(a, b)
    kp.draw(c, show=True)

def test_trivial():
    return
    a = kp.knot("unknot")
    # ep = get_endpoints(a)
    # a = kp.reidemeister_1_add_kink(k, ())
    kp.draw(a, show=True)
    pass

def test_trivial_oriented():
    return
    a = kp.knot("unknot")
    a = kp.orient(a)
    kp.draw(a, show=True)
    pass

def test_trivial_disjoint_union():
    return
    a = kp.knot("unknot")
    b = kp.knot("unknot")
    c = kp.disjoint_union(a, b)
    kp.draw(c, show=True)

    a = kp.knot("unknot")
    b = kp.knot("trefoil")
    c = kp.disjoint_union(a, b)
    kp.draw(c, show=True)


def test_kinks():
    return
    a = kp.knot("6_2")
    for epp in [("f", 3), ("d", 0), ("a", 0), ("f", 1), ("a", 2), ("d", 1)]:
        ep = a.endpoint_from_pair(epp)
        a = kp.reidemeister_1_add_kink(a, (ep,1))
    kp.draw(a, show=True, label_endpoints=True, label_nodes=True)


def test_kinks_same_arc():
    a = kp.knot("6_2")
    for epp in [("f", 3), ("g", 3)]:
        ep = a.endpoint_from_pair(epp)
        a = kp.reidemeister_1_add_kink(a, (ep,1))
    #kp.draw(a, show=True, label_endpoints=True, label_nodes=True)



if __name__ == '__main__':
    test_oriented()
    test_disjoint_union()
    test_connected_sum()
    test_trivial()
    test_trivial_oriented()
    test_trivial_disjoint_union()
    test_kinks()
    test_kinks_same_arc()