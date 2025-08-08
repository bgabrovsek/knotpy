"""
Provides a decorator to add total ordering to a class using a `_compare` method.

This is useful in Python 3 when you want to define a single `_compare()` method and
automatically get all comparison methods.
"""

__all__ = ["total_ordering_from_compare"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from typing import TypeVar, Callable

T = TypeVar("T")


def total_ordering_from_compare(cls: type[T]) -> type[T]:
    """
    Decorator that adds total ordering to a class by defining all comparison operators
    using the `_compare(other)` method.

    The decorated class must implement:
        def _compare(self, other) -> int

    Args:
        cls: A class with a `_compare` method.

    Returns:
        The same class with comparison methods `__eq__`, `__ne__`, `__lt__`, `__le__`, `__gt__`, `__ge__`.

    Example:
        @total_ordering_from_compare
        class MyObject:
            def __init__(self, value):
                self.value = value

            def _compare(self, other):
                return self.value - other.value
    """

    def __eq__(self, other):
        return self._compare(other) == 0

    def __ne__(self, other):
        return self._compare(other) != 0

    def __lt__(self, other):
        return self._compare(other) < 0

    def __le__(self, other):
        return self._compare(other) <= 0

    def __gt__(self, other):
        return self._compare(other) > 0

    def __ge__(self, other):
        return self._compare(other) >= 0

    setattr(cls, "__eq__", __eq__)
    setattr(cls, "__ne__", __ne__)
    setattr(cls, "__lt__", __lt__)
    setattr(cls, "__le__", __le__)
    setattr(cls, "__gt__", __gt__)
    setattr(cls, "__ge__", __ge__)

    return cls