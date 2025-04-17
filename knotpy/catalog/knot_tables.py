import re

from pathlib import Path
from functools import partial

from knotpy.utils.dict_utils import LazyLoadEvalDict
from knotpy.catalog.invariant_reader import load_invariant_table, _lazy_invariant_dict_eval
from knotpy.notation.native import from_knotpy_notation
from knotpy.catalog.diagram_reader import load_diagrams_as_dict

_DATA_DIR = Path(__file__).parent / "data"

def _lazy_load_invariants(filename):
    return LazyLoadEvalDict(
        load_function=partial(load_invariant_table, filename=_DATA_DIR / filename, lazy=True),
        eval_function=_lazy_invariant_dict_eval
    )

def _lazy_load_diagrams_from_invariants(filename):
    return LazyLoadEvalDict(
        load_function=partial(load_invariant_table, filename=_DATA_DIR / filename, lazy=True, field_name="native notation"),
        eval_function=from_knotpy_notation
    )

def _lazy_load_diagrams(filename):
    return LazyLoadEvalDict(
    load_function=partial(load_diagrams_as_dict, filename=_DATA_DIR / filename, lazy=True),
    eval_function=from_knotpy_notation
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

def _get_link(crossing_number, alternating, index, orientation):

    if crossing_number <= 1:
        raise ValueError(f"Only links with two or more crossings are in the KnotPy database")
    if crossing_number <= 8:
        table = _link_table_8
    elif crossing_number <= 9:
        table = _link_table_9
    elif crossing_number <= 10:
        table = _link_table_10
    elif crossing_number <= 11:
        table = _link_table_11
    else:
        raise ValueError(f"Only links up to 11 crossings are in the KnotPy database")

    if orientation:
        key = f"L{crossing_number}{alternating}{index}{{{';'.join(str(o) for o in orientation)}}}"
        if key in table:
            #print("key", key, "found")
            return table[key]
    else:
        key = f"L{crossing_number}{alternating}{index}"
        if key in table:
            return table[key]
        if key + "{0}" in table:
            return table[key + "{0}"]
        if key + "{0;0}" in table:
            return table[key + "{0;0}"]
        if key + "{0;0,0}" in table:
            return table[key + "{0;0;0}"]
        if key + "{0;0;0;0}" in table:
            return table[key + "{0;0;0;0}"]
        if key + "{0;0;0;0;0}" in table:
            return table[key + "{0;0;0;0;0}"]

    raise ValueError(f"Link {key} not in the database")


def _get_knot(crossing_number, alternating, index):
    if crossing_number <= 10:
        table = _knot_table_10
    elif crossing_number <= 11:
        table = _knot_table_11
    elif crossing_number <= 12:
        table = _knot_table_12
    elif crossing_number <= 13:
        table = _knot_table_13
    else:
        raise ValueError(f"Only knots up to 13 crossings are in the KnotPy database")

    key = f"{crossing_number}{alternating}_{index}" if alternating else f"{crossing_number}_{index}"

    if key in table:
        return table[key]

    raise ValueError(f"Knot {key} not in the database")

def _get_theta(orientation, crossing_number, index, subindex):
    if crossing_number <= 7:
        table = _theta_table_7
    else:
        raise ValueError(f"Only theta curves up to 7 crossings are in the KnotPy database")

    if orientation:
        key = f"{orientation}t{crossing_number}_{index}"
        if key in table:
            return table[key]
    elif subindex:
        key = f"t{crossing_number}_{index}.{subindex}"
        if key in table:
            return table[key]
    else:
        key = f"t{crossing_number}_{index}"
        if key in table:
            return table[key]
        if "+" + key in table:
            return table["+" + key]
        if key + ".1" in table:
            return table[key + ".1"]

    raise ValueError(f"Theta curve {key} not in the database")


def _get_handcuff(crossing_number, index, subindex):
    if crossing_number <= 7:
        table = _theta_table_7
    else:
        raise ValueError(f"Only theta curves up to 7 crossings are in the KnotPy database")
    if subindex:
        key = f"h{crossing_number}_{index}.{subindex}"
        if key in table:
            return table[key]
    else:
        key = f"h{crossing_number}_{index}"
        if key in table:
            return table[key]
        if key + ".1" in table:
            return table[key + ".1"]

    raise ValueError(f"Handcuff link {key} not in the database")


def get_knot_from_name(name):

    name = name.lower().strip().replace(" ", "")

    if name in _knot_naming_synonyms:
        name = _knot_naming_synonyms[name]

    # Is the name a link?
    if "l" in name:
        crossing_number, alternating, index, orientation = _parse_link_name(name)
        #print(crossing_number, alternating, index, orientation)
        return _get_link(crossing_number, alternating, index, orientation).copy()

    # Is the name a theta curve?
    elif "t" in name:
        orientation, crossing_number, index, sub_index = _parse_theta_name(name)
        #print(orientation, crossing_number, index, sub_index)
        return _get_theta(orientation, crossing_number, index, sub_index).copy()

    # Is the name a handcuff link?
    elif "h" in name:
        print("handcuff name", name)
        crossing_number, index, sub_index = _parse_handcuff_name(name)
        #rint(crossing_number, index, sub_index)
        return _get_handcuff(crossing_number, index, sub_index).copy()

    # is the name a knot?
    else:
        crossing_number, alternating, index = _parse_knot_name(name)
        #print(crossing_number, alternating, index)
        return _get_knot(crossing_number, alternating, index).copy()


if __name__ == "__main__":
    pass

    """
    possible names:
    3_1
    11a_214
    11n_214
    L10a124{0;0}
    L10n54{1}
    t5_1.2
    -t5_2

    3_1:

    0_1: unknot
    3_1 Trefoil
    4_1 Figure Eight
    5_1: Cinquefoil , pentafoil
    5_2: 3-twist knot
    6_1: Stevedore's Knot
    6_2: The Miller Institute Knot
    7_1:  Septafoil, cinquefoil
    9_1 Nonafoil
    8_19 Non-alternating
Hopf link
Whitehead link
Borromean rings
unlink

    """



