# knotpy/algorithms/naming.py
"""
Utilities for generating unique node names for planar diagrams.

If a diagram uses alphabetic node names (a–z, A–Z, aa, ab, ...),
the next names follow that alphabetic sequence. If the diagram uses
integer node names, the next names are the next integers.
"""

__all__ = ["unique_new_node_name", "multiple_unique_new_node_names", "generate_node_names"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

import string
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram

_BASE = len(string.ascii_letters)
_REVERSE = {ch: i for i, ch in enumerate(string.ascii_letters)}


def generate_node_names(number_of_nodes: int) -> list[str]:
    """Generate `number_of_nodes` alphabetic node names (a, b, ..., Z, aa, ab, ...)."""
    if number_of_nodes < 0:
        raise ValueError("number_of_nodes must be non-negative.")
    return [number_to_alpha(i) for i in range(number_of_nodes)]


def _is_alpha(s) -> bool:
    """Return True iff `s` is an ASCII alphabetic string."""
    return isinstance(s, str) and s.isascii() and s.isalpha()


def _alpha_to_number(s: str) -> int:
    """Convert an ASCII alphabetic string to its sequence number (a=0, b=1, ..., Z=51, aa=52, ...)."""
    if not _is_alpha(s):
        raise ValueError(f"Invalid alphabetic name: {s!r}")

    idx = 0
    for ch in s:
        idx = idx * _BASE + _REVERSE[ch]

    offset = sum(_BASE**i for i in range(1, len(s))) if len(s) > 1 else 0
    return idx + offset


def number_to_alpha(n: int) -> str:
    """Convert an integer to its alphabetic name (0 -> 'a', 51 -> 'Z', 52 -> 'aa', ...)."""
    if n < 0:
        raise ValueError("n must be non-negative.")

    length = 1
    total = _BASE
    remaining = n
    while remaining >= total:
        remaining -= total
        length += 1
        total = _BASE**length

    chars: list[str] = []
    for _ in range(length):
        remaining, rem = divmod(remaining, _BASE)
        chars.append(string.ascii_letters[rem])
    return "".join(reversed(chars))


def unique_new_node_name(k: PlanarDiagram | OrientedPlanarDiagram) -> str | int:
    """Return the next available node name for the diagram."""
    nodes = getattr(k, "nodes", [])
    if not nodes:
        return number_to_alpha(0)

    if all(isinstance(node, int) for node in nodes):
        return max(nodes) + 1

    alpha_nodes = [node for node in nodes if _is_alpha(node)]
    if not alpha_nodes:
        return number_to_alpha(0)

    max_num = max(_alpha_to_number(node) for node in alpha_nodes)
    return number_to_alpha(max_num + 1)


def multiple_unique_new_node_names(k: PlanarDiagram | OrientedPlanarDiagram, count: int) -> list[str] | list[int]:
    """Return `count` fresh node names for the diagram."""
    if count < 0:
        raise ValueError("count must be non-negative.")

    nodes = getattr(k, "nodes", [])
    if not nodes:
        return [number_to_alpha(i) for i in range(count)]

    if all(isinstance(node, int) for node in nodes):
        start = max(nodes) + 1
        return [start + i for i in range(count)]

    alpha_nodes = [node for node in nodes if _is_alpha(node)]
    if not alpha_nodes:
        return [number_to_alpha(i) for i in range(count)]

    start_num = max(_alpha_to_number(node) for node in alpha_nodes) + 1
    return [number_to_alpha(start_num + i) for i in range(count)]


if __name__ == "__main__":
    pass