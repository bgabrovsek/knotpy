from collections.abc import Iterable
from itertools import chain, combinations




def powerset(iterable):
    """Return the powerset of an iterable, e.g., for [1,2,3], obtain () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

#
#
# class LeveledSet:
#     """
#     A leveled set structure that keeps track of items at different levels.
#
#     - Allows inserting new elements at a specific level.
#     - Prevents duplicate entries across all levels.
#     - Provides fast lookups to check if an item exists at any level.
#     - Allows retrieval of all elements at a given level.
#     - Supports batch insertion via `extend()`.
#     - Supports iteration, allowing use in `min()`, `max()`, and loops.
#     """
#
#     def __init__(self, items=None):
#         """Initializes an empty leveled set structure."""
#         self.levels = [set()]  # List of sets, where each set stores diagrams at a level
#         self.global_set = set()  # Fast lookup to check if an item exists at any level
#
#         if items is not None:
#             # Ensure `items` is iterable (convert to set if it's not a list, tuple, or set)
#             if not isinstance(items, (list, tuple, set)):
#                 items = {items}  # Convert single item into a set
#             else:
#                 items = set(items)  # Convert list/tuple into a set
#
#             self.levels[0] = items
#             self.global_set.update(items)
#
#     def new_level(self, items=None):
#         """Creates a new level if the last level contains items."""
#         if self.levels[-1]:
#             self.levels.append(set())
#
#         if items:
#             if isinstance(items, (list, tuple, set)):
#                 self.extend(items)
#             else:
#                 self.add(items)
#
#     def remove_empy_levels(self):
#         """Removes empty levels from the end of the list."""
#         while self.levels and not self.levels[-1]:
#             self.levels.pop()
#
#     def add(self, item):
#         """
#         Adds an item to the specified level, ensuring it hasn't been added before.
#
#         :param item: The item (diagram) to add.
#         """
#         if item not in self.global_set:
#             self.levels[-1].add(item)
#             self.global_set.add(item)
#
#     def extend(self, items):
#         """
#         Adds multiple items at the specified level.
#
#         :param items: An iterable of items to add.
#         """
#         if not isinstance(items, (list, tuple, set)):
#             items = {items}  # Convert single item to a set
#         else:
#             items = set(items)  # Convert to set to remove duplicates
#
#         for item in items:
#             self.add(item)
#
#     def contains(self, item):
#         """
#         Checks if an item exists in any level.
#
#         :param item: The item (diagram) to check.
#         :return: True if the item exists, False otherwise.
#         """
#         return item in self.global_set
#
#     def get_level(self, level):
#         """
#         Retrieves all items at a specific level.
#
#         :param level: The level to retrieve.
#         :return: A set of items at the given level.
#         """
#         return self[level]
#
#     def union(self, other):
#         """
#         Returns the union of the global set with another set.
#
#         :param other: The set to union with.
#         :return: A new set containing all elements from both sets.
#         """
#         return self.global_set | set(other)  # why not global set?
#
#     def intersection(self, other):
#         """
#         Returns the intersection of the global set with another set.
#
#         :param other: The set to intersect with.
#         :return: A new set containing elements common to both sets.
#         """
#         return self.global_set & set(other)
#
#     def difference(self, other):
#         """
#         Returns the difference of the global set with another set.
#
#         :param other: The set to subtract.
#         :return: A new set containing elements in the global set but not in other.
#         """
#         return self.global_set - set(other)
#
#     def isdisjoint(self, other):
#         """
#         Checks if the global set has no elements in common with another set.
#
#         :param other: The set to check against.
#         :return: True if the sets are disjoint, False otherwise.
#         """
#         return self.global_set.isdisjoint(set(other))
#
#     def __getitem__(self, level):
#         if level < len(self.levels) or level < 0:
#             return self.levels[level]
#         return set()
#
#     def __iter__(self):
#         """
#         Allows iteration over all elements in the leveled set.
#         This makes it possible to use built-in functions like min(), max(), and sorted().
#         """
#         return iter(self.global_set)
#
#
#
#     # def __len__(self):
#     #     NotImplementedError()  # ambiguous (number of elements or number of levels)
#
#
#     def __repr__(self):
#         """Returns a string representation of the leveled set."""
#         return f"LeveledSet({self.levels})"


class LeveledSet:
    """
    A leveled set structure that optionally uses string representations for memory efficiency.

    - If `to_string` and `from_string` are provided, items are stored as strings internally.
    - If they are None, items are stored and accessed as-is.
    """

    def __init__(self, items=None, to_string=None, from_string=None):
        """
        Initializes the LeveledSet.

        :param items: Optional initial items to insert at level 0.
        :param to_string: Function to convert an object to a string (or None for identity).
        :param from_string: Function to convert a string back to object (or None for identity).
        """
        self.uses_conversion = to_string is not None and from_string is not None
        self.to_string = to_string
        self.from_string = from_string
        self.levels = []
        self.global_set = set()

        self.new_level(items if items else [])

    def new_level(self, items=None):
        """Creates a new level if the last one has items, and optionally adds to it."""

        if not self.levels or self.levels[-1]:

            self.levels.append(set())

        if items is not None:
            if isinstance(items, Iterable):
                self.extend(items)
            else:
                self.add(items)

    def remove_empty_levels(self):
        """Removes empty levels from the end."""
        while self.levels and not self.levels[-1]:
            self.levels.pop()

    def _convert_in(self, item):
        return self.to_string(item) if self.uses_conversion else item

    def _convert_out(self, item):
        return self.from_string(item) if self.uses_conversion else item

    def is_level_empty(self, level):
        return len(self.levels[level]) == 0

    def iter_level(self, level):
        """
        Generator that yields items from a specific level, applying conversion if needed.

        :param level: Integer index of the level (can be negative).
        """
        if -len(self.levels) <= level < len(self.levels):
            items = self.levels[level]  # we must capture the level’s contents immediately
            return (self._convert_out(s) for s in items)  # do not use yield!

        else:
            raise ValueError(f"Level {level} out of range")


    def add(self, item):
        """Adds a single item to the current level if not already present."""
        from knotpy.classes.planardiagram import PlanarDiagram
        # if not isinstance(item, PlanarDiagram):
        #     raise TypeError(f"LeveledSet only supports PlanarDiagram objects, added {item}")
        item_conv = self._convert_in(item)
        if item_conv not in self.global_set:
            self.levels[-1].add(item_conv)
            self.global_set.add(item_conv)

    def extend(self, items: Iterable):
        """Adds multiple items to the current level."""
        # #print(type(items))
        # def peek_generator(gen):
        #     if isinstance(gen, set | list | tuple):
        #         return next(iter(gen)), gen
        #     first = next(gen)
        #     print(type(gen), type(first))
        #     def new_gen():
        #         yield first
        #         yield from gen
        #
        #     return first, new_gen()
        #
        # peeked, items = peek_generator(items)
        # print("Peeked:", peeked)
        # if not isinstance(items, list | tuple | set):
        #     items = {items}
        # else:
        #     items = set(items)

        # print("extending with", items)
        for item in items:
            self.add(item)

    def contains(self, item):
        """Checks whether an item exists in any level."""
        return self._convert_in(item) in self.global_set

    # def get_level(self, level):
    #     """
    #     Retrieves all items at a specific level, converted to original form if using conversion.
    #     """
    #     return {self._convert_out(s) for s in self[level]}

    def union(self, other):
        return self.global_set | other.global_set

    def intersection(self, other):
        return self.global_set & other.global_set

    def difference(self, other):
        return self.global_set - other.global_set

    def isdisjoint(self, other):
        return self.global_set.isdisjoint(other.global_set)

    # support for get_item removed, since one can then fill the level with non-unique elements
    # def __getitem__(self, level):
    #     #if 0 <= level < len(self.levels):
    #     return self.levels[level]
    #     #return set()

    def __iter__(self):
        """Iterates over all elements, converted if using conversion."""
        return (self._convert_out(s) for s in self.global_set)