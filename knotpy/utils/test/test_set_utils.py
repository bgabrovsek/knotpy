from knotpy.utils.set_utils import LeveledSet
import knotpy as kp
from time import time
#
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

    assert ls.levels[0] == {1, 2, 3}
    assert ls.levels[1] == {10, 11}
    assert ls.levels[2] == {20, 21, 22}
    assert ls.levels[-1] == {20, 21, 22}


def test_leveled_set_reidemeister():
    k = kp.knot("3_1")


    ls1 = LeveledSet([k])
    ls1.new_level()
    for r in kp.reidemeister.reidemeister_moves_generator(k):
        ls1.add(kp.canonical(r))
    assert len(ls1.levels[0]) == 1
    assert len(ls1.levels[-1]) == 7

    ls2 = LeveledSet([k])
    ls2.new_level()
    for r in kp.reidemeister.reidemeister_moves_generator(ls2.iter_level(-2)):
        ls2.add(kp.canonical(r))
    assert len(ls2.levels[0]) == 1
    assert len(ls2.levels[-1]) == 7

    ls3 = LeveledSet([k])
    ls3.new_level()
    for _ in ls3.iter_level(-2):
        for r in kp.reidemeister.reidemeister_moves_generator(_):
            ls3.add(kp.canonical(r))
    assert len(ls3.levels[0]) == 1
    assert len(ls3.levels[-1]) == 7

    ls4 = LeveledSet([k])
    ls4.new_level(kp.canonical(kp.reidemeister.reidemeister_moves_generator(ls4.iter_level(-1))))
    assert len(ls3.levels[0]) == 1
    assert len(ls3.levels[-1]) == 7


    ls5 = LeveledSet([k])
    ls5.new_level()
    ls5.extend(kp.canonical(kp.reidemeister.reidemeister_moves_generator(ls2.iter_level(-2))))
    assert len(ls5.levels[0]) == 1
    assert len(ls5.levels[-1]) == 7

    ls6 = LeveledSet([k])
    ls6.new_level()
    ls6.extend(kp.canonical_generator(kp.reidemeister.reidemeister_moves_generator(ls2.iter_level(-2))))
    assert len(ls6.levels[0]) == 1
    assert len(ls6.levels[-1]) == 7

    t = time()
    ls1 = LeveledSet([k])
    ls1.new_level()
    for _ in ls1.iter_level(-2):
        for r in kp.reidemeister.all_reidemeister_moves(_):
            ls1.add(kp.canonical(r))
    ls1.new_level(kp.canonical(kp.reidemeister.reidemeister_moves_generator(ls1.iter_level(-1))))

    print(time() - t)
    assert len(ls1.levels[-1]) == 253
    assert len(ls1.levels[-2]) == 7
    assert len(ls1.levels[0]) == 1


    # fastest
    t = time()
    ls1 = LeveledSet([k])
    ls1.new_level()
    for _ in ls1.iter_level(-2):
        for r in kp.reidemeister.all_reidemeister_moves(_):
            ls1.add(kp.canonical(r))
    ls1.new_level(kp.canonical(kp.reidemeister.all_reidemeister_moves(ls1.iter_level(-1))))
    print(time() - t)

    assert len(ls1.levels[-1]) == 253
    assert len(ls1.levels[-2]) == 7
    assert len(ls1.levels[0]) == 1


    t= time()
    ls1 = LeveledSet([k])
    ls1.new_level()
    for _ in ls1.iter_level(-2):
        for r in kp.reidemeister.all_reidemeister_moves(_):
            ls1.add(kp.canonical(r))
    ls1.new_level()
    for _ in ls1.iter_level(-2):
        ls1.extend(kp.canonical(kp.reidemeister.all_reidemeister_moves(_)))
    print(time() - t)

    assert len(ls1.levels[-1]) == 253
    assert len(ls1.levels[-2]) == 7
    assert len(ls1.levels[0]) == 1

    # TODO: measure speed
if __name__ == '__main__':
    #test_leveled_set()
    test_leveled_set_reidemeister()