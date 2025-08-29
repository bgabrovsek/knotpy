"""
Utility functions and classes for manipulating dictionaries in KnotPy.

Includes comparison utilities, inversion helpers (flat, multi, nested), and
lazy/identity/classifier dict variants.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, Iterable, Hashable, TypeVar, Generic

__all__ = [
    "compare_dicts",
    "invert_dict",
    "invert_multi_dict",
    "invert_dict_of_sets",
    "invert_nested_dict",
    "LazyDict",
    "IdentityDict",
    "ClassifierDict",
    "common_dict",
]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")


def compare_dicts(
    dict1: dict[str, Any],
    dict2: dict[str, Any],
    exclude_keys: Iterable[str] | None = None,
    include_only_keys: Iterable[str] | None = None,
) -> int:
    """Recursively compare two dictionaries with optional key filters.

    Comparison order:
      1) Effective key sets (after include/exclude),
      2) Values under those keys (recursing into nested dicts),
      3) Sets are compared via sorted order, other values via native ordering.

    Args:
        dict1: First dictionary to compare.
        dict2: Second dictionary to compare.
        exclude_keys: Keys to ignore at the **top level**.
        include_only_keys: If provided, only these **top-level** keys are considered.

    Returns:
        1 if ``dict1 > dict2``, -1 if ``dict1 < dict2``, 0 if equal.

    Raises:
        TypeError: If corresponding values have mismatched types and cannot be compared.
    """
    ex = set(exclude_keys or ())

    if include_only_keys is None:
        inc = (set(dict1) | set(dict2)) - ex
    else:
        inc = set(include_only_keys) - ex

    keys1 = sorted(set(dict1) & inc)
    keys2 = sorted(set(dict2) & inc)
    if keys1 != keys2:
        return (keys1 > keys2) * 2 - 1

    for key in keys1:
        v1 = dict1[key]
        v2 = dict2[key]

        if type(v1) is not type(v2):
            raise TypeError(f"Cannot compare mismatched types for key '{key}': {type(v1)} vs {type(v2)}")

        if isinstance(v1, dict):
            # Note: include_only_keys applies only at the top level
            cmp = compare_dicts(v1, v2, exclude_keys=None, include_only_keys=None)
            if cmp:
                return cmp
        elif isinstance(v1, set):
            s1, s2 = sorted(v1), sorted(v2)
            if s1 != s2:
                return (s1 > s2) * 2 - 1
        else:
            if v1 != v2:
                return (v1 > v2) * 2 - 1

    return 0


def invert_dict_of_sets(d: dict[K, set[V]]) -> dict[V, set[K]]:
    """Invert a dictionary of sets.

    Args:
        d: Mapping where values are sets.

    Returns:
        Inverse mapping value -> set of original keys.
    """
    inverse: dict[V, set[K]] = {}
    for key, value_set in d.items():
        for item in value_set:
            inverse.setdefault(item, set()).add(key)
    return inverse


def invert_multi_dict(d: dict[K, V]) -> dict[V, set[K]]:
    """Invert a dictionary, grouping keys by shared values.

    Args:
        d: Input mapping (values need not be unique).

    Returns:
        Mapping from value to set of keys that mapped to it.
    """
    inverse: dict[V, set[K]] = {}
    for key, value in d.items():
        inverse.setdefault(value, set()).add(key)
    return inverse


def invert_dict(d: dict[K, V]) -> dict[V, K]:
    """Invert a dictionary with unique values.

    Args:
        d: Input mapping with unique values.

    Returns:
        Inverse mapping from value to key.

    Raises:
        ValueError: If a duplicate value is encountered.
    """
    inverse: dict[V, K] = {}
    for key, value in d.items():
        if value in inverse:
            raise ValueError(f"Cannot invert dictionary with duplicate value {value!r}.")
        inverse[value] = key
    return inverse


def invert_nested_dict(d: dict[K, dict[str, Any]]) -> dict[tuple[Any, ...], set[K]]:
    """Group keys by their nested dictionary value signatures.

    Args:
        d: Mapping whose values are nested dicts.

    Returns:
        Mapping from tuples of inner values (ordered by inner key name) to sets of outer keys.
    """
    inner_keys = sorted({ik for inner in d.values() for ik in inner})
    result: dict[tuple[Any, ...], set[K]] = {}
    for k, inner_dict in d.items():
        value = tuple(inner_dict.get(ik) for ik in inner_keys)
        result.setdefault(value, set()).add(k)
    return result


class IdentityDict(defaultdict[K, K]):
    """A ``defaultdict`` that returns the key itself as the default.

    Example:
        >>> d = IdentityDict()
        >>> d["x"]
        'x'
    """

    def __init__(self) -> None:
        super().__init__(None)  # type: ignore[arg-type]

    def __missing__(self, key: K) -> K:  # type: ignore[override]
        return key


class LazyDict(dict[K, V], Generic[K, V]):
    """Dictionary that supports lazy loading and optional lazy value evaluation.

    Args:
        load_function: Callable returning either a dict or an iterable of ``(key, value)`` pairs.
        eval_function: Optional callable applied to values on first access (per key).

    Example:
        >>> def load(): return {"a": "2 + 2"}
        >>> def evaluate(expr): return eval(expr)
        >>> d = LazyDict(load, evaluate)
        >>> d["a"]
        4
    """

    def __init__(
        self,
        load_function: Callable[[], dict[K, V] | Iterable[tuple[K, V]]],
        eval_function: Callable[[V], Any] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._load_function = load_function
        self._eval_function = eval_function
        self._data_loaded = False
        self._evaluated_keys: set[K] = set()

        if eval_function is not None and not callable(eval_function):
            raise TypeError("eval_function must be callable or None")

    def _ensure_loaded(self) -> None:
        if not self._data_loaded:
            loaded = self._load_function()
            if isinstance(loaded, dict):
                self.update(loaded)
            else:
                for k, v in loaded:
                    super().__setitem__(k, v)
            self._data_loaded = True

    def _maybe_evaluate(self, key: K) -> None:
        if self._eval_function and key not in self._evaluated_keys:
            raw_value = super().__getitem__(key)
            evaluated = self._eval_function(raw_value)
            super().__setitem__(key, evaluated)
            self._evaluated_keys.add(key)

    def __getitem__(self, key: K) -> V:  # type: ignore[override]
        self._ensure_loaded()
        self._maybe_evaluate(key)
        return super().__getitem__(key)

    def __setitem__(self, key: K, value: V) -> None:  # type: ignore[override]
        self._ensure_loaded()
        super().__setitem__(key, value)

    def __contains__(self, key: object) -> bool:  # type: ignore[override]
        self._ensure_loaded()
        return super().__contains__(key)

    def __iter__(self):  # type: ignore[override]
        self._ensure_loaded()
        return super().__iter__()

    def __len__(self) -> int:  # type: ignore[override]
        self._ensure_loaded()
        return super().__len__()

    def __repr__(self) -> str:  # type: ignore[override]
        self._ensure_loaded()
        if self._eval_function:
            # Trigger evaluation for a stable, fully-resolved repr
            for key in list(self.keys()):
                _ = self[key]
        return f"LazyDict({dict(self)!r})"

    def keys(self):  # type: ignore[override]
        self._ensure_loaded()
        return super().keys()

    def values(self):  # type: ignore[override]
        self._ensure_loaded()
        if self._eval_function:
            for key in list(self.keys()):
                _ = self[key]
        return super().values()

    def items(self):  # type: ignore[override]
        self._ensure_loaded()
        if self._eval_function:
            for key in list(self.keys()):
                _ = self[key]
        return super().items()

    def get(self, key: K, default: V | None = None) -> V | None:  # type: ignore[override]
        self._ensure_loaded()
        if super().__contains__(key):
            return self[key]
        return default

    def reload(self) -> None:
        """Reload the dictionary using the original load function.

        Clears existing values and evaluation state, then loads fresh data.
        """
        self.clear()
        self._evaluated_keys.clear()
        self._data_loaded = False
        self._ensure_loaded()


class ClassifierDict(dict[tuple[Any, ...], list[T]], Generic[T]):
    """Dictionary that groups items by a tuple of classifier function outputs.

    Args:
        functions: Mapping ``label -> function(item)`` used to compute the grouping key.
    """

    def __init__(self, functions: dict[str, Callable[[T], Any]]) -> None:
        super().__init__()
        self.functions = functions

    def append(self, item: T) -> None:
        """Group the given item under a key defined by its classification values.

        Args:
            item: The item to group.
        """
        key = tuple(func(item) for func in self.functions.values())
        if key not in self:
            self[key] = []
        self[key].append(item)


def common_dict(*dicts: dict[str, Any]) -> dict[str, Any]:
    """Find key/value pairs shared across all provided dictionaries.

    Args:
        *dicts: One or more dictionaries.

    Returns:
        Dictionary of pairs present and equal in all inputs.

    Example:
        >>> common_dict({'a': 1}, {'a': 1, 'b': 2}, {'a': 1})
        {'a': 1}
    """
    if not dicts:
        return {}
    common_keys = set.intersection(*(set(d) for d in dicts))
    base = dicts[0]
    return {k: base[k] for k in common_keys if all(d.get(k) == base[k] for d in dicts[1:])}


if __name__ == "__main__":
    pass
