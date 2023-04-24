
from knotpy.notation.em import to_em_notation, from_em_notation
from knotpy.notation.pd import to_pd_notation, from_pd_notation
from knotpy.notation.plantri import to_plantri_notation, from_plantri_notation


__all__ = ['to_notation_dispatcher', 'from_notation_dispatcher']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

_notation_aliases = {
        "em": ["em", "ewing millett", "ewing-millett", "ewing/millett"],
        "pd": ["pd", "planar diagram", "planar-diagram"],
        "plantri": ["plantri", "planar code", "ascii", "pl"]
    }

_reversed_aliases = {val: key for key in _notation_aliases for val in _notation_aliases[key]}


def to_notation_dispatcher(notation):
    assert isinstance(notation, str), "Parameter notation should be a string."
    notation = notation.lower()
    if notation not in _reversed_aliases:
        raise ValueError(f"Unknown notation '{notation}'.")

    return {
        "em": to_em_notation,
        "pd": to_pd_notation,
        "plantri": to_plantri_notation,
    }[_reversed_aliases[notation]]


def from_notation_dispatcher(notation):
    assert isinstance(notation, str), "Parameter notation should be a string."
    notation = notation.lower()
    if notation not in _reversed_aliases:
        raise ValueError(f"Unknown notation '{notation}'.")

    return {
        "em": from_em_notation,
        "pd": from_pd_notation,
        "plantri": from_plantri_notation,
    }[_reversed_aliases[notation]]



