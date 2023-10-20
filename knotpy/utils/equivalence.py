
class EquivalenceRelation(dict):
    """Partitions a set of objects into equivalence classes.
    Each key/item of the dictionary is the object and the values are sets that represent the class"""
    def __init__(self, items=[]):
        """
        :param items: iterable of objects.
        """
        super().__init__()
        for item in items:
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

    def classes(self):
        return set(tuple(c) for c in self.values())


if __name__ == "__main__":
    # four equivalent classes
    e = EquivalenceRelation([0,1,2])
    e += 3
    e += 4
    print(e.classes())

    e[0] = 3  # join classes 0 and 3
    print(e.classes())
    e[3] = 4  # join classes 4 and 3
    print(e.classes())
    e[1] = 2
    print(e.classes())

