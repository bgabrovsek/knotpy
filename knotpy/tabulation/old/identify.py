"""
identify knot or link from knot/link table
"""

from knotpy.algorithms.canonical import canonical
from knotpy.tabulation.knot_table import filter_table, knot_table, knot_invariants, link_table, link_invariants
from knotpy.invariants.jones_polynomial import jones_polynomial


def identify_diagram(diagram_dict, invariant_dict, diagram, invariants=None):
    """
    :param diagram_dict:
    :param invariant_dict:
    :param diagram:
    :param invariants:
    :return:
    """
    k = canonical(diagram)
    candidates = filter_table(diagram_dict, crossings=len(k))

    # search by diagram
    match = [name for name in candidates if knot_table[name] == k]
    if match:
        return match

    # search by invariant
    if "Jones" in invariants:
        jones = jones_polynomial(k)
        match = filter_table(diagram_dict, max_crossings=len(k), invariant_value={"Jones": jones})

    return match


def identify_knot(diagram, invariants=None):
    """
    :param diagram:
    :param invariants:
    :return:
    """
    return identify_diagram(knot_table, knot_invariants, diagram, invariants)

def identify_link(diagram, invariants=None):
    """
    :param diagram:
    :param invariants:
    :return:
    """
    return identify_diagram(link_table, link_invariants, diagram, invariants)
