import string

from knotpy.notation.em import to_em_notation, from_em_notation, to_condensed_em_notation, from_condensed_em_notation
from knotpy.notation.pd import to_pd_notation, from_pd_notation
from knotpy.notation.plantri import to_plantri_notation, from_plantri_notation
from knotpy.notation.native import to_knotpy_notation, from_knotpy_notation

__all__ = ['to_notation_dispatcher', 'from_notation_dispatcher']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

_notation_aliases = {
        "em": ["em", "ewingmillett", "ewing", "millett"],
        "emc": ["emc", "ewingmillettcondensed", "condensedewingmillett", "cem", "condensedem", "emcondensed"],
        "pd": ["pd", "planardiagram", "planar"],
        "plantri": ["plantri", "planarcode", "pl"],
        "knotpy": ["native", ],
    }

_reversed_notation_aliases = {val: key for key in _notation_aliases for val in _notation_aliases[key]}


def to_notation_dispatcher(notation: str):
    if not isinstance(notation, str):
        raise TypeError(f"The argument notation={notation} should be a string")

    notation = "".join(c for c in notation.lower() if c in string.ascii_lowercase)
    if notation not in _reversed_notation_aliases:
        raise ValueError(f"Unknown notation '{notation}'.")
    return {
        "em": to_em_notation,
        "emc": to_condensed_em_notation,
        "pd": to_pd_notation,
        "plantri": to_plantri_notation,
        "knotpy": to_knotpy_notation,
    }[_reversed_notation_aliases[notation]]


def from_notation_dispatcher(notation: str):
    if not isinstance(notation, str):
        raise TypeError("The argument notation={notation} should be a string")

    notation = "".join(c for c in notation.lower() if c in string.ascii_lowercase)
    if notation not in _reversed_notation_aliases:
        raise ValueError(f"Unknown notation '{notation}'.")
    return {
        "em": from_em_notation,
        "emc": from_condensed_em_notation,
        "pd": from_pd_notation,
        "plantri": from_plantri_notation,
        "knotpy": from_knotpy_notation
    }[_reversed_notation_aliases[notation]]



