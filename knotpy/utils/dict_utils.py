from collections import defaultdict
import warnings

__all__ = ['compare_dicts', 'inverse_dict', 'inverse_multi_dict', "inverse_nested_dict"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


def compare_dicts(dict1: dict, dict2: dict, exclude_keys=None, include_only_keys=None):
    """
    Compare dictionaries by comparing values of sorted keys. If values are again dictionaries, the comparison is
    recursive.
    :param dict1: first dictionary to be compared
    :param dict2: second dictionary to be compared
    :param exclude_keys: a set of keys to exclude from comparison
    :param include_only_keys: only compare this set of keys
    :return: 1 if dict1 > dict2, -1 if dict1 < dict2, 0 if dict1 == dict2.
    """

    exclude_keys = exclude_keys or set()
    exclude_keys = exclude_keys if isinstance(exclude_keys, set) else set(exclude_keys)  # convert to set

    if include_only_keys is None:
        include_only_keys = (set(dict1) | set(dict2)) - exclude_keys
    else:
        include_only_keys = include_only_keys if isinstance(include_only_keys, set) else set(include_only_keys)

    if include_only_keys & exclude_keys:
        warnings.warn(f"Included keys {include_only_keys} and excluded keys {exclude_keys} are not disjoint in comparison function")

    include_only_keys -= exclude_keys

    keys1 = sorted(set(dict1) & include_only_keys)
    keys2 = sorted(set(dict2) & include_only_keys)

    if keys1 != keys2:
        return (keys1 > keys2) * 2 - 1

    for key in keys1:
        value1 = dict1[key]
        value2 = dict2[key]

        if type(value1) is not type(value2):
            raise TypeError(f"Cannot compare types {type(value1)} and {type(value2)}")

        # compare dictionaries
        if isinstance(value1, dict) and isinstance(value2, dict):
            cmp = compare_dicts(value1, value2, exclude_keys=exclude_keys, include_only_keys=include_only_keys)
            if cmp:
                return cmp
        # compare sets
        elif isinstance(value1, set) and isinstance(value2, set):
            if (v1s := sorted(value1)) != (v2s := sorted(value2)):
                return (v1s > v2s) * 2 - 1
        else:
            if value1 != value2:
                return (value1 > value2) * 2 - 1

    return 0

def inverse_multi_dict(d):
    """ exchanges keys & vals, but stores keys in a set """
    invd = dict()  # defaultdict is slower (tested)
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


def inverse_nested_dict(d: dict):
    """split the dictionary into several dictionaries, such that each dictionary has the same values
    :param d:
    :return:
    """
    inner_keys = sorted(set(key for inner in d.values() for key in inner))
    result = dict()  #defaultdict(set)
    for k, k_val in d.items():
        value = tuple(k_val[key] if key in k_val else None for key in inner_keys)
        if value in result:
            result[value].add(k)
        else:
            result[value] = {k, }
    return result

# test
#print(split_nested_dict({"dict1": {"a":4}, "dict2": {"a":4, "b":1}, "dict3": {"a":4}}))

class identitydict(defaultdict):
    def __missing__(self, key):
        return key

if __name__ == "__main__":

    from itertools import permutations

    a = "abcdefglmo"
    b = [0,0,0,1,1,2,2,3,4,5]
    d = []
    for q in permutations(b):
        d.append(dict(zip(a, q)))
        #print(d)

    from time import time

    t = time()
    for x in d:

        invd = inverse_multi_dict(x)
    print(time()-t)

    t = time()
    for x in d:
        invd = inverse_multi_dict2(x)
    print(time()-t)

    exit()

    d = {"a": 1, "b": 3, "c": 1, "d": 2, "e":8, "f":1, "g":8}
    print(inverse_multi_dict(d))