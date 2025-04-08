from dataclasses import field
from typing import Hashable

from knotpy.utils.decorators import total_ordering_from_compare
from knotpy.utils.dict_utils import compare_dicts


#@dataclass(unsafe_hash=True)
@total_ordering_from_compare
class Endpoint:
    node: Hashable
    position: int
    attr: dict = field(default_factory=dict, compare=False)

    def __init__(self, node, position, **attr):
        self.node = node
        self.position = int(position)
        self.attr = dict()
        self.attr.update(attr)

    def __iter__(self):
        # for unpacking
        return iter((self.node, self.position))

    def __str__(self):
        s = ""
        if isinstance(self.node, str):
            s += f"{self.node}{self.position}"  # ⇢⇠⤍➤⤞
        else:
            s += f"({self.node},{self.position})"
        if "color" in self.attr:
            s += "=" + str(self.attr["color"])
        return s

    def __hash__(self):
        return hash((type(self), self.attr.get("color", None), self.node, self.position))

    def _compare(self, other, compare_attributes=False):

        # compare types
        if type(self) is Endpoint and (type(other) is IngoingEndpoint or type(other) is OutgoingEndpoint):
            raise TypeError("Cannot compare unoriented endpoints with oriented endpoints")

        if type(other) is Endpoint and (type(self) is IngoingEndpoint or type(self) is OutgoingEndpoint):
            raise TypeError("Cannot compare oriented endpoints with unoriented endpoints")

        if type(self) is IngoingEndpoint and type(self) is OutgoingEndpoint:
            return 1

        if type(self) is OutgoingEndpoint and type(self) is IngoingEndpoint:
            return -1

        if self.node != other.node:
            return ((self.node > other.node) * 2) - 1

        if self.position != other.position:
            return ((self.position > other.position) * 2) - 1

        if compare_attributes:
            return compare_dicts(self.attr, other.attr, compare_attributes if compare_attributes in (set, list, tuple) else None)

        return 0

    def __setitem__(self, key, value):
        self.attr[key] = value
        #print(key,"to",value)

    def __getitem__(self, key):
        return self.attr.get(key, None)

    def get(self, key, __default=None):
        return self.attr.get(key, __default)

    def __contains__(self, key):
        return key in self.attr

    @staticmethod
    def reverse_type():
        return Endpoint

    @staticmethod
    def is_oriented():
        return False

    def __repr__(self):
        return str(self)


class IngoingEndpoint(Endpoint):

    def __str__(self):
        s = ""
        if isinstance(self.node, str):
            s = f"{self.node}{self.position}i"  # ⇢⇠⤍➤⤞
        else:
            s = f"({self.node},{self.position})i"

        if "color" in self.attr:
            s += "=" + str(self.attr["color"])
        return s

    @staticmethod
    def reverse_type():
        return OutgoingEndpoint

    @staticmethod
    def is_oriented():
        return True



class OutgoingEndpoint(Endpoint):
    def __str__(self):
        s = ""
        if isinstance(self.node, str):
            s = f"{self.node}{self.position}o"  # ⇢⇠⤍➤⤞
        else:
            s = f"({self.node},{self.position})o"

        if "color" in self.attr:
            s += "=" + str(self.attr["color"])
        return s

    @staticmethod
    def reverse_type():
        return IngoingEndpoint

    @staticmethod
    def is_oriented():
        return True


if __name__ == "__main__":
    pass