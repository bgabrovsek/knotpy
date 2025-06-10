
from knotpy.catalog._knot_database import _knot_naming_synonyms, _knot_table, _link_table, _theta_table_7, _parse_knot_name, _knot_invariants, _parse_link_name
from knotpy.catalog._knot_database import (_MIN_KNOT_CROSSINGS, _MAX_KNOT_CROSSINGS, _MIN_LINK_CROSSINGS,
                                           _MAX_LINK_CROSSINGS, _MIN_THETA_CROSSINGS, _MAX_THETA_CROSSINGS,
                                           _MIN_HANDCUFF_CROSSINGS, _MAX_HANDCUFF_CROSSINGS, _KNOT_TABLE_STARTS_WITH,
                                           _LINK_TABLE_STARTS_WITH)


def _clean_name(name:str):
    """ Return a cleaned name, e.g. '4_1 ' -> '4_1' """
    name = name.lower().strip().replace(" ", "")
    return _knot_naming_synonyms[name] if name in _knot_naming_synonyms else name

"""
Get knots/links/thetas/handcuffs from their name.
"""

def knot(name: str):
    """ Return a knot diagram from its name, e.g. '4_1' """
    name = _clean_name(name)
    if name not in _knot_table:
        raise ValueError(f"Knot {name} not in KnotPy database")
    return _knot_table[name].copy()


def link(name: str):
    """ Return a link diagram from its name, e.g. 'l2a1' """
    name = _clean_name(name)
    if name in _link_table:
        return _link_table[name].copy()

    for suffix in ["{0}", "{0;0}", "{0;0;0}","{0;0;0;0}","{0;0;0;0;0}","{0;0;0;0;0;0}","{0;0;0;0;0;0;0}"]:
        if name + suffix in _link_table:
            return _link_table[name+suffix].copy()

    raise ValueError(f"Link {name} not in KnotPy database")



def theta(name: str):
    """ Return a theta curve from its name, e.g. 't5_1.2' """
    name = _clean_name(name)
    if name in _theta_table_7:
        return _theta_table_7[name].copy()

    for prefix in ["+", "-"]:
        if prefix + name in _theta_table_7:
            return _theta_table_7[prefix + name].copy()

    for suffix in [".1", ".2"]:
        if name + suffix in _theta_table_7:
            return _theta_table_7[name + suffix].copy()

    raise ValueError(f"Theta curve {name} not in KnotPy database")


def handcuff(name:str):
    """ Return a handcuff link from its name, e.g. 'h5_1.2' """
    name = _clean_name(name)
    if name in _theta_table_7:
        return _theta_table_7[name].copy()

    for prefix in ["+", "-"]:
        if prefix + name in _theta_table_7:
            return _theta_table_7[prefix + name].copy()

    for suffix in [".1", ".2"]:
        if name + suffix in _theta_table_7:
            return _theta_table_7[name + suffix].copy()

    raise ValueError(f"Handcuff link {name} not in KnotPy database")


def diagram_from_name(name):
    """Return any diagram (knot, link, theta curve, handcuff link,...) from its name."""
    name = _clean_name(name)
    # Is the name a link?
    if "l" in name:
        return knot(name)
    # Is the name a theta curve?
    elif "t" in name:
        return theta(name)
    # Is the name a handcuff link?
    elif "h" in name:
        return handcuff(name)
    # is the name a knot?
    else:
        return knot(name)


def _range_from_value(value: int | tuple[int, int] | list[int, int]  | None, default_min, default_max):
    if isinstance(value, int):
        return value, value
    elif isinstance(value, (tuple, list)):
        return value
    elif value is None:
        return default_min, default_max
    else:
        raise ValueError(f"Value {value} must be an integer or a tuple between {default_min} and {default_max}")


"""
Get knot/link/theta/handcuff tables (diagrams) from a given range.
"""


# def knot_names(crossings: int | tuple[int, int] | None = None):
#     # TODO: remove this function
#     crossings = _range_from_value(crossings, _MIN_KNOT_CROSSINGS, _MAX_KNOT_CROSSINGS)
#     map_keys = sorted(set(max(10, c) for c in crossings))
#
#     for knot_name in _knot_table.keys(from_subkeys=map_keys):
#         if crossings[0] <= _parse_knot_name(knot_name)[0] <= crossings[1]:
#             yield knot_name

def knots(crossings: int | tuple[int, int] | None = None):
    crossings = _range_from_value(crossings, _MIN_KNOT_CROSSINGS, _MAX_KNOT_CROSSINGS)  # a tuple of (max_crossings, min_crossings)
    map_keys = sorted(set(max(_KNOT_TABLE_STARTS_WITH, c) for c in crossings))  # a list of which tables we should read knots (table 10 consist of up to 10 crossings, 11 for 11 crossings,...)

    return [
        _knot_table[name].copy()
        for name in _knot_table.keys(from_subkeys=map_keys)
            if crossings[0] <= _parse_knot_name(name)[0] <= crossings[1]
    ]

def links(crossings: int | tuple[int, int] | None = None):
    crossings = _range_from_value(crossings, _MIN_LINK_CROSSINGS, _MAX_LINK_CROSSINGS)  # a tuple of (max_crossings, min_crossings)
    map_keys = sorted(set(max(_LINK_TABLE_STARTS_WITH, c) for c in crossings))  # a list of which tables we should read knots (table 10 consist of up to 10 crossings, 11 for 11 crossings,...)

    return [
        _link_table[name].copy()
        for name in _link_table.keys(from_subkeys=map_keys)
            if crossings[0] <= _parse_link_name(name)[0] <= crossings[1]
    ]



def thetas():
    """Return a list of all theta curves."""
    return [theta for theta in _theta_table_7.values()]


def knot_invariants(crossings: int | tuple[int, int] | list[int, int] | None = None, invariant=None):
    crossings = _range_from_value(crossings, _MIN_KNOT_CROSSINGS, _MAX_KNOT_CROSSINGS)
    map_keys = sorted(set(max(10, c) for c in crossings))

    for knot_name in _knot_invariants.keys(from_subkeys=map_keys):
        if crossings[0] <= _parse_knot_name(knot_name)[0] <= crossings[1]:
            if invariant is None:
                yield _knot_invariants[knot_name]["diagram"], {inv_name: inv_value for inv_name, inv_value in _knot_invariants[knot_name].items() if inv_name != "diagram"}
            else:
                yield _knot_invariants[knot_name]["diagram"], _knot_invariants[knot_name][invariant]

def get_link_table(crossings: int | tuple[int, int] | None = None):
    raise NotImplementedError()

if __name__ == "__main__":
    pass

    # for x in get_theta_curves():
    #     print(x)
    # pass

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



