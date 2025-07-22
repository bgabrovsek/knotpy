
import knotpy as kp

def test_alternating():
    assert kp.is_alternating(kp.knot("7_3"))
    assert not kp.is_alternating(kp.knot("8_19"))
    assert kp.is_alternating(kp.theta("-t5_7"))


if __name__ == "__main__":
    test_alternating()