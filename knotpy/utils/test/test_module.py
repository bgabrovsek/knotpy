from knotpy.utils.module import module


def test_module():
    m = module(2, "c") + module(15, "a") - module(3, "x")

    assert set(m.to_tuple()) == {(-3, 'x'), (15, 'a'), (2, 'c')}

    m += module(1, "x")
    assert set(m.to_tuple()) == {(-2, 'x'), (15, 'a'), (2, 'c')}

    m += module(2, "x")
    assert set(m.to_tuple()) == {(15, 'a'), (2, 'c')}

    m2 = module(-15, "a") + module(7, "d")
    m3 = m + m2
    assert set(m3.to_tuple()) == {(2, 'c'), (7, 'd')}

    m3 *= 3
    assert set(m3.to_tuple()) == {(6, 'c'), (21, 'd')}

    assert set((m3 * 2).to_tuple()) == {(12, 'c'), (42, 'd')}
    assert set((m3 * 0).to_tuple()) == set()

    m3["c"] = module(7, "z") + module(-20, "d")
    # print(m3)
    # assert set(m3.to_tuple()) == {(6*7, 'z'), (1, 'd')}
    # fix: remove zeroes

if __name__ == '__main__':
    test_module()