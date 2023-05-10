from dataclasses import dataclass, field
from typing import Hashable


@dataclass(order=True, unsafe_hash=True)
class Endpoint:
    node: Hashable
    position: int
    attr: dict = field(default_factory=dict, compare=False)

    def __init__(self, node, position, **attr):
        self.node = node
        self.position = int(position)
        self.attr = dict()
        self.attr.update(attr)

    def __str__(self):
        if isinstance(self.node, str):
            return f"{self.node}{self.position}"
        else:
            return f"({self.node},{self.position})"

    def __repr__(self):
        return str(self)


class OrientedEndpoint(Endpoint):

    outgoing: bool

    def __init__(self, node, position, outgoing, **attr):
        super().__init__(node, position, **attr)
        self.outgoing = bool(outgoing)
