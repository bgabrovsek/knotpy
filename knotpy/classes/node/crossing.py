from __future__ import annotations

"""Classical crossing node type.

A classical crossing is a degree-4 node with over/under information:
positions 0 and 2 form one strand, 1 and 3 form the other. The oriented
endpoint types (:class:`IngoingEndpoint`, :class:`OutgoingEndpoint`) determine
the crossing sign.
"""

from typing import Any, Sequence

from knotpy.classes.node.node import Node
from knotpy.classes.endpoint import Endpoint, OutgoingEndpoint, IngoingEndpoint

__all__ = ["Crossing"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovšek@pef.uni-lj.si>"


class Crossing(Node):
    """Degree-4 node with over/under semantics (classical knot theory)."""

    def __init__(self, incoming_node_data: Sequence[Any] | None = None, degree: int = 4, **attr: Any) -> None:
        """Initialize a classical crossing (always degree 4).

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
            raise ValueError("Cannot create a crossing with degree not equal to four.")
        super().__init__(incoming_node_data, degree=degree, **attr)

    def sign(self) -> int:
        """Return the crossing sign (+1 or -1) for oriented endpoints.

        The sign is determined by the orientation of the two strands:
        endpoints of the same orientation at positions (0,1) imply ``-1``;
        differing orientations imply ``+1``.

        Returns:
            int: ``+1`` or ``-1``.

        Raises:
            TypeError: If any incident endpoint is unoriented (:class:`Endpoint`).
        """
        if any(type(ep) is Endpoint for ep in self._inc):
            raise TypeError("Cannot determine the sign of an unoriented crossing.")
        # out/out, in/in → -1; out/in or in/out → +1
        return -1 if type(self._inc[0]) is type(self._inc[1]) else 1

    def __str__(self) -> str:
        """Return a compact string representation.

        Returns:
            str: ``"X"`` prefix followed by the base ``Node`` representation.
        """
        return "X" + super().__str__()


if __name__ == "__main__":
    pass
