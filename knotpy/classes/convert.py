from itertools import product

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node.crossing import Crossing
from knotpy.utils.set_utils import powerset
from knotpy.manipulation.symmetry import mirror

__all__ = ["vertices_to_crossings"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


def vertices_to_crossings(g:PlanarDiagram, vertices=None, all_crossing_signs=False):
    """
    :param g:
    :param vertices: list of vertices to convert to crossings, if empty all degree 4- vertices are converted
    :param all_crossing_signs: if False, just one crossing sign is converted (default CCW convention), otherwise all combinations of crossing signs will be returned
    :return:
    """
    if vertices is None:
        vertices = list(v for v in g.vertices if g.degree(v) == 4)

    if not all(g.degree(v) == 4 for v in vertices):
        raise ValueError("Cannot convert a vertex to a crossing if it not of degree 4")

    # convert a single vertex to a list
    if not isinstance(vertices, (list, tuple, dict, set)):
        vertices = [vertices]

    for v in g.vertices:
        if v not in g.vertices:
            raise ValueError(f"Cannot convert vertex {vertices} to a crossing")

    if not all_crossing_signs:
        # just convert the vertex to a crossing
        g_copy = g.copy()
        g_copy.convert_nodes(list(vertices), Crossing)
        return g_copy

    else:
        g_copies = []
        g_copy = g.copy()
        g_copy.convert_nodes(vertices, Crossing)  # convert 4-valent vertices to the default crossing

        # get all possible crossing-change combinations
        g_copies.extend(
            mirror(g_copy, crossings=crossings_to_change_sign, inplace=False)
            for crossings_to_change_sign in powerset(vertices)
        )

        return g_copies

