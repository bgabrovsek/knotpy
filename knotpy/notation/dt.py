# knotpy/notation/dt.py

from __future__ import annotations

"""Dowker–Thistlethwaite (DT) notation utilities."""

from typing import Iterable, Sequence, Tuple, List, Dict, Any

__all__ = ["from_dt_notation", "to_dt_notation"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovšek@pef.uni-lj.si>"


def _flatten_nested_list(nested):
    """
    Recursively flatten a list of arbitrary depth into a flat list (generator).
    """
    for item in nested:
        if isinstance(item, list):
            yield from _flatten_nested_list(item)
        else:
            yield item


def flatten_nested_list(nested):
    """
    Recursively flatten a list of arbitrary depth into a flat list.
    Example:
        [1, [2, [3, 4], 5], 6] -> [1, 2, 3, 4, 5, 6]
    """
    return list(_flatten_nested_list(nested))

def from_dt_notation(
    notation: str | Iterable[int] | Iterable[Iterable[int]],
    oriented: bool = False,
):
    """Parse DT notation (knot or link) and return a diagram.

    This currently **parses and validates** the input but does not finish the
    DT→diagram construction (the original code also stopped mid-way). For now,
    non-empty inputs raise a clear ``NotImplementedError`` instead of silently
    printing and returning ``None``.

    Accepts:
      - A string with rows separated by commas/semicolons/spaces (e.g. ``"4 -6 2"`` or ``"4 -6 2 ; 8 -10 12"``)
      - A list of ints (knot) → will be wrapped as a single-component link
      - A list of lists of ints (link)

    Args:
        notation: DT notation (string or nested iterables of ints).
        oriented: If ``True``, returns an oriented diagram instance; if ``False``,
            an unoriented one.

    Returns:
        PlanarDiagram | OrientedPlanarDiagram: Empty diagram if input is empty.

    Raises:
        ValueError: If parsing fails.
        NotImplementedError: For non-empty inputs until the constructor is completed.

    Notes:
        - The unfinished part in the original code explored endpoint placement
          options but never built the final diagram. This version preserves
          behavior safely by raising a clear exception.
    """
    # Lazy imports to keep top-level import fast
    from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
    from knotpy.utils.parsing import parse_spaced_rows

    # Parse & normalize input
    try:
        if isinstance(notation, str):
            rows = parse_spaced_rows(notation)  # list[list[int]] or []
        elif isinstance(notation, Iterable):
            # Convert various iterable shapes into list-of-lists
            if not notation:
                rows = []
            else:
                if all(isinstance(v, int) for v in notation):  # type: ignore[arg-type]
                    rows = [list(notation)]  # knot → single component
                else:
                    rows = [list(row) for row in notation]  # type: ignore[assignment]
        else:
            raise ValueError("Unsupported DT input type.")
    except Exception as e:
        raise ValueError(f"Invalid DT notation {notation!r}") from e

    if not rows:
        return OrientedPlanarDiagram() if oriented else PlanarDiagram()

    # Basic validation snapshot (mirrors original intent)
    flat = flatten_nested_list(rows)
    if any(v == 0 for v in flat):
        raise ValueError("DT labels must be nonzero integers.")
    if len({abs(v) for v in flat}) * 2 != 2 * len({abs(v) for v in flat}):
        # no-op logically; left here as a placeholder if you add deeper checks
        pass

    # TODO(implement): complete DT → planar diagram construction.
    raise NotImplementedError(
        "DT→diagram construction is not implemented yet (original code was unfinished). "
        "Parsing/validation succeeded."
    )


def to_dt_notation(k) -> Tuple[Tuple[int, ...], ...] | Tuple[int, ...]:
    """Serialize a knot/link diagram to DT notation.

    For knots, returns a single tuple of signed odd labels. For links, returns a
    tuple of tuples (one per component), following the usual conventions:
    - Label even indices along the traversal at each crossing on the *incoming over* endpoint.
    - The sign of the paired odd label is positive/negative based on the local crossing orientation.

    Args:
        k: Planar or oriented diagram.

    Returns:
        tuple: For a knot, ``(l1, l2, ..., l_{2n})``. For a link, ``((...), (...), ...)``.

    Raises:
        ValueError: If the diagram is not a knot/link in a way compatible with DT.
    """
    # Lazy imports (fast package import, avoid pulling algorithms on import)
    from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
    from knotpy.algorithms.topology import is_link
    from knotpy.algorithms.orientation import orient

    if not is_link(k):
        raise ValueError("DT notation is only defined for knots/links.")

    # Ensure oriented diagram for consistent labeling
    k = orient(k) if not k.is_oriented() else k.copy()

    labels: Dict[int, tuple] = {}  # label -> (crossing, position % 2, component)
    labels_rev: Dict[tuple, int] = {}  # (crossing, position % 2) -> label

    component = -1
    # Assign labels per component until we have 2*#crossings labels
    while len(labels_rev) < k.number_of_crossings * 2:
        component += 1
        # Start at the ingoing-over endpoint of the minimal unused crossing
        crossing = min(k.crossings)  # NOTE: for links, min() across components is OK; we filter by component later
        ep = k.endpoint_from_pair((crossing, "ingoing over"))
        # Walk, labeling even indices, jumping across the over strand each time
        while (ep.node, ep.position % 2) not in labels_rev:
            labels[len(labels) + 1] = (ep.node, ep.position % 2, component)
            labels_rev[(ep.node, ep.position % 2)] = len(labels)
            ep = k.twin((ep.node, (ep.position + 2) % 4))  # jump across the crossing

    # Build DT per component
    per_component: List[List[int]] = [[] for _ in range(component + 1)]
    for comp_idx, notation in enumerate(per_component):
        for even_label in range(1, 2 * k.number_of_crossings, 2):
            cross, pos, which = labels[even_label]
            if which != comp_idx:
                continue
            odd_label = labels_rev[(cross, 1 - pos)]
            notation.append(odd_label * (1 if pos else -1))

    # Return tuple for knot, tuple-of-tuples for links
    return tuple(per_component[0]) if len(per_component) == 1 else tuple(tuple(x) for x in per_component)


if __name__ == "__main__":
    pass
