# knotpy/utils/string_utils.py

"""
String utilities for KnotPy.

Currently includes:
- `abcABC`: convenience alphabet string (a–z + A–Z).
- `multi_replace`: repeated multi-substring replacement.
"""

from __future__ import annotations

import string

__all__ = ["abcABC", "multi_replace"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

abcABC = string.ascii_lowercase + string.ascii_uppercase
# TODO: use string.ascii_letters



def multi_replace(text: str, *replacements: tuple[str, str] | dict[str, str]) -> str:
    """Repeatedly apply multiple substring replacements until no change occurs.

    Replacements can be given as `(old, new)` tuples or `{old: new}` dicts.
    All replacements are applied in sequence per pass, and the process repeats
    until the text stops changing or `max_passes` is reached.

    Note:
        If your replacements create a cycle (e.g., `("A","B")` and `("B","A")`),
        the function would otherwise loop forever. `max_passes` prevents that;
        if reached, the current text is returned.

    Args:
        text: Input string to transform.
        *replacements: One or more `(old, new)` tuples or `{old: new}` dicts.
        max_passes: Safety cap on the number of full replacement passes.

    Returns:
        The transformed string.

    Examples:
        >>> multi_replace("AAAABC", ("AA", "a"), {"B": "b"}, ("C", "c"))
        'aabc'  # first pass: AAAABC -> aAABC -> aaABC -> aabC -> aab c
                # second pass: aabc (no change) -> stop

        >>> multi_replace("foo-bar", ("foo", "bar"), ("bar", "baz"))
        'bar-baz'
    """
    if not replacements:
        return text

    # Normalize input into a list of (old, new) tuples for fast iteration
    normalized = []
    for r in replacements:
        if isinstance(r, dict):
            normalized.extend(r.items())
        else:
            old, new = r
            normalized.append((old, new))

    while True:
        before = text
        for old, new in normalized:
            if old:
                text = text.replace(old, new)
        if text == before:
            break

    return text


if __name__ == "__main__":
    pass
