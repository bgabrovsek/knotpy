
import knotpy as kp

def test_alternating():
    print(kp.knot("7_3"))
    assert kp.is_alternating(kp.knot("7_3"))
    print(kp.knot("8_19"))
    assert not kp.is_alternating(kp.knot("8_19"))
    assert kp.is_alternating(kp.theta("t4_1"))


if __name__ == "__main__":
    test_alternating()