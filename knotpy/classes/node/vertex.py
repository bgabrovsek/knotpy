from __future__ import annotations

"""Vertex node type.

A vertex is a graph-like point in the diagram with incident arcs (endpoints)
emitting from it. It imposes no special constraints beyond what ``Node`` provides.
"""

from knotpy.classes.node import Node

__all__ = ["Vertex"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovšek@pef.uni-lj.si>"


class Vertex(Node):
    """Graph vertex with zero-dimensional support and incident endpoints."""

    def __str__(self) -> str:
        """Return a compact string representation.

        Returns:
            str: ``"V"`` prefix followed by the base ``Node`` representation.
        """
        return "V" + super().__str__()


if __name__ == "__main__":
    pass
