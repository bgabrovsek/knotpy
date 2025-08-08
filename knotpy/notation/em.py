# knotpy/notation/em.py

from __future__ import annotations

"""Modified Ewing–Millett (EM) notation utilities.

The core EM notation is a dict mapping each node to a CCW-ordered list of
tuples ``(adjacent_node, adjacent_position)`` describing where each endpoint
connects on the neighbor.

Example (graph A—B—D with C connected to both A and B):

    {
        "A": [("B", 0), ("C", 1)],
        "B": [("A", 0), ("D", 0), ("C", 0)],
        "C": [("B", 2), ("A", 1)],
        "D": [("B", 1)],
    }

The “condensed” EM notation for single-letter nodes is a CSV of tokens, one per
node in alphabetical order, where each token concatenates neighbor-letter and
neighbor-position pairs (CCW). For the example above:

    "b0c1,a0d0c0,b2a1,b1"
"""

import re
import string
from ast import literal_eval
from typing import Any, Dict, Iterable, Mapping, Tuple

from knotpy.classes.planardiagram import OrientedPlanarDiagram, PlanarDiagram
from knotpy.classes.node import Crossing, Vertex
from knotpy.classes.endpoint import Endpoint

__all__ = ["to_em_notation", "from_em_notation", "to_condensed_em_notation", "from_condensed_em_notation"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovšek@pef.uni-lj.si>"


def to_em_notation(g: PlanarDiagram) -> Dict[Any, list[tuple[Any, int]]]:
    """Return EM dict notation of a planar diagram.

    For each node, returns a CCW-ordered list of ``(neighbor, neighbor_pos)`` tuples.
    This uses the diagram’s endpoint “twin” relation to find the adjacent endpoint.

    Args:
        g: Planar diagram.

    Returns:
        dict: Mapping ``node -> [(neighbor, neighbor_pos), ...]``.

    Examples:
        >>> from knotpy.classes.planardiagram import PlanarDiagram
        >>> d = PlanarDiagram()
        >>> d.add_vertices_from(["a", "b"])
        >>> d.set_arc((("a", 0), ("b", 0)))
        >>> em = to_em_notation(d)
        >>> em["a"] == [("b", 0)]
        True
    """
    em: Dict[Any, list[tuple[Any, int]]] = {}
    for v in g.nodes:
        adj_list: list[tuple[Any, int]] = []
        for ep in g.nodes[v]:
            twin = g.twin(ep)
            adj_list.append((twin.node, twin.position))
        em[v] = adj_list
    return em


def from_em_notation(data: Mapping[Any, Iterable[tuple[Any, int]]] | str, oriented: bool = False) -> PlanarDiagram:
    """Create a planar diagram from EM dict (or stringified dict) notation.

    The input should map each node to a CCW-ordered list of
    ``(neighbor, neighbor_position)`` pairs.

    Args:
        data: EM dict, or a string that safely evaluates to such a dict.
        oriented: Whether to construct an oriented diagram (not implemented).

    Returns:
        PlanarDiagram: Parsed diagram.

    Raises:
        NotImplementedError: If ``oriented=True``.
        ValueError: On malformed inputs.
    """
    if oriented:
        raise NotImplementedError("Oriented EM import not implemented yet.")

    if isinstance(data, str):
        try:
            data = literal_eval(data)
        except Exception as e:
            raise ValueError("Failed to parse EM string with literal_eval.") from e

    if not isinstance(data, Mapping):
        raise ValueError("EM data must be a mapping of node -> iterable of (neighbor, position).")

    g = PlanarDiagram()

    # First pass: add nodes with appropriate degrees
    for node, adj in data.items():
        adj_list = list(adj)
        degree = len(adj_list)
        node_type = Crossing if degree == 4 else Vertex
        g.add_node(node_for_adding=node, create_using=node_type, degree=degree)

    # Second pass: set endpoints using provided neighbor positions
    for node, adj in data.items():
        for pos, (u, u_pos) in enumerate(adj):
            g.set_endpoint((node, pos), (u, u_pos), create_using=Endpoint)

    return g


def to_condensed_em_notation(g: PlanarDiagram, separator: str = ",") -> str:
    """Return condensed EM notation for diagrams with single-letter node labels.

    Constraints:
        - Nodes must be sortable and of the same type (e.g., all strings or all ints).
        - At most 52 nodes (a–zA–Z).

    Args:
        g: Diagram to serialize.
        separator: Token separator (default: comma).

    Returns:
        str: Condensed EM string (alphabetical node order).

    Raises:
        ValueError: If node count exceeds 52.
        TypeError: If nodes are not mutually comparable for sorting.
    """
    if len(g.nodes) > len(string.ascii_letters):
        raise ValueError(f"Condensed EM notation is undefined for > {len(string.ascii_letters)} nodes.")

    try:
        nodes = sorted(g.nodes)
    except TypeError as e:
        raise TypeError("Condensed EM notation requires nodes of a single, mutually comparable type.") from e

    # Map nodes to letters in alphabetical order
    node_label = dict(zip(nodes, string.ascii_letters[: len(nodes)]))

    tokens: list[str] = []
    for v in nodes:
        token = "".join(node_label[ep.node] + str(ep.position) for ep in g.nodes[v])
        tokens.append(token)

    return separator.join(tokens)


def from_condensed_em_notation(data: str, separator: str = ",", oriented: bool = False) -> PlanarDiagram:
    """Parse condensed EM notation into a planar diagram.

    Token format per node (CCW): ``<neighbor-letter><neighbor-position>...``.
    Nodes are assigned in alphabetical order: a, b, c, ...

    Args:
        data: Condensed EM string.
        separator: Token separator used in the string (default: comma).
        oriented: Whether to construct an oriented diagram (not implemented).

    Returns:
        PlanarDiagram: Parsed diagram.

    Raises:
        NotImplementedError: If ``oriented=True``.
        ValueError: For malformed tokens.
    """
    if oriented:
        raise NotImplementedError("Oriented condensed EM import not implemented yet.")

    s = (" " if separator == " " else "").join(data.split())
    tokens = s.split(separator) if s else []
    g = PlanarDiagram()

    for idx, token in enumerate(tokens):
        node = string.ascii_letters[idx]
        # Split into letters and integers
        adj_nodes = re.findall(r"[a-zA-Z]", token)
        adj_positions = re.findall(r"\d+", token)

        if len(adj_nodes) != len(adj_positions):
            raise ValueError(f"Malformed condensed EM token: {token!r}")

        degree = len(adj_nodes)
        node_type = Crossing if degree == 4 else Vertex
        g.add_node(node_for_adding=node, create_using=node_type, degree=degree)

        for pos, (u, u_pos) in enumerate(zip(adj_nodes, adj_positions)):
            g.set_endpoint((node, pos), (u, int(u_pos)), create_using=Endpoint)

    return g


if __name__ == "__main__":
    pass
