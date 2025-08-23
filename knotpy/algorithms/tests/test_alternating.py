import knotpy as kp

def test_is_alternating():
    assert kp.is_alternating(kp.knot("7_3"))
    assert not kp.is_alternating(kp.knot("8_19"))
    assert kp.is_alternating(kp.theta("t4_1"))

def test_face_alternating():
    k1, k2, k3 = kp.knot("3_1"), kp.knot("7_3"), kp.knot("8_19")
    assert all(kp.is_face_alternating(face) for face in k1.faces)
    assert all(kp.is_face_alternating(face) for face in k2.faces)
    assert not all(kp.is_face_alternating(face) for face in k3.faces)

if __name__ == "__main__":
    test_is_alternating()
    test_face_alternating()