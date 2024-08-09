from itertools import chain

class MultiLevelSet:
    """
    MultiLevelSet is a class that manages multiple levels of sets, ensuring that elements are unique across all levels.
    """
    def __init__(self, level_zero_elements=None):
        self.levels = []
        if level_zero_elements is not None:
            self.add_to_level(0, level_zero_elements)

    def add_to_level(self, level, element):
        while len(self.levels) <= level:  # Ensure there are enough levels
            self.levels.append(set())

        if isinstance(element, set) or isinstance(element, list) or isinstance(element, tuple):
            for el in element:
                self.add_to_level(level, el)
            return

        if not any(element in self.levels[i] for i in reversed(range(level))):
            self.levels[level].add(element)

    def __getitem__(self, level):
        # Ensure there are enough levels
        while len(self.levels) <= level:
            self.levels.append(set())
        return self.levels[level]

    def __setitem__(self, level, element):
        self.add_to_level(level, element)

    def __len__(self):
        return len(self.levels)

    def __repr__(self):
        return '\n'.join(f"Level {i}: {len(level)} element{'s' if len(level)!=1 else ''}" for i, level in enumerate(self.levels))

    def __iter__(self):
        return chain(*self.levels)

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