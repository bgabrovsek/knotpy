import knotpy as kp
from knotpy import export_pdf


def test_reverse():

    # test reverible knot

    print("a")
    ko = kp.orientations(kp.knot("3_1"))
    assert len(ko) == 2
    ko = {kp.canonical(_) for _ in ko}
    assert len(ko) == 1

    # test irreverisble knot
    # chiral
    print("b")
    ko = kp.orientations(kp.knot("9_32"))
    ko = {kp.canonical(_) for _ in ko}
    a, b = ko
    a1 = kp.canonical(kp.reverse(a))
    a2 = kp.canonical(kp.flip(kp.reverse(a)))

    assert a != a1
    assert a != a2

    print("c")

    # positive achiral chiral
    ko = kp.orientations(kp.knot("12a_427"))
    ko = {kp.canonical(_) for _ in ko}
    a, b = ko
    a1 = kp.canonical(kp.reverse(a))
    a2 = kp.canonical(kp.flip(kp.reverse(a)))


    assert a != a1
    assert a != a2


if __name__ == "__main__":
    test_reverse()
