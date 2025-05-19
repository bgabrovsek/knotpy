"""
The Union-Find structure, also known as the Disjoint Set Union (DSU) structure, is an efficient data structure used to
manage a partition of a set into disjoint (non-overlapping) subsets. It’s particularly useful in scenarios where we need
to frequently determine whether two elements are in the same subset, and to unite two subsets into a single subset.
"""

class DisjointSetUnion:
    """
    A Disjoint Set Union (DSU), also known as a Union-Find data structure,
    manages a partition of a set into disjoint (non-overlapping) subsets.
    It supports finding the set representative, and union operation to merge sets.

    :param iterable: An optional iterable of hashable elements to initialize the DSU.
    :type iterable: Iterable
    """

    def __init__(self, iterable=None):
        """
        Initializes the DSU. If elements are provided, each element is initialized in its own set.

        :param iterable: An optional iterable of hashable elements to initialize the DSU.
        :type iterable: Iterable
        """
        self.parent = {}
        self.rank = {}
        if iterable:
            for item in iterable:
                self.add(item)

    def add(self, item):
        """Add an item to the DSU if not already present, initializing its set."""
        if item not in self.parent:
            self.parent[item] = item
            self.rank[item] = 0

    def find(self, item):
        """
        Finds the representative of the set containing 'item'.

        :param item: The item to find.
        :type item: Hashable
        :return: The representative of the set containing 'item'.
        :rtype: Hashable
        """
        if item not in self.parent:
            return None
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])  # Path compression
        return self.parent[item]

    def union(self, item1, item2):
        """
        Performs the union of the sets that contain set1 and set2.

        :param item1: An element of the first set.
        :param item2: An element of the second set.
        :type item1: Hashable
        :type item2: Hashable
        """
        root1 = self.find(item1)
        root2 = self.find(item2)

        if root1 is not None and root2 is not None and root1 != root2:
            if self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            elif self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1

    def __iadd__(self, item):
        """Add an item to the DSU if not already present, initializing its set."""
        self.add(item)
        return self

    def __setitem__(self, item1, item2):
        """Performs the union of the sets that contain set1 and set2. Add item1 or item2 as new items if they do not
         exist """
        self.add(item1)
        self.add(item2)
        self.union(item1, item2)

    def __iter__(self):
        """
        Iterator over the unique sets. Each yielded item is a set of elements
        belonging to the same connected component.
        """
        seen = set()
        for item in self.parent:
            root = self.find(item)
            if root not in seen:
                seen.add(root)
                yield self.set(root)

    @property
    def elements(self):
        for element in self.parent:
            yield element

    def set(self, item):
        """
        Returns the set of items connected to 'item'.

        :param item: Any member of the set.
        :type item: Hashable
        :return: A set containing all items in the connected component of 'item'.
        :rtype: set
        """
        representative = self.find(item)
        return {x for x in self.parent if self.find(x) == representative}


    def representatives(self):
        """ Iterate over the representatives of each set."""
        for s in self:
            yield min(s)

    def classes(self):
        return list(self)

    def __len__(self) -> int:
        """
        Returns the number of disjoint sets in the union-find structure.

        Returns:
            int: The number of disjoint sets.
        """
        return len(set(self.find(x) for x in self.parent))

    def __repr__(self):
        """
        Provides a detailed string representation of the DSU, showing the parent and rank tables.
        """
        return f"DisjointSetUnion({self.parent}, {self.rank})"

    def __str__(self):
        """
        Provides a string representation of the DSU in terms of its unique sets.
        """
        return f"{list(self)}"

    def to_dict(self):
        """
        Convert the DSU to a dictionary mapping each representative to its elements (that are not the representative).
        """
        return {
            min(g): g - {min(g), } for g in self
        }
       # return {r: {item for item in self.parent if self.parent[item] == r and item != r} for r in self.representatives()}

if __name__ == "__main__":
    # DSU test
    dsu = DisjointSetUnion("abcdefg")
    dsu["a"] = "b"
    dsu["c"] = "d"
    dsu["e"] = "f"
    dsu["b"] = "c"
    print(dsu)
    print("Groups:", [group for group in dsu])
    print("Classes:", [classes for classes in dsu.classes()])
    print("Representatives:", [rep for rep in dsu.representatives()])
    print("Elements:", [e for e in dsu.elements])
    print("Dictionary:", dsu.to_dict())
