"""Layout functions for drawing a planar graph.
"""

from itertools import chain

from matplotlib.path import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages

import knotpy as kp
import knotpy.drawing
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.drawing.circlepack import CirclePack
from knotpy.utils.geometry import Circle
from knotpy.algorithms.components_link import number_of_link_components
from knotpy.algorithms.structure import bridges, loops, kinks
from knotpy.algorithms.disjoint_sum import number_of_disjoint_components
from knotpy.notation.native import to_knotpy_notation
from knotpy.algorithms.structure import insert_arc


#__all__ = ['draw', 'export_pdf', "circlepack_layout"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'




def _bezier_function(z0, z1, z2, derivative=0):
    """Return Bézier curve through control points z0, z1, z2. The curve is as the function or its derivative.
    :param z0: control point
    :param z1: control pointcirclepack.py
draw_matplotlib.py
    :param z2: control point
    :param derivative: order of derivative
    :return:
    """

    if derivative == 0:
        return lambda t: (1 - t) * ((1 - t) * z0 + t * z1) + t * ((1 - t) * z1 + t * z2)
    if derivative == 1:
        return lambda t: 2 * (1 - t) * (z1 - z0) + 2 * t * (z2 - z1)
    if derivative == 2:
        return lambda t: 2 * (z2 - 2 * z1 + z0)
    raise NotImplementedError("derivatives higher than 2 not implemented")


def bezier(*z, straight_lines=False):
    """Draw a Bézier curve of degree 1 or 2.
    :param z: list of coordinates as complex numbers
    :param straight_lines: Bézier curve degree (False = 2, True = 1)
    :return:
    """
    vertices = [(w.real, w.imag) for w in z]
    codes = [Path.MOVETO] + [Path.LINETO if straight_lines else Path.CURVE3] * (len(z) - 1)
    return Path(vertices, codes)




def _repr(d):
    """Nicely print data (region, arc, endpoint/) for debugging."""
    if isinstance(d, int) or isinstance(d, float): return str(d)
    if isinstance(d, str): return d
    if isinstance(d, dict):
        return "{" + ", ".join([_repr(k) + "->" + _repr(v) for k, v in d.items()]) + "}"
    if isinstance(d, list) or isinstance(d, tuple):
        if len(d) == 2 and isinstance(d[1], int):  # guess endpoint
            return _repr(d[0]) + _repr(d[1])
        else:
            return ("[" if isinstance(d, list) else "(") + \
                " ".join(_repr(i) for i in d) + \
                ("]" if isinstance(d, list) else ")")
    return ""




# def preprocess_diagram(k):
#     """ Replaces bridges with triple arcs.
#     Adds two additional arcs to a kink or loop."""
#     k_ = add_support_arcs(k)
#
#     return k_

def circlepack_layout(k):
    """Return a layout for knot k. A layout is a dictionary where keys are nodes/edges/areas and values are circles
    TODO: add support for: bridges, kink/loops, disjoint diagrams
    """


    if len([kinks(k)]):
        ValueError(f"Cannot plot diagram {k}, since it contains a kink.")
    if len(loops(k)):
        ValueError(f"Cannot plot diagram {k}, since it contains a loop.")
    if len(bridges(k)):
        ValueError(f"Cannot plot diagram {k}, since it contains a bridge.")
    if number_of_disjoint_components(k) > 1:
        ValueError(f"Cannot plot diagram {k}, since it contains disjoint components.")


    # if bridges(k) or loops(k):
    #     print(f"Skipping drawing {k}, since drawing loops or bridges in not yet supported.")



    #k = preprocess_diagram(k)

    _debug = False
    external_node_radius = 1.0  # radius of external circles corresponding to nodes
    external_arc_radius = 0.5  # radius of external circles corresponding to arcs

    if _debug: print("Graph is", k)

    regions = list([face for face in k.faces])
    if _debug: print("Regions are", regions)

    # get external endpoints if they exists
    external_endpoints = [ep for ep in k.endpoints if "outer" in ep.attr]
    if external_endpoints:
        external_regions = [face for face in regions if set(face).issuperset(external_endpoints)]
        if len(external_regions) == 1:
            external_region = external_regions[0]
        else:
            print("Warning: multiple external regions")
            external_region = external_regions[0]
    else:
        external_region = min(regions, key=lambda r: (-len(r), r))  # sort by longest, then by lexicographical order

    # print("External endpoints", external_endpoints)
    # print("Faes", list(k.faces))

    if _debug: print("External region is", external_region)

    regions.remove(external_region)

    # sorted(g.regions(), key=lambda r: (-len(r), r)) # sort by longest, then by lexicographical order
    if _debug: print("Internal regions are", regions)

    arcs = list(k.arcs)
    if _debug: print("Arcs are", arcs)

    ep_to_arc_dict = {ep: arc for arc in arcs for ep in arc}
    ep_to_reg_dict = {ep: reg for reg in (regions + [external_region]) for ep in reg}

    # add external nodes and arcs to the set of external circles
    external_circles = {ep.node: external_node_radius for ep in external_region} | \
                       {ep_to_arc_dict[ep]: external_arc_radius for ep in external_region}  # nodes & arcs

    # region -> arc / node
    internal_circles = {region: list(chain(*((ep_to_arc_dict[ep], ep.node) for ep in region))) for region in regions}

    # node -> region / arc
    internal_circles |= {v: list(chain(
        *((ep_to_arc_dict[ep], ep_to_reg_dict[ep]) for ep in k.nodes[v])
    )) for v in k.nodes}

    # arc -> region / node
    internal_circles |= {frozenset({ep0, ep1}): [ep_to_reg_dict[ep1], ep0.node, ep_to_reg_dict[ep0], ep1.node] for ep0, ep1 in arcs}

    internal_circles = {key: internal_circles[key] for key in internal_circles if key not in external_circles}

    circles = CirclePack(internal=internal_circles, external=external_circles)
    # we need to conjugate, for knotoids the diagram is in CW order
    return {key: Circle(value[0].conjugate(), value[1]) for key, value in circles.items()}  # return Circle objects
