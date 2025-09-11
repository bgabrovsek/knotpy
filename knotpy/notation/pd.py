# knotpy/notation/pd.py

from __future__ import annotations

"""Planar Diagram (PD) notation utilities.

PD notation describes knotted structures as incidence lists.
Reference: https://katlas.org/wiki/Planar_Diagrams

Supported input styles (auto-detected):
  - Mathematica:  "Xp[1,9,2,8],Xn[3,10,4,11],X[5,3,6,2],..."
  - KnotInfo:     "[[1,5,2,4],[3,1,4,6],[5,3,6,2]]"
  - Topoly:       "V[3,23];X[1,0,3,2];X[0,9,14,13];..."
"""

from ast import literal_eval
from collections import defaultdict
from typing import Any

from knotpy.classes.planardiagram import OrientedPlanarDiagram, PlanarDiagram
from knotpy.classes.node import Crossing, Vertex
from knotpy.utils.string_utils import abcABC, multi_replace

__all__ = ["from_pd_notation", "to_pd_notation", "to_condensed_pd_notation", "from_condensed_pd_notation"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovšek@pef.uni-lj.si>"


_node_abbreviations = {
    "X": Crossing,
    "V": Vertex,
}

_node_abbreviations_inv = {val: key for key, val in _node_abbreviations.items()}


def from_pd_notation(text: str | list | tuple, node_type: type | Any = str, oriented: bool = False, **attr: Any) -> PlanarDiagram:
    """Create a planar diagram from PD notation.

    Supports Mathematica, KnotInfo, and Topoly variants. Nodes default to ``'a','b','c',...``
    if ``node_type is str``; otherwise integers are used in order of appearance.

    Args:
        text: PD notation string (mixed styles allowed; auto-detected).
        node_type: Use ``str`` for ``a,b,c,...`` labels (default), or a different marker to keep integers.
        oriented: Whether to create an oriented diagram (not implemented yet).
        **attr: Diagram attributes to set (e.g., name, framing).

    Returns:
        PlanarDiagram: Parsed diagram.

    Raises:
        NotImplementedError: If ``oriented=True`` (placeholder).
        ValueError: If the PD string is malformed or arcs are not paired.

    Examples:
        >>> s = "V[1,2,3], X[2,3,4,5]"
        >>> d = from_pd_notation(s)
        >>> isinstance(d, PlanarDiagram)
        True
    """
    if not isinstance(text, str):
        text = str(text)

    # if oriented:
    #     raise NotImplementedError("Oriented PD import not implemented yet.")

    s = text.strip()
    # normalize separators/spacing across styles (relies on multi_replace helper)
    s = multi_replace(s, ")]", "([", {"] ": "]", ", ": ","}, ";,", ("],", "];"))
    s = s.upper()
    s = " ".join(s.split())
    s = s.replace("PD ", "PD")

    if s.startswith("PD[") and s.endswith("]"):
        s = s[3:-1]

    # Extract nested list if wrapped like [[...]] or ( ... )
    if s[:2] in ("[[", "[(", "([", "((") and s[-2:] in ("]]", "])", ")]", "))"):
        s = s[1:-1]

    # For now disable oriented, keep API-compatible variable present
    oriented = False

    k: PlanarDiagram = OrientedPlanarDiagram() if oriented else PlanarDiagram()
    arc_dict: dict[int, list[tuple[Any, int]]] = defaultdict(list)

    for node_idx, subtext in enumerate(s.split(";")):
        i0, i1 = subtext.find("["), subtext.find("]")
        if i0 == -1 or i1 == -1:
            raise ValueError(f"Invalid PD node notation: {subtext!r}")

        # Safer than eval
        node_arcs = literal_eval(subtext[i0 : i1 + 1])
        if not isinstance(node_arcs, (list, tuple)):
            raise ValueError(f"PD node arcs must be a list/tuple: {subtext!r}")

        # Node abbreviation (X/V) inferred if missing by degree
        node_abbr = subtext[:i0] if 1 <= i0 <= 2 else ("X" if len(node_arcs) == 4 else "V")
        node_name = abcABC[node_idx] if node_type is str else node_idx

        try:
            k.add_node(node_for_adding=node_name, create_using=_node_abbreviations[node_abbr], degree=len(node_arcs))
        except KeyError:
            raise ValueError(
                f"Invalid PD node abbreviation {node_abbr!r} at item {node_idx} in PD string."
            ) from None

        for pos, arc in enumerate(node_arcs):
            if not isinstance(arc, int):
                raise ValueError(f"Arc labels must be integers; got {arc!r} in {subtext!r}.")
            arc_dict[arc].append((node_name, pos))

    # Every arc id must occur exactly twice
    for arc_id, pair in arc_dict.items():
        if len(pair) != 2:
            raise ValueError(f"Invalid PD: arc id {arc_id} occurs {len(pair)} times (expected 2).")
        k.set_arc(tuple(pair))  # type: ignore[arg-type]

    k.attr.update(attr)
    return k


def from_condensed_pd_notation(text: str, node_type: type | Any = str, oriented: bool = False, **attr: Any) -> PlanarDiagram:
    """Create a planar diagram from condensed PD code (e.g., ``"abc bcde ..."``).

    Each token is a node’s incident arcs in CCW order; 4 letters → ``X`` (crossing),
    otherwise ``V`` (vertex). Arc labels must be single characters and paired globally.

    Args:
        text: Condensed PD code as space-separated tokens.
        node_type: Use ``str`` for ``a,b,c,...`` labels (default), else integers.
        oriented: Whether to create an oriented diagram (not implemented yet).
        **attr: Diagram attributes to set.

    Returns:
        PlanarDiagram: Parsed diagram.

    Raises:
        NotImplementedError: If ``oriented=True`` (placeholder).
        ValueError: If token parsing fails.
    """
    if oriented:
        raise NotImplementedError("Oriented condensed PD import not implemented yet.")

    s = text.strip()
    if not s:
        raise ValueError("Empty condensed PD string.")

    k = PlanarDiagram()
    arc_dict: dict[str, list[tuple[Any, int]]] = defaultdict(list)

    for node_idx, token in enumerate(s.split()):
        node_arcs = list(token)
        node_abbr = "X" if len(node_arcs) == 4 else "V"
        node_name = abcABC[node_idx] if node_type is str else node_idx

        k.add_node(node_for_adding=node_name, create_using=_node_abbreviations[node_abbr], degree=len(node_arcs))

        for pos, arc in enumerate(node_arcs):
            arc_dict[arc].append((node_name, pos))

    for pair in arc_dict.values():
        if len(pair) != 2:
            raise ValueError("Invalid condensed PD: every arc must appear exactly twice.")
        k.set_arc(tuple(pair))  # type: ignore[arg-type]

    k.attr.update(attr)
    return k


def to_pd_notation(k: PlanarDiagram) -> str:
    """Serialize a planar diagram to PD notation.

    Output uses abbreviations inferred by node type:
    ``X[...,...,...,...]`` for crossings and ``V[...]`` for vertices. Arc ids are
    assigned by enumerating unique arcs as they appear.

    Args:
        k: Diagram to serialize.

    Returns:
        str: PD notation string.

    Examples:
        >>> from knotpy.classes.planardiagram import PlanarDiagram
        >>> d = PlanarDiagram()
        >>> d.add_vertices_from(["a","b"])
        >>> d.set_arc((("a",0),("b",0)))
        >>> out = to_pd_notation(d)
        >>> out.startswith("V[") or out.startswith("X[")
        True
    """
    # Map endpoints to arc numbers (0..m-1)
    endpoint_to_arc: dict[Any, int] = {}
    for arc_number, (ep0, ep1) in enumerate(k.arcs):
        endpoint_to_arc[ep0] = arc_number
        endpoint_to_arc[ep1] = arc_number

    parts: list[str] = []
    for node in k.nodes:
        node_type_abbr = _node_abbreviations_inv[type(k.nodes[node])]
        plist = ",".join(str(endpoint_to_arc[ep]) for ep in k.nodes[node])
        parts.append(f"{node_type_abbr}[{plist}]")

    return ",".join(parts)


def to_condensed_pd_notation(k: PlanarDiagram) -> str:
    """Serialize a planar diagram to condensed PD notation.

    Constraints:
      - At most 50 arcs (since we label arcs with single letters).
      - Diagram must contain only vertices and crossings.
      - No vertex may have degree 4 (ambiguity with crossings).

    Args:
        k: Diagram to serialize.

    Returns:
        str: Space-separated tokens of arc letters per node (CCW).

    Raises:
        ValueError: If constraints are violated.
    """
    arcs_list = list(k.arcs)
    if len(arcs_list) > 50:
        raise ValueError("Too many arcs for condensed PD notation (max 50).")

    if len(k.vertices) + len(k.crossings) != len(k.nodes):
        raise ValueError("Condensed PD requires only vertices and crossings.")

    if any(k.degree(node) == 4 for node in k.vertices):
        raise ValueError("Condensed PD requires that no vertex has degree 4.")

    # Assign letters to arcs
    endpoint_to_letter: dict[Any, str] = {}
    for idx, (ep0, ep1) in enumerate(arcs_list):
        endpoint_to_letter[ep0] = abcABC[idx]
        endpoint_to_letter[ep1] = abcABC[idx]

    return " ".join("".join(endpoint_to_letter[ep] for ep in k.nodes[node]) for node in k.nodes)


if __name__ == "__main__":
    pass
