import re
from pathlib import Path
from functools import partial

from knotpy.utils.dict_utils import LazyLoadEvalDict, JointDict
from knotpy.catalog.invariant_reader import load_invariant_table, _lazy_invariant_dict_eval
from knotpy.notation.native import from_knotpy_notation
from knotpy.catalog.diagram_reader import load_diagrams_as_dict
from knotpy.classes.freezing import freeze

_DATA_DIR = Path(__file__).parent / "data"
_KNOT_TABLE_STARTS_WITH = 10
_LINK_TABLE_STARTS_WITH = 8
_MIN_KNOT_CROSSINGS = 0
_MAX_KNOT_CROSSINGS = 13
_MIN_LINK_CROSSINGS = 2
_MAX_LINK_CROSSINGS = 11
_MIN_THETA_CROSSINGS = 0
_MAX_THETA_CROSSINGS = 7
_MIN_HANDCUFF_CROSSINGS = 0
_MAX_HANDCUFF_CROSSINGS = 7

# TODO: make oriented/non-oriented link tables (maybe make a "variations" function?)

def _lazy_load_invariants(filename):
    return LazyLoadEvalDict(
        load_function=partial(load_invariant_table, filename=_DATA_DIR / filename, lazy=True),
        eval_function=_lazy_invariant_dict_eval
    )

def _lazy_load_diagrams_from_invariants(filename):
    return LazyLoadEvalDict(
        load_function=partial(load_invariant_table, filename=_DATA_DIR / filename, lazy=True, field_name="native notation"),
        eval_function=lambda _: freeze(from_knotpy_notation(_))
    )

def _lazy_load_diagrams(filename):
    return LazyLoadEvalDict(
    load_function=partial(load_diagrams_as_dict, filename=_DATA_DIR / filename, lazy=True),
    eval_function=lambda _: freeze(from_knotpy_notation(_))
    )

# TODO: fix/unite orientation, mirrors,...
# TODO: when we get a knot from the table, we should return a copy, not the knot, since someone can modify it.

# Load knot tables with invariants.
_knot_invariants_10 = _lazy_load_invariants("knot_invariants_up_to_10_crossings.csv.gz")
_knot_invariants_11 = _lazy_load_invariants("knot_invariants_11_crossings.csv.gz")
_knot_invariants_12 = _lazy_load_invariants("knot_invariants_12_crossings.csv.gz")
_knot_invariants_13 = _lazy_load_invariants("knot_invariants_13_crossings.csv.gz")

# Load link tables with invariants.
_link_invariants_8 = _lazy_load_invariants("link_invariants_up_to_8_crossings.csv.gz")
_link_invariants_9 = _lazy_load_invariants("link_invariants_9_crossings.csv.gz")
_link_invariants_10 = _lazy_load_invariants("link_invariants_10_crossings.csv.gz")
_link_invariants_11 = _lazy_load_invariants("link_invariants_11_crossings.csv.gz")

# TODO: speed up by reading knots from a file containing only knows

# Load knot tables (without invariants).
_knot_table_10 = _lazy_load_diagrams_from_invariants("knot_invariants_up_to_10_crossings.csv.gz")
_knot_table_11 = _lazy_load_diagrams_from_invariants("knot_invariants_11_crossings.csv.gz")
_knot_table_12 = _lazy_load_diagrams_from_invariants("knot_invariants_12_crossings.csv.gz")
_knot_table_13 = _lazy_load_diagrams_from_invariants("knot_invariants_13_crossings.csv.gz")

# Load link tables (without invariants)
_link_table_8 = _lazy_load_diagrams_from_invariants("link_invariants_up_to_8_crossings.csv.gz")
_link_table_9 = _lazy_load_diagrams_from_invariants("link_invariants_9_crossings.csv.gz")
_link_table_10 = _lazy_load_diagrams_from_invariants("link_invariants_10_crossings.csv.gz")
_link_table_11 = _lazy_load_diagrams_from_invariants("link_invariants_11_crossings.csv.gz")

# Load theta-curve and handcuff link table (without invariants)
_theta_table_7 = _lazy_load_diagrams("theta-handcuffs-7-crossings.csv.gz")

#
# for x in _theta_table_7:
#     print(x, _theta_table_7[x])
#     break
#
# for x in _knot_table_13:
#     print(x, _knot_table_13[x])
#     break

_knot_naming_synonyms = {
    "unknot": "0_1",
    "trefoil": "3_1",
    "figureeight": "4_1",
    "pentafoil": "5_1",
    "3-twistknot": "5_2", "3-twist": "5_2", "3twistknot": "5_2", "3twist": "5_2",
    "stevedore's knot": "6_1", "stevedores": "6_1", "stevedore's": "6_1",
    "themillerinstituteknot": "6_2", "millerinstituteknot": "6_2", "miller institute": "6_2",
    "septafoil": "7_1",
    "cinquefoil": "7_1",
    "nonafoil": "9_1",
    "nonalternating": "8_19",
    "hopf": "l2a1", "hopflink":"l2a1",
    "solomon'sknot": "l4a1", "guillocheknot": "l4a1", "guilloche": "l4a1", "solomons": "l4a1", "solomon's": "l4a1",
    "whitehead": "l5a1", "whiteheadlink": "l5a1",
    "borromeanrings": "l6a4", "borromeanlink": "l6a4", "borromean": "l6a4",
}



def _parse_link_name(name):
    # Parse the link: Match L<number><a|n><number>{optional list}.
    match = re.match(r"l(\d+)([an])(\d+)(?:\{([\d;]*)\})?", name, re.IGNORECASE)
    if not match:
        raise ValueError(f"Link name {name} not recognized")

    crossing_number = int(match.group(1))
    alternating = match.group(2)
    index = int(match.group(3))
    orientation_str = match.group(4)
    orientation = tuple(map(int, orientation_str.split(";"))) if orientation_str else ()

    return crossing_number, alternating, index, orientation


def _parse_theta_name(name):
    # Match optional sign, then t<number>_<index>[.subindex]
    match = re.match(r"^([+-])?t(\d+)_(\d+)(?:\.(\d+))?$", name)
    if not match:
        raise ValueError(f"Theta-curve name {name} not recognized")
    orientation = match.group(1)  # '+' or '-' or None
    crossing_number = int(match.group(2))
    index = int(match.group(3))
    subindex = int(match.group(4)) if match.group(4) else None
    return orientation, crossing_number, index, subindex


def _parse_handcuff_name(name):
    match = re.match(r"^h(\d+)_(\d+)(?:\.(\d+))?$", name)
    if not match:
        raise ValueError(f"Handcuff name {name} not recognized")
    crossing_number = int(match.group(1))
    index = int(match.group(2))
    subindex = int(match.group(3)) if match.group(3) else None
    return crossing_number, index, subindex


def _parse_knot_name(s):
    match = re.match(r"^(\d+)([an])?_(\d+)$", s)
    if not match:
        raise ValueError(f"Knot name {s} not recognized")
    crossing_number = int(match.group(1))
    alternating = match.group(2)  # 'a', 'n', or None
    index = int(match.group(3))
    return crossing_number, alternating, index


# a joint dictionary, keys are knot names ("3_1",...), values are invariant dictionaries
_knot_invariants = JointDict(
    dict_map={10:_knot_invariants_10, 11:_knot_invariants_11, 12:_knot_invariants_12, 13:_knot_invariants_13},
    key_map=lambda s: max(_parse_knot_name(s)[0], 10)
)

# a joint dictionary, keys are link names (...), values are invariant dictionaries
_link_invariants = JointDict(
    dict_map={8:_link_invariants_8, 9:_link_invariants_9, 10:_link_invariants_10, 11:_link_invariants_11},
    key_map=lambda s: max(_parse_link_name(s)[0], 8)
)

# a joint dictionary, keys are knot names ("3_1",...), values are planar diagrams
_knot_table = JointDict(
    dict_map={10:_knot_table_10, 11:_knot_table_11, 12:_knot_table_12, 13:_knot_table_13},
    key_map=lambda s: max(_parse_knot_name(s)[0], 10)
)

# a joint dictionary, keys are link names, values are planar diagrams
_link_table = JointDict(
    dict_map={8:_link_table_8, 9:_link_table_9, 10:_link_table_10, 11:_link_table_11},
    key_map=lambda s: max(_parse_link_name(s)[0], 8)
)
