# knotpy/notation/dispatcher.py

from __future__ import annotations

"""Dispatch helpers for KnotPy notations.

These functions return the appropriate converter callable based on a
user-provided notation keyword (case-insensitive, punctuation ignored).

Supported aliases (examples):
- EM / condensed EM: "em", "ewingmillett", "cem", "emc", "condensedem"
- PD: "pd", "planardiagram", "planar"
- Plantri: "plantri", "planarcode", "pl"
- Native: "knotpy", "native"
"""

import string
from typing import Callable, Any, Dict

from knotpy.notation.em import (
    to_em_notation,
    from_em_notation,
    to_condensed_em_notation,
    from_condensed_em_notation,
)
from knotpy.notation.pd import (
    to_pd_notation,
    from_pd_notation,
    to_condensed_pd_notation,
    from_condensed_pd_notation,
)
from knotpy.notation.plantri import to_plantri_notation, from_plantri_notation
from knotpy.notation.native import to_knotpy_notation, from_knotpy_notation

__all__ = ["to_notation_dispatcher", "from_notation_dispatcher"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovšek@pef.uni-lj.si>"


def _normalize_notation(s: str) -> str:
    """Normalize a notation keyword to lowercase letters only.

    Args:
        s: Input notation string.

    Returns:
        str: Lowercased string with only a–z retained.

    Raises:
        TypeError: If `s` is not a string.
    """
    if not isinstance(s, str):
        raise TypeError(f"The argument notation={s!r} should be a string")
    return "".join(c for c in s.lower() if c in string.ascii_lowercase)


_TO_DISPATCH: Dict[str, Callable[..., Any]] = {
    # EM
    "em": to_em_notation,
    "ewingmillett": to_em_notation,
    "ewing": to_em_notation,
    "millett": to_em_notation,
    # condensed EM
    "cem": to_condensed_em_notation,
    "emc": to_condensed_em_notation,
    "ewingmillettcondensed": to_condensed_em_notation,
    "condensedewingmillett": to_condensed_em_notation,
    "condensedem": to_condensed_em_notation,
    "emcondensed": to_condensed_em_notation,
    # PD
    "pd": to_pd_notation,
    "planardiagram": to_pd_notation,
    "planar": to_pd_notation,
    # Plantri
    "plantri": to_plantri_notation,
    "planarcode": to_plantri_notation,
    "pl": to_plantri_notation,
    # Native
    "knotpy": to_knotpy_notation,
    "native": to_knotpy_notation,
}

_FROM_DISPATCH: Dict[str, Callable[..., Any]] = {
    # EM
    "em": from_em_notation,
    "ewingmillett": from_em_notation,
    "ewing": from_em_notation,
    "millett": from_em_notation,
    # condensed EM
    "cem": from_condensed_em_notation,
    "emc": from_condensed_em_notation,
    "ewingmillettcondensed": from_condensed_em_notation,
    "condensedewingmillett": from_condensed_em_notation,
    "condensedem": from_condensed_em_notation,
    "emcondensed": from_condensed_em_notation,
    # PD
    "pd": from_pd_notation,
    "planardiagram": from_pd_notation,
    "planar": from_pd_notation,
    # Plantri
    "plantri": from_plantri_notation,
    "planarcode": from_plantri_notation,
    "pl": from_plantri_notation,
    # Native
    "knotpy": from_knotpy_notation,
    "native": from_knotpy_notation,
}


def to_notation_dispatcher(notation: str) -> Callable[..., Any]:
    """Return the “to-notation” converter function for a given keyword.

    Args:
        notation: Notation keyword (e.g., "pd", "plantri", "em", "cem", "native").

    Returns:
        Callable[..., Any]: Function that converts a diagram to the requested notation.

    Raises:
        ValueError: If the notation keyword is unsupported.
        TypeError: If `notation` is not a string.

    Examples:
        >>> fn = to_notation_dispatcher("PD")
        >>> callable(fn)
        True
    """
    key = _normalize_notation(notation)
    try:
        return _TO_DISPATCH[key]
    except KeyError:
        raise ValueError(f"Unknown notation '{notation}'.") from None


def from_notation_dispatcher(notation: str) -> Callable[..., Any]:
    """Return the “from-notation” parser function for a given keyword.

    Args:
        notation: Notation keyword (e.g., "pd", "plantri", "em", "cem", "native").

    Returns:
        Callable[..., Any]: Function that parses the notation into a diagram.

    Raises:
        ValueError: If the notation keyword is unsupported.
        TypeError: If `notation` is not a string.

    Examples:
        >>> fn = from_notation_dispatcher("cem")
        >>> callable(fn)
        True
    """
    key = _normalize_notation(notation)
    try:
        return _FROM_DISPATCH[key]
    except KeyError:
        raise ValueError(f"Unsupported notation format '{notation}'.") from None


if __name__ == "__main__":
    pass
