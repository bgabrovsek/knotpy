from knotpy.utils.set_utils import LeveledSet
import knotpy as kp
from time import time
#

# tests/test_set_utils.py

import pytest
from knotpy.utils.set_utils import powerset, LeveledSet


def test_powerset_basic():
    ps = list(powerset([1, 2, 3]))
    assert ps == [
        (),
        (1,),
        (2,),
        (3,),
        (1, 2),
        (1, 3),
        (2, 3),
        (1, 2, 3),
    ]


def test_leveledset_no_conversion_basic_levels_and_counts():
    ls = LeveledSet[int, int]([1, 2])
    assert ls.number_of_levels() == 1
    assert ls.level_sizes() == (2,)
    assert ls.number_of_items() == 2

    # new level is created because last level is non-empty
    ls.new_level([3])
    assert ls.number_of_levels() == 2
    assert ls.level_sizes() == (2, 1)
    assert ls.number_of_items() == 3

    # adding duplicate doesn't increase counts
    ls.add(2)
    assert ls.number_of_items() == 3
    assert sorted(list(ls)) == [1, 2, 3]


def test_leveledset_iter_level_indexing_and_errors():
    ls = LeveledSet[int, int]([1, 2])
    ls.new_level([3, 4])

    assert list(ls.iter_level(0)) == [1, 2] or set(ls.iter_level(0)) == {1, 2}
    assert set(ls.iter_level(1)) == {3, 4}
    assert set(ls.iter_level(-1)) == {3, 4}

    with pytest.raises(IndexError):
        _ = list(ls.iter_level(2))


def test_leveledset_remove_empty_levels_trailing_only():
    ls = LeveledSet[int, int]([1])
    ls.new_level([2])
    ls.new_level()  # creates an empty level because previous level is non-empty
    assert ls.number_of_levels() == 3
    assert ls.level_sizes() == (1, 1, 0)

    ls.remove_empty_levels()
    assert ls.number_of_levels() == 2
    assert ls.level_sizes() == (1, 1)


def test_leveledset_contains_and_extend():
    ls = LeveledSet[str, str]()
    assert not ls.contains("a")
    ls.extend(["a", "b", "a"])
    assert ls.contains("a")
    assert set(ls) == {"a", "b"}
    assert ls.number_of_items() == 2


def test_leveledset_with_conversion_roundtrip_and_ops():
    # store externally as tuples, internally as strings
    to_s = lambda t: f"{t[0]}:{t[1]}"
    from_s = lambda s: tuple(s.split(":"))  # type: ignore[return-value]

    ls1 = LeveledSet[tuple[str, str], str](to_string=to_s, from_string=from_s)
    ls2 = LeveledSet[tuple[str, str], str](to_string=to_s, from_string=from_s)

    ls1.extend([("a", "1"), ("b", "2")])
    ls2.extend([("b", "2"), ("c", "3")])

    # roundtrip via iteration returns tuples again
    assert set(ls1) == {("a", "1"), ("b", "2")}
    assert set(ls2) == {("b", "2"), ("c", "3")}

    # set ops return external items
    assert ls1.union(ls2) == {("a", "1"), ("b", "2"), ("c", "3")}
    assert ls1.intersection(ls2) == {("b", "2")}
    assert ls1.difference(ls2) == {("a", "1")}
    assert not ls1.isdisjoint(ls2)

    # disjoint check
    ls3 = LeveledSet[tuple[str, str], str](to_string=to_s, from_string=from_s)
    ls3.extend([("x", "9")])
    assert ls1.isdisjoint(ls3)

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
    assert ls._levels == [{1, 2, 3}, {10, 11}, {20, 21, 22}]

    assert 1 in ls
    assert 4 not in ls
    assert 10 in ls
    assert 20 in ls
    assert 30 not in ls

    assert ls._levels[0] == {1, 2, 3}
    assert ls._levels[1] == {10, 11}
    assert ls._levels[2] == {20, 21, 22}
    assert ls._levels[-1] == {20, 21, 22}


def test_leveled_set_reidemeister():
    k = kp.knot("3_1")


    ls1 = LeveledSet([k])
    ls1.new_level()
    for r in kp.reidemeister.reidemeister_moves_generator(k):
        ls1.add(kp.canonical(r))
    assert len(list(ls1.iter_level(-1))) == 7
    assert len(list(ls1.iter_level(0))) == 1


    ls2 = LeveledSet([k])
    ls2.new_level()
    for r in kp.reidemeister.reidemeister_moves_generator(ls2.iter_level(-2)):
        ls2.add(kp.canonical(r))
    assert len(list(ls1.iter_level(-1))) == 7
    assert len(list(ls1.iter_level(0))) == 1

    ls3 = LeveledSet([k])
    ls3.new_level()
    for _ in ls3.iter_level(-2):
        for r in kp.reidemeister.reidemeister_moves_generator(_):
            ls3.add(kp.canonical(r))
    assert len(list(ls1.iter_level(-1))) == 7
    assert len(list(ls1.iter_level(0))) == 1

    ls4 = LeveledSet([k])
    ls4.new_level(kp.canonical(kp.reidemeister.reidemeister_moves_generator(ls4.iter_level(-1))))
    assert len(list(ls1.iter_level(-1))) == 7
    assert len(list(ls1.iter_level(0))) == 1


    ls5 = LeveledSet([k])
    ls5.new_level()
    ls5.extend(kp.canonical(kp.reidemeister.reidemeister_moves_generator(ls2.iter_level(-2))))
    assert len(list(ls1.iter_level(-1))) == 7
    assert len(list(ls1.iter_level(0))) == 1

    ls6 = LeveledSet([k])
    ls6.new_level()
    ls6.extend(kp.canonical_generator(kp.reidemeister.reidemeister_moves_generator(ls2.iter_level(-2))))
    assert len(list(ls1.iter_level(-1))) == 7
    assert len(list(ls1.iter_level(0))) == 1

    t = time()
    ls1 = LeveledSet([k])
    ls1.new_level()
    for _ in ls1.iter_level(-2):
        for r in kp.reidemeister.all_reidemeister_moves(_):
            ls1.add(kp.canonical(r))
    ls1.new_level(kp.canonical(kp.reidemeister.reidemeister_moves_generator(ls1.iter_level(-1))))

    #print(time() - t)
    assert len(list(ls1.iter_level(-1))) == 253
    assert len(list(ls1.iter_level(-2))) == 7
    assert len(list(ls1.iter_level(0))) == 1



    # fastest
    t = time()
    ls1 = LeveledSet([k])
    ls1.new_level()
    for _ in ls1.iter_level(-2):
        for r in kp.reidemeister.all_reidemeister_moves(_):
            ls1.add(kp.canonical(r))
    ls1.new_level(kp.canonical(kp.reidemeister.all_reidemeister_moves(ls1.iter_level(-1))))
    #print(time() - t)

    assert len(list(ls1.iter_level(-1))) == 253
    assert len(list(ls1.iter_level(-2))) == 7
    assert len(list(ls1.iter_level(0))) == 1


    t= time()
    ls1 = LeveledSet([k])
    ls1.new_level()
    for _ in ls1.iter_level(-2):
        for r in kp.reidemeister.all_reidemeister_moves(_):
            ls1.add(kp.canonical(r))
    ls1.new_level()
    for _ in ls1.iter_level(-2):
        ls1.extend(kp.canonical(kp.reidemeister.all_reidemeister_moves(_)))
    #print(time() - t)

    assert len(list(ls1.iter_level(-1))) == 253
    assert len(list(ls1.iter_level(-2))) == 7
    assert len(list(ls1.iter_level(0))) == 1


# ---- Manual runner ----
if __name__ == "__main__":
    test_powerset_basic()
    test_leveledset_no_conversion_basic_levels_and_counts()
    test_leveledset_iter_level_indexing_and_errors()
    test_leveledset_remove_empty_levels_trailing_only()
    test_leveledset_contains_and_extend()
    test_leveledset_with_conversion_roundtrip_and_ops()
    test_leveled_set()
    test_leveled_set_reidemeister()
    print("All tests passed.")

