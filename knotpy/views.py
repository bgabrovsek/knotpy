"""
The views are read-only iterable containers that are updated as the planar diagram is updated.
As with dicts, the graph should not be updated while iterating through the view.
"""
from collections.abc import Mapping, Set
from functools import total_ordering
import knotpy as kp

__all__ = [
    "AttributeView",
    "AdjacencyView"
]

@total_ordering
class AttributeView(Mapping, Set):

    __slots__ = ("_attr",)

    def __getstate__(self):
        return {"_attr": self._attr}

    def __setstate__(self, state):
        self._attr = state["_attr"]

    def __init__(self, attributes):
        self._attr = attributes

    # Mapping methods
    def __len__(self):
        return len(self._attr)

    def __iter__(self):
        return iter(self._attr)

    def __getitem__(self, key):
        if isinstance(key, slice):
            raise ValueError(f"{type(self).__name__} does not support slicing.")
        return self._attr[key]

    # Set methods
    def __contains__(self, key):
        return key in self._attr

    @classmethod
    def _from_iterable(cls, it):
        return set(it)

    # DataView method
    def __call__(self, data=False, default=None):
        raise NotImplemented("")

    def data(self, data=True, default=None):
        """Return a read-only view of node data."""
        raise NotImplemented("")

    # comparison methods

    def __eq__(self, other):
        """Compare nested dictionaries {key1: dict1, key: dict2, ...}"""
        return self._attr == other._attr  # compare dictionaries

    def __lt__(self, other):
        """Compare nested dictionaries {key1: dict1, key: dict2, ...}"""
        outer_dict1, outer_dict2 = self._attr, other._attr

        if len(outer_dict1) != len(outer_dict2):
            return len(outer_dict1) < len(outer_dict2)
        try:
            # compare keys
            if (outer_keys1 := sorted(outer_dict1)) != (outer_keys2 := sorted(outer_dict2)):
                return outer_keys1 < outer_keys2
            # compare dictionaries values
            for outer_key in outer_keys1:
                inner_dict1, inner_dict2 = outer_dict1[outer_key], outer_dict2[outer_key]
                if inner_dict1 or inner_dict2:  # we expect most attributes will be empty
                    if (inner_items1 := sorted(inner_dict1.items())) != (inner_items2 := sorted(inner_dict2.items())):
                        return inner_items1 < inner_items2
        except TypeError as e:
            raise TypeError(f"Cannot compare planar structures with different instance types (e).")
        except Exception as e:
            raise Exception(e)
        return False  # they are the same

    def __ge__(self, other):
        """Compare nested dictionaries {key1: dict1, key: dict2, ...}.
        The >= operator is needed for lexicographical comparison, so that two comparisons are not called twice
        """
        return self == other or not self < other  # TODO: implement whole method

    def __str__(self):
        #return str(list(self))
        return self.__repr__()

    def __repr__(self):
        return ", ".join(
            [
                f"{key}" + u" \u2192 ({0})".format(
                    " ".join([str(inner_key) for inner_key in val])
                ) for key, val in self._attr.items()
            ]
        )




@total_ordering
class AdjacencyView(Mapping, Set):

    __slots__ = ("_adj",)

    def __getstate__(self):
        return {"_adj": self._attr}

    def __setstate__(self, state):
        self._adj = state["_adj"]

    def __init__(self, adjacencies):
        self._adj = adjacencies

    # Mapping methods
    def __len__(self):
        return len(self._adj)

    def __iter__(self):
        return iter(self._adj)

    def __getitem__(self, key):
        if isinstance(key, slice):
            raise ValueError(f"{type(self).__name__} does not support slicing.")
        return self._adj[key]

    # Set methods
    def __contains__(self, key):
        return key in self._adj

    @classmethod
    def _from_iterable(cls, it):
        return set(it)

    # comparison methods

    def __eq__(self, other):
        """Compare dictionaries with lists values {key1: list1, key: list2, ...}"""
        return self._adj == other._adj  # compare dictionaries

    def __lt__(self, other):
        """Compare dictionaries with lists values {key1: list1, key: list2, ...}"""
        outer_dict1, outer_dict2 = self._adj, other._adj

        if len(outer_dict1) != len(outer_dict2):
            return len(outer_dict1) < len(outer_dict2)
        try:
            # compare keys
            if (outer_keys1 := sorted(outer_dict1)) != (outer_keys2 := sorted(outer_dict2)):
                return outer_keys1 < outer_keys2
            # compare list values
            for outer_key in outer_keys1:
                if (inner_list1 := outer_dict1[outer_key]) != (inner_list2 := outer_dict2[outer_key]):
                    return inner_list1 < inner_list2
        except TypeError as e:
            raise TypeError(f"Cannot compare planar structures with different instance types (e).")
        except Exception as e:
            raise Exception(e)

        return False  # they are the same

    def __ge__(self, other):
        """Compare nested dictionaries {key1: dict1, key: dict2, ...}.
        The >= operator is needed for lexicographical comparison, so that two comparisons are not called twice
        """
        return self == other or not self < other  # TODO: implement whole method

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ", ".join(
            [
                f"{v}" + u" \u2192 ({0})".format(" ".join([str(e[0]) for e in u])) for v, u in self._adj.items()
            ]
        )

