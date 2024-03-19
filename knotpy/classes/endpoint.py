from dataclasses import dataclass, field
from typing import Hashable

from knotpy.utils.decorators import total_ordering_py3
from knotpy.utils.dict_utils import compare_dicts


@dataclass(unsafe_hash=True)
@total_ordering_py3
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
    def py3_cmp(self, other, compare_attributes=False):

        if type(self).__name__ != type(other).__name__:
            return ((type(self).__name__ > type(other).__name__) << 1) - 1

        if self.node != other.node:
            return ((self.node > other.node) << 1) - 1

        if self.position != other.position:
            return ((self.position > other.position) << 1) - 1

        if compare_attributes:
            return compare_dicts(self.attr, other.attr)

        return 0

    def __setitem__(self, key, value):
        self.attr[key] = value
        #print(key,"to",value)

    def __getitem__(self, key):
        return self.attr[key]

    def get(self, key, __default=None):
        return self.attr.get(key, __default)

    def __contains__(self, key):
        return key in self.attr



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
if __name__ == "__main__":
    pass