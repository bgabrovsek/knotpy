from dataclasses import dataclass, field
from typing import Hashable

from knotpy.utils.decorators import total_order_py3
from knotpy.utils.combinatorics import cmp_dict


@dataclass(unsafe_hash=True)
@total_order_py3
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
        if isinstance(self.node, str):
            return f"{self.node}{self.position}"  # ⇢⇠⤍➤⤞
        else:
            return f"({self.node},{self.position})"

    def py3_cmp(self, other, compare_attributes=False):

        if type(self).__name__ != type(other).__name__:
            return ((type(self).__name__ > type(other).__name__) << 1) - 1

        if self.node != other.node:
            return ((self.node > other.node) << 1) - 1

        if self.position != other.position:
            return ((self.position > other.position) << 1) - 1

        if compare_attributes:
            return cmp_dict(self.attr, other.attr)

        return 0

    def __repr__(self):
        return str(self)


class IngoingEndpoint(Endpoint):
    def __str__(self):
        return f"in({self.node},{self.position})"


class OutgoingEndpoint(Endpoint):
    def __str__(self):
        return f"out({self.node},{self.position})"

