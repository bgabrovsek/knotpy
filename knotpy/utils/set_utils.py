from itertools import chain


class LevelSet:
    def __init__(self, elements=None):
        self.levels = {}
        if elements:
            self.extend(elements, level=0)

    def add(self, element, level):
        """Add an element to a specific level, if it's not already present."""
        if level not in self.levels:
            self.levels[level] = set()
        if element not in self:
            self.levels[level].add(element)

    def extend(self, elements, level):
        """Add multiple elements to a specific level, if they're not already present."""
        if level not in self.levels:
            self.levels[level] = set()
        for element in elements:
            if element not in self:
                self.levels[level].add(element)

    def __contains__(self, element):
        """Check if an element exists in any level."""
        return any(element in level for level in self.levels.values())

    def __getitem__(self, level):
        """Get the set of elements at a specific level."""
        return self.levels.get(level, set())

    def __iter__(self):
        """Iterate over all elements in the LevelSet, independent of level."""
        seen = set()
        for level in self.levels.values():
            for element in level:
                if element not in seen:
                    seen.add(element)
                    yield element

    def __repr__(self):
        """String representation of the LevelSet."""
        return f"LevelSet({self.levels})"

#
#
# m = MultiLevelSet({0})
# m.add_to_level(1, {0,1,2,3,})
# m.add_to_level(2, {5,6,1,1})
# m.add_to_level(3, {0,6,1,1})
#
# print(m)
#
# print(bool(m[0]), bool(m[1]), bool(m[2]), bool(m[3]),)
#
# for x in m:
#     print(x)