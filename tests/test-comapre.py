
from functools import total_ordering

@total_ordering
class dd(Set):
    __slots__ = ("_comparison_structure",)

    def __eq__(self, other):
        return self._name == other._name

    def __lt__(self, other):
        s = self._comparison_structure
        o = other._comparison_structure

        return s < o


@total_ordering
class ddd:
    __slots__ = ("_comparison_structure",)

    def __eq__(self, other):
        print("Dummy")
        return False

    def __lt__(self, other):
        print("Dummy lt")
        return False


class my(ddd, dd):

    def __init__(self, name):
        self._name = name

    @property
    def _comparison_structure(self):
        return self._name

a = my(3)
b = my(3)

print(a == b, a < b, a <= b)

b._name = 1
print(a == b, a < b, a <= b)
