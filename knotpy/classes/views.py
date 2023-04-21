"""
The views are read-only iterable containers that are updated as the planar diagram is updated.
As with dicts, the graph should not be updated while iterating through the view.
"""
from collections.abc import Mapping, Set
from functools import total_ordering
import knotpy as kp
from knotpy.utils import cmp_dict_dict, cmp_dict_list

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
        """Return data read-only view of node data."""
        raise NotImplemented("")

    # comparison methods

    _convert = {
        '__eq__': lambda self, other: self._attr == other._attr,
        '__ne__': lambda self, other: self._attr != other._attr,
        '__lt__': lambda self, other: self.py3cmp(other) < 0,
        '__le__': lambda self, other: self.py3cmp(other) <= 0,
        '__gt__': lambda self, other: self.py3cmp(other) > 0,
        '__ge__': lambda self, other: self.py3cmp(other) >= 0,
    }

    def py3_cmp(self, other):
        return cmp_dict_dict(self._attr, other._attr)




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
    _convert = {
        '__eq__': lambda self, other: self._adj == other._adj,
        '__ne__': lambda self, other: self._adj != other._adj,
        '__lt__': lambda self, other: self.py3cmp(other) < 0,
        '__le__': lambda self, other: self.py3cmp(other) <= 0,
        '__gt__': lambda self, other: self.py3cmp(other) > 0,
        '__ge__': lambda self, other: self.py3cmp(other) >= 0,
    }

    def py3_cmp(self, other):
        return cmp_dict_list(self._adj, other._adj)


    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ", ".join(
            [
                f"{v}" + u" \u2192 ({0})".format(" ".join([str(e[0]) for e in u])) for v, u in sorted(self._adj.items())
            ]
        )


