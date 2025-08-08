# knotpy/notation/plantri.py

from __future__ import annotations

"""Plantri planar code notation helpers.

Refs:
- https://users.cecs.anu.edu.au/~bdm/plantri/
- https://users.cecs.anu.edu.au/~bdm/plantri/plantri-guide.txt
"""

from string import ascii_letters
import re
from typing import Iterable

from knotpy.classes.planardiagram import PlanarDiagram

__all__ = ["from_plantri_notation", "to_plantri_notation"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovšek@pef.uni-lj.si>"


def to_plantri_notation(g: PlanarDiagram) -> str:
    """Convert a planar diagram to **plantri** notation (alphabetical form).

    Plantri’s alphabetical notation lists each node’s neighbors **in CW order**.
    Our diagrams store endpoints CCW, so we iterate the diagram’s stored order
    directly and rely on the fact that the notation consumer understands CW.
    (If your internal storage differs, you may need to reverse per node.)

    The output looks like: ``"5 bcde,aedc,abd,acbe,adb"`` (node count + space + CSV).

    Args:
        g: Planar diagram to serialize.

    Returns:
        str: Plantri alphabetical notation.

    Raises:
        ValueError: If the diagram has more than 52 nodes (``a–zA–Z``).

    Examples:
        >>> from knotpy.classes.planardiagram import PlanarDiagram
        >>> d = PlanarDiagram()
        >>> d.add_vertices_from(["a", "b", "c"])
        >>> d.set_arc((("a", 0), ("b", 0)))
        >>> d.set_arc((("b", 1), ("c", 0)))
        >>> to_plantri_notation(d).split()[0].isdigit()
        True
    """
    if g.number_of_nodes > len(ascii_letters):
        raise ValueError(f"Number of nodes cannot exceed {len(ascii_letters)} (a–zA–Z).")

    # Map sorted node ids to letters a,b,c,... (mixed types sort may raise; user should keep ids sortable)
    node_ids = list(sorted(g.nodes))
    label_map = dict(zip(node_ids, ascii_letters))  # type: ignore[arg-type]

    parts: list[str] = []
    for v in g.nodes:
        # neighbors in stored order
        neighbors = "".join(label_map[ep.node] for ep in g.nodes[v])
        parts.append(neighbors)

    return f"{g.number_of_nodes} " + ",".join(parts)


def from_plantri_notation(graph_string: str) -> PlanarDiagram:
    """Parse a **plantri** notation string into a :class:`PlanarDiagram`.

    Supports:
      - **Alphabetical**: ``"5 bcde,aedc,abd,acbe,adb"``
      - **Numeric**: ``"7: 1[2 3 4 5] 2[1 5 6 3] ..."``

    The plantri order is **CW**; this function reverses each adjacency string
    to obtain **CCW** before building the diagram.

    Args:
        graph_string: Plantri string (alphabetical or numeric).

    Returns:
        PlanarDiagram: New diagram with vertices ``'a','b','c',...`` and arcs set.

    Raises:
        ValueError: If vertex count exceeds 52 (``a–zA–Z``) or parsing fails.

    Examples:
        >>> s = "5 bcde,aedc,abd,acbe,adb"
        >>> d = from_plantri_notation(s)
        >>> isinstance(d, PlanarDiagram)
        True
        >>> d.number_of_nodes == 5
        True
    """
    s = graph_string.strip()
    if not s:
        raise ValueError("Empty plantri string.")

    # Detect alphabetical vs numeric by presence of letters
    alphabetical = any(ch.isalpha() for ch in s)

    # Extract adjacency strings per vertex
    if alphabetical:
        # e.g. "5 bcde,aedc,abd,acbe,adb" → ["bcde","aedc","abd","acbe","adb"]
        # We ignore a leading count if present; we only collect pure alpha runs.
        adj_lists = re.findall(r"\b[a-zA-Z]+\b", s)
    else:
        # Numeric form: find each [...] group and pull its integers
        groups = re.findall(r"\[([^\]]*)\]", s)
        ints_per_group = [re.findall(r"\d+", grp) for grp in groups]
        if len(ints_per_group) >= len(ascii_letters):
            raise ValueError(f"Plantri notation only up to {len(ascii_letters)} vertices is supported.")
        # Map 1->'a', 2->'b', ...
        adj_lists = ["".join(ascii_letters[int(i) - 1] for i in ints) for ints in ints_per_group]

    if not adj_lists:
        raise ValueError("Could not parse plantri adjacency lists.")

    # Build dict: vertex -> neighbors (CW in input → reverse to CCW)
    if len(adj_lists) > len(ascii_letters):
        raise ValueError(f"Too many vertices: {len(adj_lists)} > {len(ascii_letters)}.")
    vertices = ascii_letters[: len(adj_lists)]
    connections = {v: neigh[::-1] for v, neigh in zip(vertices, adj_lists)}

    d = PlanarDiagram()
    d.add_vertices_from(connections.keys())

    # Add arcs (supporting parallel edges by using occurrence indices)
    for v, neighs in connections.items():
        for pos, u in enumerate(neighs):
            # How many times have we seen 'u' before at this vertex?
            occ = neighs[:pos].count(u)
            # Pick the matching position on neighbor 'u' where it points back to 'v',
            # counting from the end because we reversed for CCW.
            u_pos = [i for i, ch in enumerate(connections[u]) if ch == v][-(occ + 1)]
            d.set_arc(((v, pos), (u, u_pos)))

    return d


if __name__ == "__main__":
    pass
