""" Connected and disjoint sum of diagrams. Loosely supported"""
from typing import Union

from knotpy.classes.planardiagram import PlanarDiagram


class PlanarDiagramExpression:
    """Base class for diagram sum expressions."""
    components = []
    attr = dict()

    def __len__(self):
        return len(self.components)

    def __iter__(self):
        return iter(self.components)

    @property
    def name(self):
        """Name identifier of planar diagram."""
        return self.attr.get("name", "")


    def is_oriented(self):
        val = [_.is_oriented() for _ in self.components]
        if all(val):
            return True
        if any(val):
            raise ValueError("Mixed oriented and non-oriented components")
        return False


class DisjointSum(PlanarDiagramExpression):
    """Disjoint sum of one or more planar diagrams"""

    def __init__(self, *args, **attr):
        # Flatten nested DisjointSum instances
        self.components = []
        self.attr = attr

        for arg in args:
            if isinstance(arg, DisjointSum):
                self.components.extend(arg.components)
            elif isinstance(arg, (PlanarDiagram, ConnectedSum)):
                self.components.append(arg)
            else:
                raise TypeError(f"Cannot make a disjoint sum of instance of type {type(arg)}")

    def __ior__(self, other):

        if isinstance(other, DisjointSum):
            self.components.extend(other.components)
        else:
            self.components.append(other)
        return self

    def __or__(self, other):
       return DisjointSum(self, other)

    def __repr__(self):
        return " ⊔ ".join(map(str, self.components))



class ConnectedSum(PlanarDiagramExpression):

    def __init__(self, *args, **attr):
        # Flatten nested Connected sum
        self.components = []
        self.attr = attr
        for arg in args:
            if isinstance(arg, DisjointSum):
                raise TypeError("Cannot make a connected sum with a disjoint sum (ambiguity)")
            if isinstance(arg, ConnectedSum):
                self.components.extend(arg.components)
            else:
                self.components.append(arg)


    def __ior__(self, other):
        # untested
        if isinstance(other, ConnectedSum):
            self.components.extend(other.components)
        if isinstance(other, DisjointSum):
            raise TypeError("Cannot make a connected sum with a disjoint sum (ambiguity)")
        else:
            self.components.append(other)

        return self

    def __or__(self, other):
        # untested
        return ConnectedSum(*self, other)

    def __repr__(self):
        return " # ".join(map(str, self.components))

def flatten(k: PlanarDiagramExpression):
    raise NotImplementedError()


