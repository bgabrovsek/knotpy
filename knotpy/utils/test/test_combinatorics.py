# from knotpy.utils.combinatorics import (
#     lexicographical_minimal_cyclic_rotation_shift,
#     iterable_depth,
#     union,
#     combinations_with_limited_repetitions,
#     parted_permutations
# )
#
# def test_lexicographical_minimal_cyclic_rotation_shift():
#     assert lexicographical_minimal_cyclic_rotation_shift([3, 1, 2]) == 1
#     assert lexicographical_minimal_cyclic_rotation_shift([1, 2, 3]) == 0
#     assert lexicographical_minimal_cyclic_rotation_shift([2, 3, 1]) == 2
#
# def test_iterable_depth():
#     assert iterable_depth(5) == 0
#     assert iterable_depth([1, 2]) == 1
#     assert iterable_depth([(1, 2)]) == 2
#     assert iterable_depth({'a': 1}) == 1
#     assert iterable_depth({'a': [1, 2]}) == 2
#
# def test_union():
#     assert union([1, 2], [2, 3]) == {1, 2, 3}
#     assert union(set([4]), set()) == {4}
#     assert union() == set()
#
# def test_combinations_with_limited_repetitions_basic():
#     elements = ['a', 'b']
#     result = list(combinations_with_limited_repetitions(elements, 2, [1, 2]))
#     expected = [{'a': 0, 'b': 2}, {'a': 1, 'b': 1}]
#     for r in expected:
#         assert r in result
#     assert all(sum(v for v in d.values()) == 2 for d in result)
#
# def test_combinations_with_zero_inclusion():
#     elements = ['a', 'b']
#     result = list(combinations_with_limited_repetitions(elements, 1, [1, 1], include_zero_multiplicities=True))
#     for d in result:
#         assert set(d.keys()) == {'a', 'b'}
#         assert 'a' in d and 'b' in d
#
# def test_parted_permutations():
#     d = {'a': 0, 'b': 0, 'x': 1}
#     perms = list(parted_permutations(d))
#     assert ['a', 'b', 'x'] in perms or ['b', 'a', 'x'] in perms
#     assert all(set(p) == {'a', 'b', 'x'} for p in perms)
#
# if __name__ == "__main__":
#     test_lexicographical_minimal_cyclic_rotation_shift()
#     test_iterable_depth()
#     test_union()
#     test_combinations_with_limited_repetitions_basic()
#     test_combinations_with_zero_inclusion()
#     test_parted_permutations()
#     print("All combinatorics tests passed.")