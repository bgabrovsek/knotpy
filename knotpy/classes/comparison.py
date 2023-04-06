__all__ = [
    "dict_dict_lt",
]


def dict_dict_lt(dict1, dict2):
    """Compare nested dictionaries {key1: dict1, key: dict2, ...}
    :return: dict1 < dict2
    """
    if len(dict1) != len(dict2):
        return len(dict1) < len(dict2)

    # compare keys
    try:
        if (list1 := sorted(dict1)) != (list2 := sorted(dict2)):
            return list1 < list2
    except TypeError as e:
        raise TypeError(f"Cannot compare planar structures with different instance types (e).")
    except Exception as e:
        raise Exception(e)

    # compare values
    try:
        for key in list1:
            val1, val2 =, dict2[key]
            if dict1[key] or dict2[key]:
                items1 = sorted(dict1[key].items())

        if (list1 := sorted(dict1)) != (list2 := sorted(dict2)):
            return list1 < list2
    except TypeError as e:
        raise TypeError(f"Cannot compare planar structures with different instance types (e).")
    except Exception as e:
        raise Exception(e)

        # compare node attributes
    for node in self._nodes:
        if self._nodes[node] or other._nodes[node]:  # we expect node attributes to be mostly empty
            tup_items_self = sorted(self._nodes[node].items())
            tup_items_other = sorted(other._nodes[node].items())
            if tup_items_self != tup_items_other:
                return tup_items_self < tup_items_other
    return False

