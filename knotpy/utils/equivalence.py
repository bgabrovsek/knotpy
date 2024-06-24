__all__ = ["EquivalenceRelation"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


class EquivalenceRelation(dict):
    """Partitions a set of objects into equivalence classes.
    Each key/item of the dictionary is the object and the values are sets that represent the class"""
    def __init__(self, iterable=None):
        """
        :param iterable: iterable of objects.
        """
        iterable = iterable or []
        super().__init__()
        for item in iterable:
            super().__setitem__(item, {item})

    def __iadd__(self, item):
        """We add a new item (and class) by the += operator."""
        if item not in self:
            super().__setitem__(item, {item})
        return self

    def __setitem__(self, item1, item2):
        """Join classes of item1 and item2."""
        self.__iadd__(item1)
        self.__iadd__(item2)
        new_set = self[item1] | self[item2]
        for item in new_set:
            super().__setitem__(item, new_set)

    def representatives(self):
        for cls in self.classes():
            yield min(cls)

    def classes(self):
        already_yielded = []
        for c in self.values():
            if c not in already_yielded:
                yield c
                already_yielded.append(c)

    def number_of_classes(self):
        return sum(1 for c in self.classes())

if __name__ == "__main__":
    # four equivalent classes
    e = EquivalenceRelation([0,1,2])
    e += 3
    e += 4

    e[0] = 0
    e[0] = 3  # join classes 0 and 3
    e[3] = 3
    e[5] = 5
    e[3] = 4  # join classes 4 and 3
    e[1] = 2
    print(list(e.classes()))
    print(list(e.representatives()))

"""

[{0}, {1}, {2}, {3}, {4}]
[{0, 3}, {1}, {2}, {4}]
[{0, 3, 4}, {1}, {2}]
[{0, 3, 4}, {1, 2}]

[{0}, {1}, {2}, {3}, {4}]
[{0, 3}, {1}, {2}, {4}, {5}]
[{0, 3, 4}, {1}, {2}, {5}]
[{0, 3, 4}, {1, 2}, {5}]

"""