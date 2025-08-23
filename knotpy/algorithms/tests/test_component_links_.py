import knotpy as kp

def test_number_of_link_components():
    k31 = kp.knot("3_1")
    k813 = kp.knot("8_13")
    l2a1 = kp.link("L2a_1++")
    l6a5 = kp.link("L6a_5+++")


    assert kp.number_of_link_components(k31) == 1
    assert kp.number_of_link_components(k813) == 1
    assert kp.number_of_link_components(l2a1) == 2
    assert kp.number_of_link_components(l6a5) == 3

if __name__ == '__main__':
    test_number_of_link_components()