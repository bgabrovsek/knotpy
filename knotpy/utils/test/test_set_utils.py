from knotpy.utils.set_utils import LeveledSet


def test_leveled_set():
    # level 0
    ls = LeveledSet([1, 2, 3])

    ls.new_level()
    ls.extend([10, 11, 1, 2])

    ls.new_level()
    ls.add(2)
    ls.add(20)
    ls.add(21)
    ls.add(10)
    ls.add(22)

    assert set(ls) == {1, 2, 3, 10, 11, 20, 21, 22}
    assert ls.levels == [{1, 2, 3}, {10, 11}, {20, 21, 22}]

    assert 1 in ls
    assert 4 not in ls
    assert 10 in ls
    assert 20 in ls
    assert 30 not in ls

    assert ls[0] == {1, 2, 3}
    assert ls[1] == {10, 11}
    assert ls[2] == {20, 21, 22}
    assert ls[3] == set()
    assert ls[-1] == {20, 21, 22}
    assert ls[-2] == {10, 11}

if __name__ == '__main__':
    test_leveled_set()