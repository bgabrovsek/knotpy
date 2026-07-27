__all__ = ["unplugging"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


from collections import deque
from random import choice
from itertools import combinations

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.naming import unique_new_node_name
from knotpy.algorithms.rewire import replug_endpoint
from knotpy.classes.node import Vertex
from knotpy.algorithms.remove import remove_bivalent_vertices
from knotpy.algorithms.components_link import link_components_endpoints
from knotpy.reidemeister.simplify import simplify as _simplify
from knotpy.algorithms.canonical import canonical

def _unplug(k: PlanarDiagram, node, unplug_endpoint_positions):
    """Unplug endpoints from the node.
    :param k: Planar diagram
    :param node: the node to unplug endpoints
    :param unplug_endpoint_positions: positions/indices to be unplugged
    :return:
    """

    unplug_endpoint_positions = sorted(unplug_endpoint_positions)
    while unplug_endpoint_positions:
        position = unplug_endpoint_positions.pop()  # remove (last) endpoint at index
        # create new leaf node
        new_node = unique_new_node_name(k)
        k.add_node(node_for_adding=new_node, create_using=Vertex, degree=1)
        replug_endpoint(k, source_endpoint=(node, position), destination_endpoint=(new_node, 0))

def _color_uncolored_endpoints(k: PlanarDiagram, color):
    """ Color all uncolored endpoints."""
    for ep in k.endpoints:
        if "color" not in ep.attr:
            ep.attr["color"] = color

def _propagate_endpoint_colors_to_set(knot):
    """Propagate endpoint colors (so all endpoints on a component are colored)
    and convert colors to a set (ordered tuple without repetition)."""

    for component in link_components_endpoints(knot):
        colors = tuple(sorted({ep.attr["color"] for ep in component if "color" in ep.attr}))
        for ep in component:
            ep.attr["color"] = colors

def _flatten_colors(knot, mixed_color):
    """ Convert singleton colors to element and non-singlton to mixed_color"""
    for ep in knot.endpoints:
        if len(ep.attr["color"]) == 1:
            ep.attr["color"] = next(iter(ep.attr["color"]))
        elif len(ep.attr["color"]) > 1:
            ep.attr["color"] = mixed_color
        else:
            raise ValueError("No color")

def unplugging(k: PlanarDiagram, simplify=True, mixed_color=None):

    """Computes the "unplugging" invariant T.
    See Kauffman, L. H. (1989). Invariants of graphs in three-space. Transactions of the American Mathematical Society,
    311(2), 697-710.

        k: spatial graph for which
        simplify:
        default_color: color for uncolored edges
        mixed_color: optionally one can replace mixed colors with a single color
    """

    stack = deque()
    stack.append(k.copy())  # put a shallow copy onto the stack
    constituent_knots = []  # value (result) of the invariant

    is_colored = any("color" in ep.attr for ep in k.endpoints)

    while stack:
        k = stack.pop()
        vertices = [v for v in k.vertices if k.degree(v) > 2]

        # if there are no vertices, the unplugging is the knot
        if not vertices:
            constituent_knots.append(k)
            continue

        # choose a vertex and put all local replacements on the stack
        v = choice(vertices)  # choose a vertex, vertex[0] would be faster
        deg = k.degree(v)
        for p in combinations(range(deg), 2):
            # p=(i,j) are plugged nodes, i.e. keep v[i] and v[j] plugged, remove the rest of the endpoints
            unplug_k = k.copy()
            _unplug(unplug_k, node=v, unplug_endpoint_positions=set(range(deg)) - set(p))
            stack.append(unplug_k)

    for c in constituent_knots:
        if is_colored:
            _propagate_endpoint_colors_to_set(c)
            _flatten_colors(c, mixed_color)
        remove_bivalent_vertices(c)

    if simplify:
        constituent_knots_ = [_simplify(_, keep_attributes=True) for _ in constituent_knots]
        constituent_knots_ = [canonical(_) for _ in constituent_knots_]
        return sorted(constituent_knots_)

    return constituent_knots

