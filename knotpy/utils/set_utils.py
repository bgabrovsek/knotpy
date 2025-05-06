from itertools import chain, combinations

def powerset(iterable):
    """Return the powerset of an iterable, e.g., for [1,2,3], obtain () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))



class LeveledSet:
    """
    A leveled set structure that keeps track of items at different levels.

    - Allows inserting new elements at a specific level.
    - Prevents duplicate entries across all levels.
    - Provides fast lookups to check if an item exists at any level.
    - Allows retrieval of all elements at a given level.
    - Supports batch insertion via `extend()`.
    - Supports iteration, allowing use in `min()`, `max()`, and loops.
    """

    def __init__(self, items=None):
        """Initializes an empty leveled set structure."""
        self.levels = [set()]  # List of sets, where each set stores diagrams at a level
        self.global_set = set()  # Fast lookup to check if an item exists at any level

        if items is not None:
            # Ensure `items` is iterable (convert to set if it's not a list, tuple, or set)
            if not isinstance(items, (list, tuple, set)):
                items = {items}  # Convert single item into a set
            else:
                items = set(items)  # Convert list/tuple into a set

            self.levels[0] = items
            self.global_set.update(items)

    def new_level(self, items=None):
        """Creates a new level if the last level contains items."""
        if self.levels[-1]:
            self.levels.append(set())

        if items:
            if isinstance(items, (list, tuple, set)):
                self.extend(items)
            else:
                self.add(items)

    def add(self, item):
        """
        Adds an item to the specified level, ensuring it hasn't been added before.

        :param item: The item (diagram) to add.
        """
        if item not in self.global_set:
            self.levels[-1].add(item)
            self.global_set.add(item)

    def extend(self, items):
        """
        Adds multiple items at the specified level.

        :param items: An iterable of items to add.
        """
        if not isinstance(items, (list, tuple, set)):
            items = {items}  # Convert single item to a set
        else:
            items = set(items)  # Convert to set to remove duplicates

        for item in items:
            self.add(item)

    def contains(self, item):
        """
        Checks if an item exists in any level.

        :param item: The item (diagram) to check.
        :return: True if the item exists, False otherwise.
        """
        return item in self.global_set

    def get_level(self, level):
        """
        Retrieves all items at a specific level.

        :param level: The level to retrieve.
        :return: A set of items at the given level.
        """
        return self[level]

    def union(self, other):
        """
        Returns the union of the global set with another set.

        :param other: The set to union with.
        :return: A new set containing all elements from both sets.
        """
        return self.global_set | set(other)  # why not global set?

    def intersection(self, other):
        """
        Returns the intersection of the global set with another set.

        :param other: The set to intersect with.
        :return: A new set containing elements common to both sets.
        """
        return self.global_set & set(other)

    def difference(self, other):
        """
        Returns the difference of the global set with another set.

        :param other: The set to subtract.
        :return: A new set containing elements in the global set but not in other.
        """
        return self.global_set - set(other)

    def isdisjoint(self, other):
        """
        Checks if the global set has no elements in common with another set.

        :param other: The set to check against.
        :return: True if the sets are disjoint, False otherwise.
        """
        return self.global_set.isdisjoint(set(other))

    def __getitem__(self, level):
        if level < len(self.levels) or level < 0:
            return self.levels[level]
        return set()

    def __iter__(self):
        """
        Allows iteration over all elements in the leveled set.
        This makes it possible to use built-in functions like min(), max(), and sorted().
        """
        return iter(self.global_set)



    # def __len__(self):
    #     NotImplementedError()  # ambiguous (number of elements or number of levels)


    def __repr__(self):
        """Returns a string representation of the leveled set."""
        return f"LeveledSet({self.levels})"