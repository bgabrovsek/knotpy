"""
Lightweight parsers for KnotPy notations.

Functions here parse tiny, dependency-free fragments such as endpoints (``a12``),
arcs (two endpoints concatenated, e.g. ``a1b5``), comma-separated arc lists,
and simple “rows of integers” strings.

These utilities are intentionally strict and small; they’re used by several
notation modules and should stay fast and import-light.
"""

from __future__ import annotations

from string import ascii_letters
import re
from typing import List, Tuple, Union

__all__ = [
    "parse_endpoint",
    "parse_arc",
    "parse_arcs",
    "parse_spaced_rows",
    "universal_list_of_lists_parser",
]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

# Precompiled regexes for speed and clarity
_ENDPOINT_RE = re.compile(r"^\s*([A-Za-z])\s*(\d+)\s*$")
_CONCAT_ENDPOINTS_RE = re.compile(r"([A-Za-z]\d+)")


def parse_endpoint(endpoint: str) -> Tuple[str, int]:
    """Parse a single endpoint like ``'a9'`` into ``('a', 9)``.

    Accepts exactly one ASCII letter followed by one or more digits.
    Whitespace around the letter and digits is ignored.

    Args:
        endpoint: Endpoint string, e.g. ``'a0'``, ``'Z12'``.

    Returns:
        (letter, index) pair.

    Raises:
        ValueError: If the format is invalid.
    """
    m = _ENDPOINT_RE.match(endpoint)
    if not m:
        raise ValueError(f"Invalid endpoint format: {endpoint!r}")
    letter, number = m.groups()
    if letter not in ascii_letters:
        # Redundant due to regex, but keeps the error message explicit.
        raise ValueError(f"Invalid endpoint letter: {letter!r}")
    return letter, int(number)


def parse_arc(arc: str) -> Tuple[Tuple[str, int], Tuple[str, int]]:
    """Parse a concatenated arc like ``'a1b5'`` → ``(('a', 1), ('b', 5))``.

    The function finds exactly two endpoint tokens (letter+digits). Tokens may
    have surrounding whitespace.

    Args:
        arc: Arc string, e.g. ``'a1b5'`` or ``' a12  b003 '``.

    Returns:
        A pair of parsed endpoints.

    Raises:
        ValueError: If exactly two endpoints are not found or any endpoint is invalid.
    """
    tokens = _CONCAT_ENDPOINTS_RE.findall(arc.strip())
    if len(tokens) != 2:
        raise ValueError(f"Invalid arc format (need exactly 2 endpoints): {arc!r}")
    ep1, ep2 = (parse_endpoint(tok) for tok in tokens)
    return ep1, ep2


def parse_arcs(arcs: str) -> List[Tuple[Tuple[str, int], Tuple[str, int]]]:
    """Parse a comma-separated list of arcs.

    Example:
        ``'a6b6, a9u8'`` → ``[(('a', 6), ('b', 6)), (('a', 9), ('u', 8))]``.

    Args:
        arcs: A string like ``'a1b2, c3d4'`` (commas may be surrounded by spaces).

    Returns:
        List of parsed arcs.

    Raises:
        ValueError: If any individual arc is invalid.
    """
    if not arcs.strip():
        return []
    return [parse_arc(part.strip()) for part in arcs.split(",") if part.strip()]


def universal_list_of_lists_parser(input_str: str) -> List[List[Union[int, str]]]:
    """Best-effort parser for “list of lists” written in a few loose styles.

    This helper is **kept for compatibility** and is intentionally permissive.
    It supports inputs like::

        "[1 2 3], [4 5 6]"
        "(1 2 3) (4 5 6)"
        "1 2 3, 4 5 6"
        "1 2 3; 4 5 -6"

    Items are split by commas/whitespace; integers are converted to ``int``,
    other tokens are kept as ``str``.

    Args:
        input_str: Source text.

    Returns:
        A list of lists with parsed items.

    Notes:
        This is not a general parser. Prefer structured formats where possible.
    """
    s = input_str.strip()
    if not s:
        return []

    # Normalize brackets to square for extraction
    bracketed = any(c in s for c in "[]()")
    if bracketed:
        s = s.replace("(", "[").replace(")", "]")
        groups = re.findall(r"\[([^\[\]]+)\]", s)
        if not groups:
            # Fallback to splitting if brackets present but empty/mismatched
            groups = re.split(r"[;,]", s)
    else:
        groups = re.split(r"[;,]", s)

    result: List[List[Union[int, str]]] = []
    for grp in groups:
        items = re.split(r"[,\s]+", grp.strip())
        items = [it for it in items if it]  # remove empties
        if not items:
            continue
        parsed: List[Union[int, str]] = []
        for it in items:
            try:
                parsed.append(int(it))
            except ValueError:
                parsed.append(it)
        result.append(parsed)

    return result


def parse_spaced_rows(data_str: str) -> Union[List[int], List[List[int]]]:
    """Parse space-separated integers into one row or multiple rows.

    Accepts commas or semicolons as row separators.

    Examples:
        - ``"1 2 3"`` → ``[1, 2, 3]``
        - ``"1 2 3, 4 5 -6"`` → ``[[1, 2, 3], [4, 5, -6]]``
        - ``"1 2 3 ; 4 5 -6"`` → ``[[1, 2, 3], [4, 5, -6]]``

    Args:
        data_str: Input string.

    Returns:
        A single list of ints if one row is given, otherwise list of rows.
    """
    s = data_str.strip()
    if not s:
        return []

    # Normalize row separators to a single token
    s = s.replace(";", "|").replace(",", "|")
    rows = [row.strip() for row in s.split("|") if row.strip()]

    parsed = [[int(num) for num in row.split()] for row in rows]
    return parsed[0] if len(parsed) == 1 else parsed


if __name__ == "__main__":
    pass
