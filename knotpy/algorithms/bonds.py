from itertools import combinations
from knotpy.algorithms.topology import edges as _edges
from knotpy.classes.planardiagram import Diagram

def is_colored_bonded_knot(k:Diagram):
    """ Checks if the knot is properly colored as a bonded knot (every colored edge has only non-colored adjacent edges)."""
    for edge in _edges(k):
        # check that the edge only has one color
        edge_colors = {ep.attr.get("color", None) for ep in edge}
        if len(edge_colors) != 1:
            return False
    # check that every vertex has exactly one color
    for v in k.vertices:
        number_of_colors = sum("color" in k.endpoint_from_pair((v, pos)).attr for pos in range(k.degree(v)))
        if number_of_colors != 1:
            return False
    return True

def bond_colorings(bonded_knot, bond_color, non_bonded_color):
    """ Colors the diagrams so that every colored edge has only non-colored adjacent edges. """
    colored_bonded_knots = []

    edges = _edges(bonded_knot)
    number_of_bonds = len(edges) // 3  # number of bonds

    # color all possible bonds
    for bonds in combinations(edges, number_of_bonds):
        # set of first and last vertices of every bond
        vertices = {b[0].node for b in bonds} | {b[-1].node for b in bonds}

        # bonds do not touch
        if len(vertices) == 2* number_of_bonds:
            knot_copy = bonded_knot.copy()

            # color all endpoints of the bond edges with color 1
            for b in bonds:
                for ep in b:
                    knot_copy.endpoint_from_pair((ep.node, ep.position)).attr["color"] = bond_color  # set color to 1
            if non_bonded_color is not None:
                for ep in knot_copy.endpoints:
                    if ep.attr.get("color", None) != bond_color:
                        knot_copy.endpoint_from_pair((ep.node, ep.position)).attr["color"] = non_bonded_color

            colored_bonded_knots.append(knot_copy)

    return colored_bonded_knots
