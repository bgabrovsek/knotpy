from collections import defaultdict

__all__ = ['compare_dicts', 'inverse_dict', 'inverse_multi_dict']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


def compare_dicts(dict1: dict, dict2: dict, except_keys=None):
    """
    Compare dictionaries by comparing values of sorted keys. If values are again dictionaries, the comparison is
    recursive.
    :param dict1: first dictionary to be compared
    :param dict2: second dictionary to be compared
    :param except_keys: a set of keys to exclude from comparison
    :return: 1 if dict1 > dict2, -1 if dict1 < dict2, 0 if dict1 == dict2.
    """
    except_keys = except_keys or set()
    keys1 = sorted(set(dict1) - set(except_keys))
    keys2 = sorted(set(dict2) - set(except_keys))

    if keys1 == keys2:
        try:
            for key in keys1:
                value1 = dict1[key]
                value2 = dict2[key]

                if isinstance(value1, dict) and isinstance(value2, dict):
                    cmp = compare_dicts(value1, value2)
                    if cmp > 0: return 1
                    if cmp < 0: return -1
                else:
                    if value1 > value2: return 1
                    if value1 < value2: return -1
            return 0
        except TypeError as e:
            raise TypeError(f"Cannot compare planar structures with different instance types ({e}).")
        except Exception as e:
            raise Exception(e)

    if keys1 > keys1: return 1
    if keys1 < keys2: return -1
    return 0



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




class identitydict(defaultdict):
    def __missing__(self, key):
        return key

