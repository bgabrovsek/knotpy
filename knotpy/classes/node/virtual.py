from __future__ import annotations

"""Virtual crossing node type.

A virtual crossing is a degree-4 node used in virtual knot theory. Unlike a
classical crossing, it carries **no** over/under information—its four incident
endpoints are treated symmetrically.
"""

from typing import Any, Sequence

from knotpy.classes.node.node import Node

__all__ = ["VirtualCrossing"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"


class VirtualCrossing(Node):
    """Degree-4 node without over/under semantics (virtual knot theory)."""

    def __init__(self, incoming_node_data: Sequence[Any] | None = None, degree: int = 4, **attr: Any) -> None:
        """Initialize a virtual crossing (always degree 4).

        Args:
            incoming_node_data: Optional list/sequence of incident endpoints. If shorter
                than 4, it will be padded; if longer, an error is raised.
            degree: Must be 4; provided for API symmetry and validated.
            **attr: Node attributes.

        Raises:
            ValueError: If ``degree`` is not 4.
        """
        degree = degree or 4
        if degree != 4:
            raise ValueError("Cannot create a virtual crossing with degree not equal to four.")
        super().__init__(incoming_node_data, degree=degree, **attr)

    def mirror(self) -> "VirtualCrossing":
        """Return the mirrored virtual crossing.

        Notes:
            For virtual crossings, mirroring has no effect (no over/under data).

        Returns:
            VirtualCrossing: ``self`` (identity).
        """
        # Mirror is identity for virtual crossings.
        return self

    def __str__(self) -> str:
        """Return a compact string representation.

        Returns:
            str: ``"V"`` prefix followed by the base ``Node`` representation.
        """
        return "V" + super().__str__()


if __name__ == "__main__":
    pass
