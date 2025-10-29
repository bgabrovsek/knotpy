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

class SymmetryDSU:
    """Symmetry-aware union–find on top of a base DSU.

    Layers:
      1) A Disjoint Set Union for true equality.
      2) A labeled, undirected multigraph between DSU components for symmetry relations.

    You can later "promote" a symmetry to equivalence via `collapse(sym)`, which
    unions all components linked by that symmetry.

    Notes:
      - The graph is on DSU representatives (components).
      - `relate(a, b, sym)` records that class(a) ~ class(b) by symmetry label `sym`.
      - `orbit_items(item, allowed=...)` returns the components in the symmetry orbit.
      - Self-mirror edges are ignored by default (no-op if a and b are same class).
    """

    def __init__(self, dsu=None, *, iterable=None):
        # Use provided DSU or create one
        self.dsu = dsu if dsu is not None else DisjointSetUnion()
        if iterable is not None and dsu is None:
            for x in iterable:
                self.dsu.add(x)

        # adjacency: rep -> sym_label -> set(rep)
        self._adj = {}

    # ---------- basic DSU passthroughs ----------
    def add(self, item):
        self.dsu.add(item)
        self._ensure_node(self.dsu.find(item))

    def union(self, a, b):
        """Merge DSU classes for a and b; relabel symmetry-graph nodes accordingly."""
        ra, rb = self.dsu.find(a), self.dsu.find(b)
        if ra is None or rb is None or ra == rb:
            return
        # Keep both reps before union; DSU decides survivor
        self.dsu.union(ra, rb)
        r_new = self.dsu.find(ra)  # new representative after union
        r_old = rb if r_new == ra else ra
        self._relabel_node(r_old, r_new)

    def find(self, item):
        return self.dsu.find(item)

    def classes(self):
        return self.dsu.classes()

    def __len__(self):
        return len(self.dsu)

    # ---------- symmetry graph operations ----------
    def relate(self, a, b, sym):
        """Declare that class(a) is related to class(b) by symmetry `sym` (undirected)."""
        ra, rb = self.dsu.find(a), self.dsu.find(b)
        if ra is None or rb is None or ra == rb:
            # Already same component or unknowns -> nothing to add
            return
        self._ensure_node(ra)
        self._ensure_node(rb)
        self._adj[ra].setdefault(sym, set()).add(rb)
        self._adj[rb].setdefault(sym, set()).add(ra)

    def edges(self):
        """Iterate over edges as (rep_u, rep_v, sym)."""
        seen = set()
        for u, labels in self._adj.items():
            for sym, nbrs in labels.items():
                for v in nbrs:
                    key = (u, v, sym)
                    rkey = (v, u, sym)
                    if key in seen or rkey in seen:
                        continue
                    seen.add(key)
                    yield (u, v, sym)

    def orbit_reps(self, item, allowed=None):
        """Return the set of DSU representatives reachable from class(item)
        via symmetry edges whose labels are in `allowed` (or all if None)."""
        start = self.dsu.find(item)
        if start is None:
            return set()
        start = self._canonical_rep(start)

        def ok(label):
            return True if allowed is None else label in allowed

        visited, stack = {start}, [start]
        while stack:
            u = stack.pop()
            for sym, nbrs in self._adj.get(u, {}).items():
                if not ok(sym):
                    continue
                for v in nbrs:
                    v = self._canonical_rep(v)
                    if v not in visited:
                        visited.add(v)
                        stack.append(v)
        return visited

    def orbit_items(self, item, allowed=None):
        """Return the list of DSU components (as sets of items) in the symmetry orbit."""
        reps = self.orbit_reps(item, allowed=allowed)
        comp_map = {r: set() for r in reps}
        for x in self.dsu.parent:
            r = self.dsu.find(x)
            if r is not None:
                r = self._canonical_rep(r)
                if r in comp_map:
                    comp_map[r].add(x)
        return list(comp_map.values())

    def collapse(self, sym):
        """Promote symmetry `sym` to equivalence: union pairs of components linked by this label."""
        pairs = [(u, v) for u, v, s in self.edges() if s == sym]
        for u, v in pairs:
            ru = self._canonical_rep(u)
            rv = self._canonical_rep(v)
            if ru != rv:
                # Union the classes represented by ru and rv (use reps directly)
                self.union(ru, rv)
        self._prune_self_loops(sym)

    # ---------- helpers ----------
    def _ensure_node(self, r):
        if r is None:
            return
        r = self._canonical_rep(r)
        self._adj.setdefault(r, {})

    def _canonical_rep(self, r):
        """Map any representative to its current DSU representative."""
        cr = self.dsu.find(r)
        return r if cr is None else cr

    def _relabel_node(self, old, new):
        """When DSU merges old->new, merge adjacency and relabel references."""
        if old == new:
            return
        old = self._canonical_rep(old)
        new = self._canonical_rep(new)
        if old not in self._adj:
            self._ensure_node(new)
            return

        self._ensure_node(new)
        # Merge label maps
        for sym, nbrs in self._adj[old].items():
            tgt = self._adj[new].setdefault(sym, set())
            for v in nbrs:
                v2 = self._canonical_rep(v)
                if v2 != new:
                    tgt.add(v2)

        # Redirect neighbors pointing to old -> new
        for _u, nbrs in list(self._adj.items()):
            for lab, vs in nbrs.items():
                if old in vs:
                    vs.discard(old)
                    vs.add(new)

        # Drop old node
        del self._adj[old]

        # Clean accidental self-loops
        for sym in list(self._adj[new].keys()):
            if new in self._adj[new][sym]:
                self._adj[new][sym].discard(new)
                if not self._adj[new][sym]:
                    del self._adj[new][sym]

    def _prune_self_loops(self, sym):
        for u in list(self._adj.keys()):
            vs = self._adj[u].get(sym)
            if not vs:
                continue
            cu = self._canonical_rep(u)
            new_vs = {self._canonical_rep(v) for v in vs if self._canonical_rep(v) != cu}
            if new_vs:
                self._adj[u][sym] = new_vs
            else:
                del self._adj[u][sym]

def  what_sdsu():

    def show_classes(S):
        print(f"\n== classes ==")
        comps = sorted([sorted(c) for c in S.classes()])
        for i, comp in enumerate(comps, 1):
            print(f"  C{i}: {comp}")

    def show_orbit(S, item, allowed=None, title=None):
        print("Orbit")
        tag = f"(allowed={sorted(allowed)})" if allowed is not None else "(all symmetries)"

        orbit = S.orbit_items(item, allowed=allowed)
        for i, comp in enumerate(sorted([sorted(g) for g in orbit]), 1):
            print(f"  O{i}: {comp}")

    base = DisjointSetUnion(["a", "ma", "b", "mb", "c", "mc", "d", "md"])
    s = SymmetryDSU(base)
    s.relate("a", "ma", "mirror")
    s.relate("b", "mb", "mirror")
    s.relate("c", "mc", "mirror")
    s.relate("d", "md", "mirror")

    show_classes(s)

    print("ORBITS (MIRROR)")
    for x in base.representatives():
        print("Element:", x, end="   ")
        o = s.orbit_items(x, "mirror")
        print("  orbit", o)

    base["a"] = "ma"

    print("ORBITS (MIRROR)")
    for x in base.representatives():
        print("Element:", x, end="   ")
        o = s.orbit_items(x, "mirror")
        print("  orbit", o)

    base["a"] = "mb"

    print("ORBITS (MIRROR)")
    for x in base.representatives():
        print("Element:", x, end="   ")
        o = s.orbit_items(x, "mirror")
        print("  orbit", o)

if __name__ == "__main__":
    what_sdsu()
    pass
