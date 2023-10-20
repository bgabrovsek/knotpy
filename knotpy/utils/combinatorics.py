from itertools import product, permutations, chain
from collections import defaultdict

__all__ = ['lexicographical_minimal_cyclic_rotation_shift', 'iterable_depth', 'union', 'inverse_multi_dict',
           'combinations_with_limited_repetitions', 'parted_permutations', 'cmp_dict_list', 'cmp_dict_dict',
           'identitydict', 'cmp_dict', "inverse_dict"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

# lists, tuples


#def minimal_cyclic_rotation(values):
#    return min(values[i:] + values[:i] for i in range(len(values)))


def lexicographical_minimal_cyclic_rotation_shift(values):
    zip_values = [tuple(zip(*(values[shift:] + values[:shift]))) for shift in range(len(values))]
    return min(range(len(zip_values)), key=lambda i: zip_values[i])


def iterable_depth(o):
    """Return the depth of iterable object, e.g. iterable_depth([1, 2]) = 1 and iterable_depth([(1,2)]) = 2."""
    if not hasattr(o, '__iter__'):
        return 0
    if isinstance(o, dict):
        return iterable_depth(o[next(iter(o))])+1 if len(o) > 0 else 1
    else:
        return iterable_depth(next(iter(o))) + 1 if len(o) > 0 else 1


#def inverse_iter_iter(iter_iter) -> dict:
"""Inverse of a list (tuple) of lists (tuples), so we can quickly search what list the elements belong to.
The elements in the lists must be unique. For example, the inverse of [[1,2],[3]] is {1:[1,2], 2:[1,2], 3:[3]}
"""
 #   return {elt: inner for inner in iter_iter for elt in inner}


# print(iterable_depth([({1},)]))

# sets

def union(*sets):
    """Returns a union of the sets in the arguments."""
    return set.union(*(set(s) for s in sets)) if len(sets) else set()

# dictionaries
def inverse_multi_dict(d):
    """ exchanges keys & vals, but stores keys in a set """
    invd = dict()  # defaultdict?
    for key, value in d.items():
        if value in invd:
            invd[value].add(key)
        else:
            invd[value] = {key, }
    return invd

def inverse_dict(d):
    """Exchange keys & vals, assume there are no duplicate vals."""
    invd = dict()
    for key, value in d.items():
        if value in invd:
            raise ValueError("Cannot make inverse dictionary of {d}.")
        invd[value] = key
    return invd

# combinatorics


def combinations_with_limited_repetitions(elements, n,
                                          available_repetitions=None,
                                          include_zero_multiplicities=False):
    result = []
    """From elements select some select n, where the order does not matter.
    The parameter n can be also iterable.
    The parameter count_limits tells how many elements of each type are available.
    example: elts = [(a,1), (b,2)], n = 2, should return: ab, bb -> [(a,1),(b,1)], [(b,2)]
    example: elts = A1,B2,C1,D2, should return 
    [(A1,B1,C1),(A1,B1,D1),(A1,B2),(A1,C1,D1),(A1,D2),(B1,C1,D1),(B1,D2),(B2,C1),(B2,D1),(C1,D2)]
    TODO: write new description, since dictionaries are now used.
    But this method is not universal, since elements must be hashable.
    """

    if available_repetitions is None:
        available_repetitions = [n for e in elements]

    if n == 0:
        #yield dict()
        yield dict()
        return

    # start with first element
    e = elements[0]  # the element
    r = available_repetitions[0]  # maximal number of repetitions

    # limit the minimal and maximal number of times we take the 0-th element
    for m in range(max(0, n - sum(available_repetitions[1:])), min(n, r) + 1):
        #counter = {e: m} if m > 0 else dict()
        seq = {e: m} if include_zero_multiplicities or m else dict() # add element e with multiplicity m
        for other_seq in combinations_with_limited_repetitions(elements[1:], n-m, available_repetitions[1:]):
            #yield counter | other_counters
            yield seq | other_seq



# print(inverse_multi_dict({'a': 0, 'b': 0, 'c': 1}))


def parted_permutations(d):
    """Returns "parted" permutations of keys of d split by values (partition values, classes) of d.
    e.g. d = {'a':0, 'b':0, 'c':0, 'x':1, 'y':1, 'q':2} -> abc-xy-q, abc-yx-q, acb-xy-q, acb-yx-q, ... , cba-yx-q
    """
    d_ = inverse_multi_dict(d)
    for seq_of_seq in product(*[permutations(d_[key]) for key in sorted(d_.keys())]):
        yield list(chain.from_iterable(seq_of_seq))

#for x in parted_permutations({5:0, 6:1, 7:0, 8: 0, 9: 2}): print(x)

# comparison


def cmp_dict_list(dict1, dict2):
    """Compare dictionaries of iterables, returns 1 if self > other, -1 if self < other and 0 if self == other"""
    if len(dict1) != len(dict2):
        return 2 * (len(dict1) > len(dict2)) - 1
    try:
        # compare keys
        if (keys1 := sorted(dict1)) != (keys2 := sorted(dict2)):
            return 2 * (keys1 > keys2) - 1
        # compare list values
        for key in keys1:
            if (inner_list1 := dict1[key]) != (inner_list2 := dict2[key]):
                return 2 * (inner_list1 > inner_list2) - 1
    except TypeError as e:
        raise TypeError(f"Cannot compare dictionary structures with different instance types ({e}).")
    except Exception as e:
        raise Exception(e)

    return 0

def cmp_dict_dict(dict1, dict2):
    """Compare dictionaries of dictionaries of iterables,
    returns 1 if self > other, -1 if self < other and 0 if self == other"""
    if len(dict1) != len(dict2):
        return 2 * (len(dict1) > len(dict2)) - 1
    try:
        # compare keys
        if (outer_keys1 := sorted(dict1)) != (outer_keys2 := sorted(dict2)):
            return 2 * (outer_keys1 > outer_keys2) - 1
        # compare dictionaries values
        for outer_key in outer_keys1:
            inner_dict1, inner_dict2 = dict1[outer_key], dict2[outer_key]
            if inner_dict1 or inner_dict2:  # we expect most attributes will be empty
                if (inner_items1 := sorted(inner_dict1.items())) != (inner_items2 := sorted(inner_dict2.items())):
                    return 2 * (inner_items1 > inner_items2) - 1
    except TypeError as e:
        raise TypeError(f"Cannot compare planar structures with different instance types (e).")
    except Exception as e:
        raise Exception(e)
    return 0  # they are the same


def cmp_dict(dict1, dict2, except_keys=None):
    """Compare dictionaries of dictionaries of iterables,
    returns 1 if self > other, -1 if self < other and 0 if self == other"""
    except_keys = except_keys or set()
    keys1 = sorted(set(dict1) - set(except_keys))
    keys2 = sorted(set(dict2) - set(except_keys))

    if keys1 != keys2:
        return ((keys1 > keys2) << 1) - 1
    try:
        # compare dictionaries values
        for key in keys1:
            if (val1 := dict1[key]) != (val2 := dict2[key]):
                return ((val1 > val2) << 1) - 1
    except TypeError as e:
        raise TypeError(f"Cannot compare planar structures with different instance types ({e}).")
    except Exception as e:
        raise Exception(e)
    return 0  # they are the same


class identitydict(defaultdict):
    def __missing__(self, key):
        return key

"""
print(f"Minimal cyclic rotation of {(test_list := [4,3,0,1])} is {minimal_cyclic_rotation(test_list)}.")
print (f"Union of sets {(test_sets := [{1, 2}, {0, 1}, {5}])} is {union(*test_sets)}.")
print(f"Inverse multi-dictionary of {(test_dict := {0:3, 1:4, 2:3})} is {inverse_multi_dict(test_dict)}.")
"""