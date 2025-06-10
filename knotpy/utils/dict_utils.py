from collections import defaultdict
import warnings

__all__ = ['compare_dicts', 'invert_dict', 'invert_multi_dict', "invert_nested_dict", "LazyEvalDict", "LazyLoadDict",
           "LazyLoadEvalDict","identitydict","ClassifierDict","common_dict", "JointDict"]
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

    TODO: simplify
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

def invert_dict_of_sets(d):
    inverse = {}
    for key, value_set in d.items():
        for item in value_set:
            inverse.setdefault(item, set()).add(key)
    return inverse

def invert_multi_dict(d):
    """ exchanges keys & vals, but stores keys in a set """
    inverse = dict()  # defaultdict is slower (tested)
    for key, value in d.items():
        if value in inverse:
            inverse[value].add(key)
        else:
            inverse[value] = {key, }
    return inverse

def invert_dict(d):
    """Exchange keys & vals, assume there are no duplicate vals."""
    #TODO: use items() tuple
    inverse = dict()
    for key, value in d.items():
        if value in inverse:
            raise ValueError("Cannot make inverse dictionary of {d}.")
        inverse[value] = key
    return inverse


def invert_nested_dict(d: dict):
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

class identitydict(defaultdict):
    def __missing__(self, key):
        return key


class LazyLoadDict(dict):
    """
    LazyLoadDict is a custom dictionary class that defers data loading until it is first accessed,
    optimizing resource usage by delaying expensive initialization operations. It mimics the behavior
    of a standard Python dictionary while incorporating lazy loading functionality.

    This makes it ideal for scenarios where loading data is expensive, and you want to defer the operation
    until it’s actually needed.
    """

    def __init__(self, load_function, *args, **kwargs):
        """
        Initializes an instance with a function to load data, along with any additional arguments or keyword arguments.

        Parameters
        ----------
        load_function : Callable or None
            A function responsible for loading the data. The function should return a dictionary or a list or tuples
            representing the dictionary. If None, the data is assumed to be preloaded.
        *args :
            Additional positional arguments passed to the superclass.
        **kwargs :
            Additional keyword arguments passed to the superclass.

        Attributes
        ----------
        _data_loaded : bool
            A flag indicating whether the data has already been loaded.
        _load_function : Callable or None
            The function used to load data. If None, no loading function is used.
        """
        super().__init__(*args, **kwargs)
        self._data_loaded = load_function is None
        self._load_function = load_function

    def _ensure_loaded(self):
        if not self._data_loaded:
            self.update(self._load_function())
            self._data_loaded = True

    def __getitem__(self, key):
        self._ensure_loaded()
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        self._ensure_loaded()
        super().__setitem__(key, value)

    def __contains__(self, key):
        self._ensure_loaded()
        return super().__contains__(key)

    def __iter__(self):
        self._ensure_loaded()
        return super().__iter__()

    def get(self, key):
        self._ensure_loaded()
        return super().get(key)

    def keys(self):
        self._ensure_loaded()
        return super().keys()

    def values(self):
        self._ensure_loaded()
        return super().values()

    def items(self):
        self._ensure_loaded()
        return super().items()

    def __len__(self):
        self._ensure_loaded()
        return super().__len__()

    def __repr__(self):
        self._ensure_loaded()
        return f"LazyLoadDict({dict().__repr__()})"


class LazyEvalDict(dict):
    """
    A dictionary that evaluates values lazily upon access.

    This class extends the standard Python dictionary to support lazy evaluation
    of its values. A user-defined function is applied to the value associated
    with a key the first time that key is accessed. Subsequent accesses return
    the already-evaluated value without invoking the evaluation function again.
    This approach is beneficial in scenarios where the value computation is
    expensive, and the result is needed only on demand.

    Attributes:
        _eval_function: Callable function used to lazily evaluate values.
        _evaluated_keys: Set of keys whose values have already been evaluated.
    """
    def __init__(self, eval_function, *args, **kwargs):
        """
        Initializes an instance of a class that performs actions based on a provided evaluation function.
        Ensures the evaluation function is callable and prepares an internal state to track evaluated keys.

        Parameters
        ----------
        eval_function : Callable
            A callable used to perform evaluations. Must be passed and checked for
            its callable nature.
        *args
            Positional arguments passed to the base class initializer.
        **kwargs
            Keyword arguments passed to the base class initializer.

        Raises
        ------
        TypeError
            If `eval_function` is not callable.
        """
        super().__init__(*args, **kwargs)
        if not callable(eval_function):
            raise TypeError("eval_function must be callable")
        self._eval_function = eval_function
        self._evaluated_keys = set()

    def __getitem__(self, key):
        # Evaluate the value of the key if it is not already evaluated.
        if key not in self._evaluated_keys:
            super().__setitem__(key, self._eval_function(super().__getitem__(key)))
            self._evaluated_keys.add(key)
        return super().__getitem__(key)

    def values(self):
        """Return all values, forcing evaluation of any unevaluated entries."""
        for key in self:
            _ = self[key]  # Ensure all values are evaluated
        return super().values()

    def items(self):
        """Return all key-value pairs, forcing evaluation of any unevaluated entries."""
        for key in self:
            _ = self[key]  # Ensure all values are evaluated
        return super().items()

    def __repr__(self):
        return f"LazyEvalDict(keys={dict().keys()})"


class LazyLoadEvalDict(dict):
    """
    LazyLoadDict is a custom dictionary class that defers data loading until it is first accessed,
    optimizing resource usage by delaying expensive initialization operations. It mimics the behavior
    of a standard Python dictionary while incorporating lazy loading functionality.

    This makes it ideal for scenarios where loading data is expensive, and you want to defer the operation
    until it’s actually needed.
    """

    def __init__(self, load_function, eval_function, *args, **kwargs):
        """
        Initializes an instance with a function to load data, along with any additional arguments or keyword arguments.

        Parameters
        ----------
        load_function : Callable or None
            A function responsible for loading the data. The function should return a dictionary or a list or tuples
            representing the dictionary. If None, the data is assumed to be preloaded.
        *args :
            Additional positional arguments passed to the superclass.
        **kwargs :
            Additional keyword arguments passed to the superclass.

        Attributes
        ----------
        _data_loaded : bool
            A flag indicating whether the data has already been loaded.
        _load_function : Callable or None
            The function used to load data. If None, no loading function is used.
        """
        super().__init__(*args, **kwargs)
        self._data_loaded = load_function is None
        self._load_function = load_function
        if not callable(eval_function):
            raise TypeError("eval_function must be callable")
        self._eval_function = eval_function
        self._evaluated_keys = set()

    def _ensure_loaded(self):
        if not self._data_loaded:
            self.update(self._load_function())
            self._data_loaded = True

    def __getitem__(self, key):
        self._ensure_loaded()
        # Evaluate the value of the key if it is not already evaluated.
        if key not in self._evaluated_keys:
            super().__setitem__(key, self._eval_function(super().__getitem__(key)))
            self._evaluated_keys.add(key)
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        self._ensure_loaded()
        super().__setitem__(key, value)

    def __contains__(self, key):
        self._ensure_loaded()
        return super().__contains__(key)

    def __iter__(self):
        self._ensure_loaded()
        return super().__iter__()

    def get(self, key):
        self._ensure_loaded()
        return super().get(key)

    def keys(self):
        self._ensure_loaded()
        return super().keys()

    def values(self):
        self._ensure_loaded()
        for key in self:
            _ = self[key]  # Ensure all values are evaluated
        return super().values()

    def items(self):
        self._ensure_loaded()
        for key in self:
            _ = self[key]  # Ensure all values are evaluated
        return super().items()

    def __len__(self):
        self._ensure_loaded()
        return super().__len__()

    def __repr__(self):
        self._ensure_loaded()
        for key in self:
            _ = self[key]  # Ensure all values are evaluated
        return f"LazyLoadDict({dict().__repr__()})"


class ClassifierDict(dict):
    """
    A dictionary-like object that partitions items based on values returned by
    a collection of functions. The keys are tuples of computed values, and the
    values are lists of items sharing those values.
    """

    def __init__(self, functions: dict):
        """
        Initialize the partitioner with a set of value-producing functions.

        Args:
            functions (dict): A dictionary mapping labels to functions.
                              Each function should take an item and return a value.
        """
        super().__init__()
        self.functions = functions

    def append(self, item):
        """
        Compute the key for an item using the provided functions and store
        the item in the corresponding group.

        Args:
            item: The object to be grouped.
        """
        # Build a key from the tuple of values returned by the functions
        key = tuple(func(item) for func in self.functions.values())

        # Append the item to the corresponding list in the dictionary
        if key not in self:
            self[key] = []
        self[key].append(item)


def common_dict(*dicts):
    """
    Return a dictionary containing key-value pairs that are common across all input dictionaries.

    A key-value pair is included in the result if:
    - The key exists in every dictionary.
    - All dictionaries have the same value associated with that key.

    Parameters:
        *dicts: Any number of dictionaries to compare.

    Returns:
        dict: A dictionary of key-value pairs shared by all input dictionaries with equal values.
              Returns an empty dictionary if no common key-value pairs exist or if no dictionaries are given.

    Example:
        >>> common_dict({'a': 1, 'b': 2}, {'a': 1, 'b': 3}, {'a': 1})
        {'a': 1}
    """
    if not dicts:
        return {}
    common_keys = set.intersection(*(set(d) for d in dicts))
    return {key: dicts[0][key] for key in common_keys if all(d[key] == dicts[0][key] for d in dicts[1:])}

class JointDict:
    def __init__(self, dict_map: dict[int, dict], key_map=None):
        """
        Initialize with a mapping from prefix (int) to dictionary.
        Keys in each dictionary must start with that prefix and an underscore.
        Example: {1: {'1_a': ...}, 2: {'2_b': ...}}
         Args:
            dict_map (dict): Mapping from keys (e.g. IDs, types) to sub-dictionaries.
            key_map (callable): Function that takes a joint key and returns (subdict_key, key_in_subdict)
        """
        self._dict_map = dict_map
        self.key_map = key_map

    def __getitem__(self, key):
        subkey = self.key_map(key)
        if subkey not in self._dict_map:
            raise KeyError(f"No dictionary for subkey {subkey}")
        return self._dict_map[subkey][key]

    def __contains__(self, key):
        subkey = self.key_map(key)
        return key in self._dict_map[subkey]

    def keys(self, from_subkeys=None):
        if from_subkeys is None:
            for inner_dict in self._dict_map.values():
                yield from inner_dict
        else:
            for subkey in sorted(from_subkeys):
                yield from self._dict_map[subkey]

    def items(self, from_subkeys=None):
        if from_subkeys is None:
            for inner_dict in self._dict_map.values():
                yield from inner_dict.items()
        else:
            for subkey in sorted(from_subkeys):
                yield from self._dict_map[subkey].items()

    def values(self, from_subkeys=None):
        if from_subkeys is None:
            for inner_dict in self._dict_map.values():
                yield from inner_dict.values()
        else:
            for subkey in sorted(from_subkeys):
                yield from self._dict_map[subkey].values()

    def __iter__(self):
        return self.keys()

    def __len__(self):
        return sum(len(inner_dict) for inner_dict in self._dict_map.values())


if __name__ == "__main__":

    pass