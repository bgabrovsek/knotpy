"""
Disjoint Set Union (Union–Find).

Efficiently maintains a partition of a set into disjoint subsets with near-constant-time
`find` (with path compression) and `union` (by rank).
"""

__all__ = ["DisjointSetUnion"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from typing import Hashable, Iterable, Iterator, Optional


class DisjointSetUnion:
    """Union–Find / Disjoint Set Union (DSU).

    Manages a partition of elements into disjoint sets and supports:
    adding elements, finding a set representative, uniting two sets,
    iterating over components, and exporting components.

    Args:
        iterable: Optional iterable of elements to initialize as singleton sets.

    Example:
        >>> dsu = DisjointSetUnion([1, 2, 3])
        >>> dsu.union(1, 2)
        >>> dsu.find(1) == dsu.find(2)
        True
        >>> sorted(sorted(g) for g in dsu)
        [[1, 2], [3]]
    """

    def __init__(self, iterable: Optional[Iterable[Hashable]] = None) -> None:
        self.parent: dict[Hashable, Hashable] = {}
        self.rank: dict[Hashable, int] = {}
        if iterable:
            for item in iterable:
                self.add(item)

    def add(self, item: Hashable) -> None:
        """Add a new item as a singleton set (no-op if it already exists).

        Args:
            item: Element to add.
        """
        if item not in self.parent:
            self.parent[item] = item
            self.rank[item] = 0

    def find(self, item: Hashable) -> Optional[Hashable]:
        """Return the representative (root) of the set containing ``item``.

        Performs path compression for near-constant amortized time.

        Args:
            item: Element to locate.

        Returns:
            The set representative, or ``None`` if the item is unknown.

        Example:
            >>> dsu = DisjointSetUnion([1, 2])
            >>> dsu.find(1) in {1, 2}
            True
        """
        if item not in self.parent:
            return None
        # Path compression
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])  # type: ignore[arg-type]
        return self.parent[item]

    def union(self, item1: Hashable, item2: Hashable) -> None:
        """Merge the sets containing ``item1`` and ``item2`` (if both exist).

        Uses union-by-rank heuristic. If either item is unknown, nothing happens.

        Args:
            item1: First element.
            item2: Second element.

        Example:
            >>> dsu = DisjointSetUnion([1, 2, 3])
            >>> dsu.union(1, 2)
            >>> dsu.find(1) == dsu.find(2)
            True
        """
        root1 = self.find(item1)
        root2 = self.find(item2)
        if root1 is None or root2 is None or root1 == root2:
            return

        r1, r2 = self.rank[root1], self.rank[root2]
        if r1 > r2:
            self.parent[root2] = root1
        elif r1 < r2:
            self.parent[root1] = root2
        else:
            self.parent[root2] = root1
            self.rank[root1] += 1

    def __iadd__(self, item: Hashable):
        """Shorthand for ``dsu.add(item)``."""
        self.add(item)
        return self

    def __setitem__(self, item1: Hashable, item2: Hashable) -> None:
        """Shorthand for “add both, then union”: ``dsu[item1] = item2``.

        Args:
            item1: First element.
            item2: Second element.
        """
        self.add(item1)
        self.add(item2)
        self.union(item1, item2)

    def __iter__(self) -> Iterator[set[Hashable]]:
        """Iterate over the current disjoint sets (as Python sets).

        Yields:
            Each component as a ``set`` of elements.

        Notes:
            This runs in O(n α(n)) due to path-compressed finds and a single grouping pass.

        Example:
            >>> dsu = DisjointSetUnion([1, 2, 3, 4])
            >>> dsu.union(1, 2); dsu.union(3, 4)
            >>> sorted(sorted(g) for g in dsu)
            [[1, 2], [3, 4]]
        """
        # Build components in one pass (avoids O(n^2) repeated scans)
        comps: dict[Hashable, set[Hashable]] = {}
        for x in self.parent:
            r = self.find(x)
            if r is not None:
                comps.setdefault(r, set()).add(x)
        return iter(comps.values())

    @property
    def elements(self) -> Iterator[Hashable]:
        """Iterate over all elements ever added.

        Returns:
            An iterator over elements.
        """
        return iter(self.parent)

    def to_set(self, item: Hashable) -> set[Hashable]:
        """Return the component containing ``item``.

        Args:
            item: An element present in the DSU.

        Returns:
            The set of items in the same component (empty set if item unknown).

        Example:
            >>> dsu = DisjointSetUnion([1, 2, 3])
            >>> dsu.union(1, 2)
            >>> dsu.to_set(1) == {1, 2}
            True
        """
        root = self.find(item)
        if root is None:
            return set()
        return {x for x in self.parent if self.find(x) == root}

    def representatives(self) -> Iterator[Hashable]:
        """Yield one representative per component (uses ``min`` for stability).

        Warning:
            Elements in a component must be mutually comparable for ``min`` to work.

        Yields:
            A representative element per component.
        """
        for component in self:
            yield min(component)

    def classes(self) -> list[set[Hashable]]:
        """Return a list of all disjoint sets (components)."""
        return list(self)

    def __len__(self) -> int:
        """Return the number of components."""
        # Use a single pass + path compression
        reps = set()
        for x in self.parent:
            r = self.find(x)
            if r is not None:
                reps.add(r)
        return len(reps)

    def __repr__(self) -> str:
        return f"DisjointSetUnion({self.parent}, {self.rank})"

    def __str__(self) -> str:
        return str(self.classes())

    def to_dict(self) -> dict[Hashable, set[Hashable]]:
        """Return a mapping {rep: others} for each component.

        The representative is chosen as ``min(component)`` (see caveat in
        :meth:`representatives`).

        Returns:
            A dictionary mapping each representative to the other members in the set.
        """
        result: dict[Hashable, set[Hashable]] = {}
        for comp in self:
            rep = min(comp)
            result[rep] = set(comp) - {rep}
        return result


if __name__ == "__main__":
    pass
