import knotpy as kp

def test_adjacent():
    k = kp.knot("6_2")
    assert kp.is_adjacent(k, "a", "b")
    assert not kp.is_adjacent(k, "a", "e")

    ep1 = k.endpoint_from_pair(("a", 0))
    ep2 = k.endpoint_from_pair(("a", 1))
    ep3 = k.endpoint_from_pair(("b", 0))
    assert kp.is_adjacent(k, ep1, ep2)
    assert not kp.is_adjacent(k, ep1, ep3)



if __name__ == '__main__':
    test_adjacent()