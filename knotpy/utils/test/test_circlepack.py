# test_circlepack.py

from knotpy.utils.circlepack import circle_pack, invert_packing, normalize_packing, invert_around


def test_basic_circle_pack():
    internal = {'A': ['B', 'C', 'D']}
    external = {'B': 1.0, 'C': 1.0, 'D': 1.0}
    packing = circle_pack(internal, external)

    assert isinstance(packing, dict)
    assert len(packing) == 4
    for k, (z, r) in packing.items():
        assert isinstance(z, complex | float | int)
        assert r > 0


def test_disjoint_key_check():
    try:
        circle_pack({'A': ['B']}, {'A': 1.0})
        assert False, "Expected ValueError for overlapping keys"
    except ValueError:
        pass


def test_negative_radius_check():
    try:
        circle_pack({'A': ['B']}, {'B': -1.0})
        assert False, "Expected ValueError for negative radius"
    except ValueError:
        pass


def test_inversion_preserves_count():
    internal = {'A': ['B', 'C', 'D']}
    external = {'B': 1.0, 'C': 1.0, 'D': 1.0}
    packing = circle_pack(internal, external)
    inverted = invert_packing(packing, 0)
    assert isinstance(inverted, dict)
    assert len(inverted) == len(packing)


def test_normalization():
    internal = {'A': ['B', 'C', 'D']}
    external = {'B': 1.0, 'C': 1.0, 'D': 1.0}
    packing = circle_pack(internal, external)
    smallest = min(packing.items(), key=lambda x: x[1][1])[0]
    normalized = normalize_packing(packing, smallest, target=5.0)

    _, r = normalized[smallest]
    assert abs(r - 5.0) < 1e-8


def test_invert_around():
    internal = {'A': ['B', 'C', 'D']}
    external = {'B': 1.0, 'C': 1.0, 'D': 1.0}
    packing = circle_pack(internal, external)
    inv = invert_around(packing, 'A')
    assert isinstance(inv, dict)
    assert len(inv) == len(packing)


if __name__ == "__main__":
    test_basic_circle_pack()
    test_disjoint_key_check()
    test_negative_radius_check()
    test_inversion_preserves_count()
    test_normalization()
    test_invert_around()
    print("All tests passed.")