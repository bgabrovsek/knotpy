#from knotpy.utils import iterable_depth

import knotpy as kp

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
        "em": kp.notation.to_em_notation,
        "pd": kp.notation.to_pd_notation,
        "plantri": kp.notation.to_plantri_notation,
    }[_reversed_aliases[notation]]


def from_notation_dispatcher(notation):
    assert isinstance(notation, str), "Parameter notation should be a string."
    notation = notation.lower()
    if notation not in _reversed_aliases:
        raise ValueError(f"Unknown notation '{notation}'.")

    return {
        "em": kp.notation.from_em_notation,
        "pd": kp.notation.from_pd_notation,
        "plantri": kp.notation.from_plantri_notation,
    }[_reversed_aliases[notation]]



