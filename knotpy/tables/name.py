


def clean_name(name: str) -> str:
    """
    Normalize a knot, link, theta-curve, or handcuff name into a canonical format.

    Handles capitalization, underscore insertion, mirror indicators (*),
    and orientation signs (+/-). Recognizes and formats identifiers like:
    - Knots: 'K10_14' → '10_14', '31' → '3_1', '112' → '11_2', '11a17' → '11a_17'
    - Links: 'l6A2*' → 'L6a_2*'
    - Thetas: 'T31' → 'T3_1'
    - Handcuffs: 'h6n42+-' → 'H6n_42+-'

    Raises:
        ValueError: If multiple type indicators (L, T, H) are found.
    """

    _knot_naming_synonyms = {
        "unknot": "0_1", "trefoil": "3_1", "figureeight": "4_1", "pentafoil": "5_1",
        "3twistknot": "5_2", "3twist": "5_2", "stevedoresknot": "6_1", "stevedores": "6_1", "stevedore": "6_1",
        "themillerinstituteknot": "6_2", "millerinstituteknot": "6_2", "millerinstitute": "6_2",
        "cinquefoil": "5_1", "septafoil": "7_1", "nonafoil": "9_1", "nonalternating": "8_19",
        "hopf": "L2a_1", "hopflink": "L2a_1",
        "solomonsknot": "L4a_1", "guillocheknot": "L4a_1", "guilloche": "L4a_1", "solomons": "L4a_1", "solomon": "L4a_1",
        "whitehead": "L5a_1", "whiteheadlink": "L5a_1",
        "borromeanrings": "L6a_4", "borromeanlink": "L6a_4", "borromean": "L6a_4",
        "theta": "T0_1", "trivialtheta": "T0_1", "handcuff": "H0_1", "trivialhandcuff": "H0_1"
    }

    if (simplified := ''.join(c for c in name if c.isalnum()).lower()) in _knot_naming_synonyms:
        return _knot_naming_synonyms[simplified]

    # Mirror and orientation
    mirror_count = name.count("*")
    is_mirrored = mirror_count % 2 == 1
    orientations = [c for c in name if c in "+-"]

    # Normalize letter casing
    name = ''.join(
        c.upper() if c.lower() in "lth" else c.lower() if c.lower() in "an" else c
        for c in name
    )

    # Extract prefix
    prefixes = [c for c in name if c in "LTH"]
    if len(prefixes) > 1:
        raise ValueError(f"Multiple type indicators found: {prefixes}")
    prefix = prefixes[0] if prefixes else ""

    # Strip all unwanted characters
    allowed = set("0123456789_an")
    raw = ''.join(c for c in name if c in allowed)

    # Insert underscore if missing
    if "_" not in raw:
        if "a" in raw or "n" in raw:
            ai = raw.find("a") if "a" in raw else raw.find("n")
            crossing = raw[:ai]
            letter = raw[ai]
            index = raw[ai + 1:]
            raw = f"{crossing}{letter}_{index}"
        else:
            if len(raw) == 2:
                raw = f"{raw[0]}_{raw[1]}"
            elif len(raw) == 3:
                raw = f"{raw[:2]}_{raw[2]}"
            else:
                raise ValueError(f"Cannot parse identifier from: {raw}")

    # Ensure a/n is followed by underscore
    if "a" in raw or "n" in raw:
        ai = raw.find("a") if "a" in raw else raw.find("n")
        if raw[ai + 1] != "_":
            raw = raw[:ai + 1] + "_" + raw[ai + 1:]

    # Build final name
    result = prefix + raw
    if is_mirrored:
        result += "*"
    if orientations:
        result += ''.join(orientations)
    return result


def parse_name(name: str):
    """
    Parse a clean knot/link/theta/handcuff name into its components.

    Assumes the name is in standard normalized form:
        [L|T|H]Crossings[a|n]_Index[*][+-...]

    Returns:
        type_name: one of "knot", "link", "theta", "handcuff"
        crossings: int
        alt_type: one of "a" (alternating), "n" (non-alternating), or None
        index: int
        mirror: bool
        orientation: string of + and - (can be empty)
    """

    name = name.strip()
    # orientation
    orientation = "".join([c for c in name if c == "+" or c == "-"])
    # mirror
    mirror = "*" in name
    # type
    type_name = "knot"
    for key, value in [("L", "link"), ("T", "theta"), ("H", "handcuff"), ("K", "knot")]:
        if key in name:
            type_name = value
    # alternating/non-alternating
    if "a" in name:
        alt_type = "a"
    elif "n" in name:
        alt_type = "n"
    else:
        alt_type = None
    # number of crossings
    crossing_str, index_str = name.split("_")
    number_of_crossings = int(''.join(c for c in crossing_str if c.isdigit()))
    # index
    index = int(''.join(c for c in index_str if c.isdigit()))
    return type_name, number_of_crossings, alt_type, index, mirror, orientation


def diagram_from_name(name):
    from knotpy.tables.knot import knot
    from knotpy.tables.theta import theta, handcuff
    """Return any diagram (knot, link, theta curve, handcuff link,...) from its name."""
    name = clean_name(name)
    print(clean_name(name))
    # Is the name a link?
    if "L" in name:
        pass
    # Is the name a theta curve?
    elif "T" in name:
        return theta(name)
    # Is the name a handcuff link?
    elif "H" in name:
        return handcuff(name)
    # is the name a knot?
    else:
        return knot(name)