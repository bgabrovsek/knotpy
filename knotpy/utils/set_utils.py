"""
Utilities for working with sets and layered (leveled) collections.

- ``powerset``: iterate over all subsets of an iterable.
- ``LeveledSet``: maintain items grouped by discovery "levels", with optional
  compact internal storage via (to_string/from_string) conversions.

This module is lightweight and has no heavy imports.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from itertools import chain, combinations
from typing import Generic, TypeVar

__all__ = ["powerset", "LeveledSet"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

T = TypeVar("T")   # external/public item type (what users pass in / get out)
I = TypeVar("I")   # internal storage type (often str when using to_string)


def powerset(iterable: Iterable[T]) -> Iterator[tuple[T, ...]]:
    """Iterate over all subsets (the power set) of an iterable.

    Subsets are yielded as tuples in increasing size order.

    Args:
        iterable: Any iterable of items.

    Yields:
        Tuples representing each subset, starting with the empty tuple.

    Example:
        >>> list(powerset([1, 2, 3]))
        [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


class LeveledSet(Generic[T, I]):
    """A leveled set structure with optional compact internal representation.

    Items can be stored internally as strings (or any type ``I``) to reduce memory
    usage or enable hashing on otherwise unhashable public types. You can provide
    a pair of conversion functions:

    - ``to_string(item: T) -> I`` stores items internally (often as ``str``).
    - ``from_string(stored: I) -> T`` reconstructs external/public items.

    If either function is omitted (``None``), items are stored directly.

    Levels:
        The structure maintains a list of *levels*. New items are added into the
        *current* level (the last one). Calling :meth:`new_level` creates a new
        level **only if** the last level is non-empty (so you don't accumulate
        trailing empties). All seen items are tracked in a global set to avoid
        duplicates across levels.

    Notes:
        - All set operations (union, intersection, difference) act on the *global*
          content, not per-level content.
        - Iteration yields public/external items (``T``), applying conversion back
          if needed.

    Args:
        items: Optional initial items to insert at level 0.
        to_string: Function to convert an external item ``T`` to internal ``I``.
        from_string: Function to convert an internal item ``I`` back to ``T``.
    """

    def __init__(
        self,
        items: Iterable[T] | None = None,
        to_string: Callable[[T], I] | None = None,
        from_string: Callable[[I], T] | None = None,
    ) -> None:
        self._use_conversion = to_string is not None and from_string is not None
        self._to_string = to_string  # type: ignore[assignment]
        self._from_string = from_string  # type: ignore[assignment]
        self._levels: list[set[I | T]] = []
        self._global_set: set[I | T] = set()
        self.new_level(items if items is not None else [])

    # ---- Introspection -----------------------------------------------------

    def number_of_levels(self) -> int:
        """Return the number of levels currently stored."""
        return len(self._levels)

    def level_sizes(self) -> tuple[int, ...]:
        """Return a tuple with the size of each level."""
        return tuple(len(level) for level in self._levels)

    def number_of_items(self) -> int:
        """Return the total number of unique items across all levels."""
        return len(self._global_set)

    def is_level_empty(self, level: int) -> bool:
        """Return whether a given level is empty.

        Args:
            level: Level index (supports negative indexing like Python lists).

        Raises:
            IndexError: If level is out of range.
        """
        if not -len(self._levels) <= level < len(self._levels):
            raise IndexError(f"Level {level} out of range.")
        return len(self._levels[level]) == 0

    # ---- Level management --------------------------------------------------

    def new_level(self, items: Iterable[T] | T | None = None) -> None:
        """Create a new current level (only if last level is non-empty), then add optional items.

        Args:
            items: Optional single item or iterable of items to add to the new current level.
        """
        if not self._levels or self._levels[-1]:
            self._levels.append(set())

        if items is not None:
            if isinstance(items, Iterable) and not isinstance(items, (str, bytes)):
                self.extend(items)  # type: ignore[arg-type]
            else:
                self.add(items)  # type: ignore[arg-type]

    def remove_empty_levels(self) -> None:
        """Remove trailing empty levels."""
        while self._levels and not self._levels[-1]:
            self._levels.pop()

    # ---- Conversion helpers ------------------------------------------------

    def _in(self, item: T | I) -> T | I:
        return self._to_string(item) if self._use_conversion else item  # type: ignore[misc]

    def _out(self, item: T | I) -> T:
        return self._from_string(item) if self._use_conversion else item  # type: ignore[return-value]

    # ---- Content manipulation ----------------------------------------------

    def add(self, item: T) -> None:
        """Add a single item to the current level if not seen before."""
        stored = self._in(item)
        if stored not in self._global_set:
            self._levels[-1].add(stored)
            self._global_set.add(stored)

    def extend(self, items: Iterable[T]) -> None:
        """Add multiple items to the current level."""
        for item in items:
            self.add(item)

    def contains(self, item: T) -> bool:
        """Return True if the item appears in any level."""
        return self._in(item) in self._global_set

    # ---- Set-like global operations ----------------------------------------

    def union(self, other: "LeveledSet[T, I]") -> set[T]:
        """Return the union of contents (as external items) with another LeveledSet."""
        return {self._out(x) for x in (self._global_set | other._global_set)}

    def intersection(self, other: "LeveledSet[T, I]", evaluate=True) -> set[T]:
        """Return the intersection of contents (as external items) with another LeveledSet."""
        if evaluate:
            return {self._out(x) for x in (self._global_set & other._global_set)}
        else:
            return {x for x in (self._global_set & other._global_set)}

    def difference(self, other: "LeveledSet[T, I]") -> set[T]:
        """Return the difference of contents (as external items) with another LeveledSet."""
        return {self._out(x) for x in (self._global_set - other._global_set)}

    def isdisjoint(self, other: "LeveledSet[T, I]") -> bool:
        """Return True if the two LeveledSets share no common items."""
        return self._global_set.isdisjoint(other._global_set)

    # ---- Iteration ----------------------------------------------------------

    def iter_level(self, level: int) -> Iterator[T]:
        """Iterate items of a specific level (converted to external items).

        Args:
            level: Level index (supports negative indexing).

        Yields:
            Items at the requested level.

        Raises:
            IndexError: If level is out of range.
        """
        if not -len(self._levels) <= level < len(self._levels):
            raise IndexError(f"Level {level} out of range.")
        # Snapshot the set to keep iteration stable if the structure mutates elsewhere.
        items = tuple(self._levels[level])
        return (self._out(s) for s in items)

    def __iter__(self) -> Iterator[T]:
        """Iterate all unique items (converted to external items)."""
        return (self._out(s) for s in self._global_set)


if __name__ == "__main__":
    pass
