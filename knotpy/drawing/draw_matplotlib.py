"""Draw a planar graph from a PlanarGraph object."""

import math
import warnings
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection, LineCollection, PolyCollection
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import to_rgb

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node import Vertex, Crossing
from knotpy.classes.endpoint import IngoingEndpoint, Endpoint
from knotpy.algorithms.topology import bridges, loops, kinks, leafs
from knotpy.algorithms.cut_set import cut_nodes
from knotpy.utils.multiprogressbar import Bar
from knotpy.drawing.layout import circlepack_layout, bezier
from knotpy.utils.geometry import (Circle, CircularArc, Line, Segment, perpendicular_arc, is_angle_between, antipode,
                                   tangent_line, middle, bisector, bisect, split,
                                   perpendicular_arc_through_point, BoundingBox, weighted_circle_center_mean)

from knotpy.drawing._support import _add_support_arcs
from knotpy.notation.native import to_knotpy_notation
from sklearn.decomposition import PCA
from knotpy.notation import to_knotpy_notation

__all__ = ['draw', 'export_pdf', "circlepack_layout", "draw_from_layout", "plt", "export_png", "export_pdf_groups"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


# default styles
# node
_DEFAULT_NODE_SIZE = 0.1
_DEFAULT_NODE_COLOR = "black"

# arcs
_DEFAULT_ARC_WIDTH = 1.5
_DEFAULT_ARC_COLOR = "tab:blue"
_DEFAULT_GAP_WIDTH = 0.2  # arc break marking the under-passing
# text
_DEFAULT_TEXT_COLOR = "black"
_DEFAULT_FONT_SIZE = 16
_DEFAULT_FONT_SIZE_PIXELS = _DEFAULT_FONT_SIZE * 72 / 100 / 100  # default 100 DPI
# circles
_DEFAULT_CIRCLE_ALPHA = 0.15
_DEFAULT_CIRCLE_COLOR = "cadetblue"
# edge colors
_EDGE_COLORS = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray',
               'tab:olive', 'tab:cyan']

# arrows
_ARROW_LENGTH = 0.25
_ARROW_WIDTH = 0.25
_ARROW_FLOW = 0.5  # arrow slant so it appears more natural, 0 = tangent
_DEFAULT_ARROW_COLOR = _DEFAULT_ARC_COLOR

_SHOW_SUPPORT_ARCS = False
_SUPPORT_COLOR = "yellow"



def to_color(item):
    return _EDGE_COLORS[item % len(_EDGE_COLORS)] if isinstance(item, int) else item

def average_color(color1, color2):
    rgb1, rgb2 = to_rgb(to_color(color1)), to_rgb(to_color(color2))
    return (rgb1[0] + rgb2[0])/2, (rgb1[1] + rgb2[1])/2, (rgb1[2] + rgb2[2])/2


class Arrow:
    """Class representing a graphical arrow."""
    def __init__(self, pointy_end: complex, direction: complex):
        """
        :param pointy_end: the position of the pointy end of the arrow (end point)
        :param direction: direction of arrow from start point to end point
        """
        self.point = pointy_end
        self.direction = direction / abs(direction)

    def triangle(self):
        point0 = self.point
        point_ = self.point - self.direction * _ARROW_LENGTH
        point1 = point_ + 1j * self.direction * 0.5 * _ARROW_WIDTH
        point2 = point_ - 1j * self.direction * 0.5 * _ARROW_WIDTH
        return [(point0.real, point0.imag), (point1.real, point1.imag), (point2.real, point2.imag)]





def _plot_vertices(k, circles, with_labels, ax):
    """Plot vertices as points or circles with label
    :param k: planar graph
    :param circles: dictionary containing vertices as keys and (position, radius) as value
    :param with_labels: set True to draw node labels
    :param ax: pyplot axis
    :return:
    """

    vertices = k.vertices if hasattr(k, "vertices") else []

    crossings = k.crossings if hasattr(k, "crossings") else []

    for node in crossings:
        circle = circles[node]
        xy = (circle.center.real, circle.center.imag) if isinstance(circle, Circle) else (circle.real, circle.imag)

        if with_labels:
            ax.text(*xy,
                    s=str(node),
                    ha="center",
                    va="center",
                    fontsize=_DEFAULT_FONT_SIZE//2,
                    color=_DEFAULT_TEXT_COLOR,
                    zorder=4)

    for node in vertices:
        circle = circles[node]
        xy = (circle.center.real, circle.center.imag) if isinstance(circle, Circle) else (circle.real, circle.imag)

        if not _visible(k.nodes[node]):
            continue

        if with_labels:
            circle_patch_out = plt.Circle(xy, _DEFAULT_FONT_SIZE_PIXELS * 1.3 + _DEFAULT_ARC_WIDTH / 100 * 1.5,
                                          color=k.nodes[node].attr.get("color", _DEFAULT_NODE_COLOR), zorder=2)
            circle_patch_in = plt.Circle(xy, _DEFAULT_FONT_SIZE_PIXELS * 1.3,
                                         color="white", zorder=3)
            ax.add_patch(circle_patch_out)
            ax.add_patch(circle_patch_in)
            ax.text(*xy,
                    s=str(node),
                    ha="center",
                    va="center",
                    fontsize=_DEFAULT_FONT_SIZE,
                    color=_DEFAULT_TEXT_COLOR,
                    zorder=4)
        else:
            color = k.nodes[node].attr.get("color", _DEFAULT_NODE_COLOR)
            circle_patch = plt.Circle(xy, _DEFAULT_NODE_SIZE / 2, color=color, zorder=3)
            ax.add_patch(circle_patch)

    # BOND NODES
    for key in circles:
        if isinstance(key, str) and "__BOND__" in key:
            # BONDED NODE
            BONDED_NODE_COLOR = "black"
            value = circles[key]
            xy = (value.real, value.imag)
            circle_patch = plt.Circle(xy, _DEFAULT_NODE_SIZE / 2 * 0.67, color=BONDED_NODE_COLOR, zorder=3)
            ax.add_patch(circle_patch)



def _plot_circles(circles, ax):
    """Plot circles obtained by the circle packing theorem to draw the diagram.
    :param circles:  dictionary containing vertices/edges/areas as keys and (position, radius) as value
    :param ax: pyplot axis
    :return:
    """
    for circle in circles.values():
        circle_patch = plt.Circle((circle.center.real, circle.center.imag), circle.radius,
                                  alpha=_DEFAULT_CIRCLE_ALPHA,
                                  facecolor=_DEFAULT_CIRCLE_COLOR,
                                  ls="none")
        ax.add_patch(circle_patch)


def _plot_middle_arc(k: PlanarDiagram, circles):
    """The middle "arc" part that is a path through the arc circle and starts and ends on the intersection of the arc
    circle and the adjacent tangent node circles.
    :param k:
    :param circles:
    :return:
    """

    approximate = True

    result_curves = []
    for arc in k.arcs.keys():
        ep0, ep1 = arc

        # do not draw if invisible
        if not _visible(ep0) or not _visible(ep1):
            continue

        # compute the arc that is perpendicular to the arc circle
        g_arc = perpendicular_arc(circles[arc], circles[ep0.node], circles[ep1.node], approx=approximate)
        color1 = k.nodes[ep0].get("color", _DEFAULT_ARC_COLOR)
        color2 = k.nodes[ep1].get("color", _DEFAULT_ARC_COLOR)
        if color1 != color2:
            print("Warning: different colored twin edges not yet supported.")
        color = average_color(color1, color2)

        # TODO: if endpoints are different color, split arcs in half using the bisect() method
        result_curves.append((g_arc, color))
    return result_curves


def _vertex_endpoints_colors(k, v):
    # return a list of colors of endpoints of v in order
    return [to_color(k.nodes[ep].get("color", _DEFAULT_ARC_COLOR)) for ep in k.endpoints[v]]


def _closest_point_to_circle_index(circle, points):
    # return the index of the circle that is closest to the point
    distances = [abs(point - circle.center) for point in points]
    return distances.index(max(distances))


def _indices_by_value_count(lst):
    """ Return sorted indices of the list, e.g. given [1,1,5,8,5,1], it will return  [(3,), (2,4), (0,1,5)],
    i.e. indices 8, 5, 1 respectfully."""
    counter = defaultdict(list)
    for i, val in enumerate(lst):
        counter[val].append(i)
    return sorted(counter.values(), key=lambda t: len(t))


def _visible(__obj):
    """Should object (node, endpoint, ...) be shown in diagram?
    :param __obj:
    :return:
    """
    if not hasattr(__obj, "attr"):
        return True
    if "__support__" in __obj.attr and __obj.attr["__support__"]:
        return False
    return True


def _plot_endpoint(k: PlanarDiagram, circles: dict, arc, ep: Endpoint, gap=False, arrow=False):
    """ Plot the node endpoint presented by the arc. Also plot arrows, gaps, etc.
    :param k: planar diagram
    :param circles: circle-packing
    :param arc: the geometric arc to draw
    :param ep: endpoint to draw
    :return:
    """

    if not _visible(ep):
        return []
    return_curves = []
    color = to_color(ep.get("color", _DEFAULT_ARC_COLOR))

    # get the two endpoints od the arc
    pt0 = arc(arc.theta1) if isinstance(arc, CircularArc) else arc(0)
    pt1 = arc(arc.theta2) if isinstance(arc, CircularArc) else arc(1)
    # which arc endpoint is the one at the vertex/crossing, 0 or 1?
    node_pt = 0 if abs(circles[ep.node].center - pt0) < abs(circles[ep.node].center - pt1) else pt1

    if isinstance(arc, CircularArc):
        if not gap:
            return_curves.append((arc, color))
            arrow_angle = _ARROW_LENGTH / arc.radius  # circular arc length is s = theta * radius
            if arrow and isinstance(ep, IngoingEndpoint):

                if arrow and isinstance(ep, IngoingEndpoint):
                    if node_pt == 0:
                        a = Arrow(arc(arc.theta1 + arrow_angle*0.5),
                                  arc(arc.theta1) - arc(arc.theta1 + arrow_angle))
                        return_curves.append((a, color))
                    else:
                        a = Arrow(arc(arc.theta2 - arrow_angle*0.5),
                                  arc(arc.theta2) - arc(arc.theta2 - arrow_angle))
                        return_curves.append((a, color))

        else:

            gap_angle = _DEFAULT_GAP_WIDTH / arc.radius  # circular arc length is s = theta * radius
            arrow_angle = _ARROW_LENGTH / arc.radius  # circular arc length is s = theta * radius
            if arc.length() > _DEFAULT_GAP_WIDTH:
                if node_pt == 0:
                    return_curves.append((CircularArc(arc.center, arc.radius, arc.theta1 + gap_angle, arc.theta2), color))
                    if arrow and isinstance(ep, IngoingEndpoint):
                        a = Arrow(arc(arc.theta1 + gap_angle - arrow_angle * 0.25),
                                  arc(arc.theta1 + gap_angle) - arc(arc.theta1 + gap_angle + arrow_angle))
                        return_curves.append((a, color))
                else:
                    return_curves.append((CircularArc(arc.center, arc.radius, arc.theta1, arc.theta2 - gap_angle), color))
                    if arrow and isinstance(ep, IngoingEndpoint):
                        a = Arrow(arc(arc.theta2 - gap_angle + arrow_angle * 0.25),
                                  arc(arc.theta2 - gap_angle) - arc(arc.theta2 - gap_angle - arrow_angle))
                        return_curves.append((a, color))

    elif isinstance(seg := arc, Segment):
        if not gap:
            return_curves.append((seg, color))
        else:
            gap_t = _DEFAULT_GAP_WIDTH / seg.length()
            if node_pt == 0:
                return_curves.append((seg(gap_t, 1), color))
            else:
                return_curves.append((seg(0, 1-gap_t), color))

        if arrow and isinstance(ep, IngoingEndpoint):
            arrow_t = _ARROW_WIDTH / seg.length()
            if node_pt == 0:
                a = Arrow(arc(0), arc(0) - arc(arrow_t))
                return_curves.append((a, color))
            else:
                a = Arrow(arc(1), arc(1) - arc(1-arrow_t))
                return_curves.append((a, color))


    else:
        raise TypeError(f"Arc {arc} is of type {type(arc)}, but should be of type CircularArc or Segment")

    return return_curves


def _plot_all_endpoints(k: PlanarDiagram, circles, new_vertices: dict):

    approximate = False

    result_curves = []

    for v in k.nodes:
        node = k.nodes[v]
        arcs = k.arcs[v]
        endpoints = k.endpoints[v]
        colors = [to_color(k.nodes[ep].get("color", _DEFAULT_ARC_COLOR)) if _visible(ep) else None for ep in endpoints]
        #visibles = [ep for ep in endpoints if _visible(ep)]
        # is the vertex smooth?
        if isinstance(node, Vertex) and len(colors) == 3 and len(set(colors)) == 2:
            """If geometry allows, create a 3-valent vertex, such that:
             - the two same colored edges are represented by an arc perpendicular to the vertex circle
             - the one single colored arc is a segment lying on the line through the edge and the antipodal point
             Otherwise create a 3-valent vertex, such that:
             - the two same colored edges are represented by an arc perpendicular to the vertex circle
             - the single colored arc lies on a circular arc perpendicular to the circle and goes through the bisection
               point of the "same colored arc" at step 1. This point is obtained as the intersection of the tangent line
               at the single arc and the bisector line through the segment of the edge point and the bisector of the
               "same colored arc"
            """
            """Connect 3-valent vertices with 2 colors such that the same colored vertices are smooth at crossing"""
            [b], [a1, a2] = _indices_by_value_count(colors)  # indices of same (a1, a2) and different (b) arc
            ep_b, ep_a1, ep_a2 = endpoints[b], endpoints[a1], endpoints[a2]
            arc_b, arc_a1, arc_a2 = arcs[b], arcs[a1], arcs[a2]

            """the two same colored edges are represented by an arc perpendicular to the vertex circle"""
            # arcs that are the same color
            same_arc = perpendicular_arc(circles[v], circles[arc_a1], circles[arc_a2], order := [])

            boundary_b_point = circles[arc_b] * circles[v]  # intersection point on the circle boundary
            boundary_b_point = boundary_b_point[0]
            mid_arc_point = middle(same_arc)

            diff_arc = perpendicular_arc_through_point(circles[v], boundary_b_point, mid_arc_point)

            # draw the single endpoint that is of different color

            result_curves += _plot_endpoint(k, circles, diff_arc, ep_b, gap=False, arrow=True)


            same_arc1, same_arc2 = bisect(same_arc)
            result_curves += _plot_endpoint(k, circles, same_arc1, ep_a1 if order[0] == 1 else ep_a2, gap=False, arrow=True)
            result_curves += _plot_endpoint(k, circles, same_arc2, ep_a2 if order[1] == 2 else ep_a1, gap=False, arrow=True)

            new_vertices[v] = mid_arc_point

        # is it a non-smooth vertex?
        elif isinstance(node, Vertex) and k.degree(v) == 2:
            """if degree is 2, then plot an arc"""
            arc1, arc2 = arcs
            ep1, ep2 = endpoints
            same_arc = perpendicular_arc(circles[v], circles[arc1], circles[arc2], order := [])
            same_arc1, same_arc2 = bisect(same_arc)
            mid_arc_point = middle(same_arc)
            result_curves += _plot_endpoint(k, circles, same_arc1, ep1 if order[0] == 1 else ep2, gap=False, arrow=True)
            result_curves += _plot_endpoint(k, circles, same_arc2, ep2 if order[1] == 2 else ep1, gap=False, arrow=True)
            new_vertices[v] = mid_arc_point

        elif isinstance(node, Vertex):
            """Connect vertex-like endpoints by straight lines from the middle arc to the vertex node.
            But skip 3-valent vertices where one arc is smooth (two arcs that have the same color, but is different from one
            of the rest od the endpoints. TODO: make the average boundary point as the node position and and arcs"""
            for arc in k.arcs[v]:  # loop through incident arcs
                ep0, ep1 = arc

                # if not _visible(ep0):
                #     continue

                color = to_color(k.nodes[ep0].get("color", _DEFAULT_ARC_COLOR))  # assume 1st endpoint is at vertex
                int_point = circles[arc] * circles[v]  # intersection point
                int_point = int_point[0]

                if _visible(ep0):
                    result_curves.append((Segment(int_point, circles[v].center), color))


        elif isinstance(node, Crossing):
            """Connect crossing endpoints. Plot two circular arcs from the crossing to the endpoint. The over-arc is a single
            circular arc, the under-arc splits into two sub-arcs, the gap represents the arc break emphasizing that the 
            under-arc travels below the over-arc."""

            # get circular arcs
            over_arc = perpendicular_arc(circles[v], circles[arcs[1]], circles[arcs[3]], over_order := [], approx=approximate)
            under_arc = perpendicular_arc(circles[v], circles[arcs[0]], circles[arcs[2]], under_order := [], approx=approximate)


            if approximate:
                point = [weighted_circle_center_mean(over_arc, under_arc)]
            else:
                point = (over_arc * under_arc)

            #point = (over_arc * under_arc)

            if not isinstance(point, complex):
                point = point[0]

            over_arc1, over_arc3 = split(over_arc, point)
            under_arc0, under_arc2 = split(under_arc, point)

            result_curves += _plot_endpoint(k, circles, over_arc1, endpoints[1] if over_order[0] == 1 else endpoints[3], gap=False, arrow=False)
            result_curves += _plot_endpoint(k, circles, over_arc3, endpoints[3] if over_order[1] == 2 else endpoints[1], gap=False, arrow=False)

            result_curves += _plot_endpoint(k, circles, under_arc0, endpoints[0] if under_order[0] == 1 else endpoints[2], gap=True, arrow=True)
            result_curves += _plot_endpoint(k, circles, under_arc2, endpoints[2] if under_order[0] == 1 else endpoints[0], gap=True, arrow=True)

        elif isinstance(node, Bond):
            # TODO: make for bonds...
            DEFAULT_BOND_COLOR = "black"
            arc01 = perpendicular_arc(circles[v], circles[arcs[0]], circles[arcs[1]], order01 := [])
            arc23 = perpendicular_arc(circles[v], circles[arcs[2]], circles[arcs[3]], order23 := [])
            arc0, arc1 = bisect(arc01)
            arc2, arc3 = bisect(arc23)
            result_curves += _plot_endpoint(k, circles, arc0, endpoints[0] if order01[0] == 1 else endpoints[1], gap=False, arrow=False)
            result_curves += _plot_endpoint(k, circles, arc1, endpoints[1] if order01[1] == 2 else endpoints[0], gap=False, arrow=False)
            result_curves += _plot_endpoint(k, circles, arc2, endpoints[2] if order23[0] == 1 else endpoints[3], gap=False, arrow=False)
            result_curves += _plot_endpoint(k, circles, arc3, endpoints[3] if order23[1] == 2 else endpoints[2], gap=False, arrow=False)
            result_curves.append((Segment(middle(arc01), middle(arc23)), DEFAULT_BOND_COLOR))
            new_vertices["__BOND__0" + str(len(new_vertices))] = middle(arc01)
            new_vertices["__BOND__2" + str(len(new_vertices))] = middle(arc23)

            #result_curves.append((Circle(middle(arc01), DEFAULT_BOND_NODE_RADIUS), DEFAULT_BOND_COLOR))
            #result_curves.append((Circle(middle(arc23), DEFAULT_BOND_NODE_RADIUS), DEFAULT_BOND_COLOR))

            # draw the bond itself

    return result_curves


def _plot_arcs(k, circles, ax, bounding_box=None):
    """ Plot diagram arcs obtained by the circle-packing theorem. An arc is a path from a node to a node.
    :param k: planar graph
    :param circles: dictionary containing vertices (or arcs or areas) as keys and (position, radius) as values
    :param ax: pyplot axis
    :param bounding_box: BoundingBox object
    :return:
    """

    curves = []  # curves patches

    """In new_vertices, coordinates of vertices given by intersections are stored. 
    Nodes are not necessarily positioned in the center of the circle, but might be moved inside the
    circle, so the layout looks more natural. 
    """
    new_vertices = dict()
    # draw middle arc
    curves += _plot_middle_arc(k, circles)

    curves += _plot_all_endpoints(k, circles, new_vertices)

    # plot

    # filter arcs and segments
    arc_patches = [patches.Arc((arc.center.real, arc.center.imag), 2 * arc.radius, 2 * arc.radius,
                       theta1=math.degrees(arc.theta1), theta2=math.degrees(arc.theta2))
                   for arc, color in curves if isinstance(arc, CircularArc)]

    arc_colors = [color for arc, color in curves if isinstance(arc, CircularArc)]

    segments = [((seg.A.real, seg.A.imag), (seg.B.real, seg.B.imag)) for seg, color in curves if isinstance(seg, Segment)]
    segment_colors = [color for seg, color in curves if isinstance(seg, Segment)]

    arrows = [pol for pol, color in curves if isinstance(pol, Arrow)]
    arrow_colors = [color for seg, color in curves if isinstance(seg, Arrow)]  # TODO: use zip

    # circles/points
    arc_patches = [patches.Arc((arc.center.real, arc.center.imag), 2 * arc.radius, 2 * arc.radius,
                       theta1=math.degrees(arc.theta1), theta2=math.degrees(arc.theta2))
                   for arc, color in curves if isinstance(arc, CircularArc)]

    arc_colors = [color for arc, color in curves if isinstance(arc, CircularArc)]


    ax.add_collection(PatchCollection(arc_patches,
                                      facecolor='none',
                                      lw=_DEFAULT_ARC_WIDTH,
                                      edgecolor=arc_colors,
                                      ))

    ax.add_collection(LineCollection(segments,
                                     facecolor='none',
                                     lw=_DEFAULT_ARC_WIDTH,
                                     edgecolor=segment_colors,
                                     ))

    # Create a PolyCollection with the triangles

    ax.add_collection(
        PolyCollection(
        [arrow.triangle() for arrow in arrows],
        facecolors=arrow_colors, edgecolors="none"
    )
    )

    # compute the bounding box
    if bounding_box is not None:
        for g, color in curves:
            if isinstance(g, CircularArc) or isinstance(g, Segment):
                bounding_box |= BoundingBox(g)
    return new_vertices

def compute_PCA(complex_points: list):
    """
    https: // en.wikipedia.org / wiki / Principal_component_analysis

    :param complex_points: list of complex points
    :return:
    """
    # Step 1: Convert complex numbers to 2D vectors (x, y)
    points_2d = [[z.real, z.imag] for z in complex_points]

    # Step 2: Fit PCA model to the data
    pca = PCA(n_components=2)
    pca.fit(points_2d)

    # Step 3: Extract the principal components and explained variance
    conjugated_principal_components = [complex(c[0], -c[1]) for c in pca.components_]
    conjugated_principal_components = [c / abs(c) for c in conjugated_principal_components]  # they should already be normalized
    # the 0th principal component should be the biggest

    conj_print_comp = conjugated_principal_components[0]

    return [c*conj_print_comp for c in complex_points]




def canonically_rotate_layout(layout, PCA_degrees=0):
    """

    :param layout:
    :param PCA_degrees: https://en.wikipedia.org/wiki/Principal_component_analysis
    :return:
    """
    centers = [circle.center for circle in layout.values()]
    radii = [circle.radius for circle in layout.values()]

    mass_center = sum(c * r for c, r in zip(centers, radii)) / sum(radii)
    centers = [c - mass_center for c in centers]
    centers = aligned_centers = compute_PCA(centers)
    # rotate centers
    rotation = complex(math.cos(math.radians(PCA_degrees)), math.sin(math.radians(PCA_degrees)))
    centers = [c * rotation for c in centers]
    return {key: Circle(c, r) for key, c, r in zip(layout, centers, radii)}


def draw_from_layout(k,
                     layout,
                     draw_circles=True,
                     with_labels=False,
                     with_title=False,
                     ax=None,
                     **style_kwargs):
    """
    :param k:
    :param layout:
    :param draw_circles:
    :param with_labels:
    :param with_title:
    :param ax:
    :angle from the principal component analysis (to canonically rotate the circles)
    :return:
    """

    use_bounding_box = False
    margin = 0.5  # max(radius for coord, radius in circles.values()) * 0.25
    bb = BoundingBox() if use_bounding_box else None

    if ax is None:
        ax = plt.gca()

    # compute image size
    x_min = min(circle.center.real - circle.radius for circle in layout.values()) - margin
    x_max = max(circle.center.real + circle.radius for circle in layout.values()) + margin
    y_min = min(circle.center.imag - circle.radius for circle in layout.values()) - margin
    y_max = max(circle.center.imag + circle.radius for circle in layout.values()) + margin

    # if plt.get_fignums():
    #     plt.close()

    # Create a figure and axis
    #fig, ax = plt.subplots(figsize=((x_max - x_min), (y_max - y_min)))
    ax.axis('off')

    if draw_circles:
        _plot_circles(layout, ax)

    new_vertices = _plot_arcs(k, layout, ax, bounding_box=bb)

    layout.update(new_vertices)

    _plot_vertices(k, layout, with_labels=with_labels, ax=ax)

    if with_title:

        ax.set_title(k.attr["_title"], fontsize=5)



    # Set axis limits for better visualization
    if use_bounding_box:
        bb.add_padding(fraction=0.1)
        bb.make_square()
        ax.set_xlim(bb.bottom_left.real, bb.top_right.real)
        ax.set_ylim(bb.bottom_left.imag, bb.top_right.imag)
    else:
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

    # Set aspect ratio to be equal
    ax.set_aspect('equal', adjustable='box')


def get_style_from_style(style_kwargs):
    """ Get full style from (optional) partial style keywords."""

    def _get(keys, default):
        # get first keyword from style_kwargs, default if not present
        for _ in [keys] if isinstance(keys, str) else keys:
            if _ in style_kwargs:
                return style_kwargs[_]
        return default

    return {
        "node-size": _get(["node-size", "ms", "nodesize", "markersize", "ns"], _DEFAULT_NODE_SIZE),
        "node-color": _get(["node-color", "nodecolor", "nc", "markerfacecolor", "markercolor"], _DEFAULT_NODE_COLOR),
        "arc-width": _get(["arc-width", "arcwidth", "aw", "width", "w", "lw", "linewidth", "alw"], _DEFAULT_ARC_WIDTH),
        "arc-color": _get(["arc-color", "arccolor", "ac", "color", "c"], _DEFAULT_ARC_COLOR),
        "gap-width": _get(["gap-width", "gapwidth", "gw", "gap"], _DEFAULT_GAP_WIDTH),
        "arrow-length": _get(["arrow-length", "al", "arrowlength"], _ARROW_LENGTH),
        "arrow-width": _get(["arrow-width", "aw", "arrowwidth"], _ARROW_WIDTH),
        "arrow-flow": _get(["arrow-flow", "arrowflow", "aflow", "flow"], _ARROW_FLOW),
        "arrow-color": _get(["arrow-color", "arrowcolor", "ac"], _DEFAULT_ARROW_COLOR),
    }

def _draw_error_diagram(k, error_text):
    # draw an "X"
    ax = plt.gca()
    x_values_1 = [0, 1]
    y_values_1 = [0, 1]
    x_values_2 = [0, 1]
    y_values_2 = [1, 0]

    # Plot the "X" shape on the provided axis
    ax.plot(x_values_1, y_values_1, color="blue", linewidth=2)
    ax.plot(x_values_2, y_values_2, color="blue", linewidth=2)

    # Add centered text
    ax.text(0.5, 0.5, "Error (" + ", ".join(error_text) + ")",
            ha='center', va='center',
            fontsize=12, color='red', weight='bold')

    title = str(k.name) if len(str(k.name)) > 0 else str(type(k).__name__)
    ax.set_title(str(title))

    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.5, 1.5)
    ax.set_aspect('equal')
    ax.axis("off")


def _check_diagram_drawability(k:PlanarDiagram):

    diagram_drawable = True
    error_text = []

    if bridges(k):
        warnings.warn(f"Diagram {to_knotpy_notation(k)} contains bridges (skipping)", UserWarning)
        error_text.append("bridge")
        diagram_drawable = False

    if loops(k):
        warnings.warn(f"Diagram {to_knotpy_notation(k)} contains loops (skipping)", UserWarning)
        error_text.append("loop")
        diagram_drawable = False

    if kinks(k):
        warnings.warn(f"Diagram {to_knotpy_notation(k)} contains kinks (skipping)", UserWarning)
        error_text.append("kink")
        diagram_drawable = False

    if leafs(k):
        warnings.warn(f"Diagram {to_knotpy_notation(k)} contains leafs (skipping)", UserWarning)
        error_text.append("leaf")
        diagram_drawable = False

    if cut_nodes(k):
        warnings.warn(f"Diagram {to_knotpy_notation(k)} contains cut-nodes (skipping)", UserWarning)
        error_text.append("cut-node")
        diagram_drawable = False

    return diagram_drawable, error_text

def draw(
    k: PlanarDiagram,
    draw_circles: bool = False,
    with_labels: bool = False,
    with_title: bool = False,
    ax = None,
    **style_kwargs
):
    """
    Draw the planar diagram using the Matplotlib library.

    :param k: A planar diagram to be drawn.
    :type k: PlanarDiagram
    :param draw_circles: Determines whether circles defining positions are drawn. Default is False.
    :param with_labels: Set to True for displaying node labels. Default is False.
    :param with_title: Set to True for displaying the diagram title. Default is False.
    :param style_kwargs: Additional keyword arguments for styling. Possible arguments are:
    node-size (default: 100), node-color (default: black), arc-width (default: 1), arc-color (default: black),
    gap-width (default: 1), arrow-length (default: 1), arrow-width (default: 1), arrow-flow (default: 1),
    arrow-color (default: black).
    :return: None
    """

    # Add "invisible" support arcs so the diagram has no bridges or cut-vertices.

    k = _add_support_arcs(k)

    diagram_drawable, error_text = _check_diagram_drawability(k)

    # compute the layout
    if diagram_drawable:
        try:
            circles = circlepack_layout(k)
            circles = canonically_rotate_layout(circles, 0)
            draw_from_layout(k, circles, draw_circles, with_labels, with_title, ax=ax, **style_kwargs)
        except ZeroDivisionError:
            warnings.warn(f"Diagram {to_knotpy_notation(k)} yields a zero division error (skipping)", UserWarning)
            error_text.append("zero division")
            diagram_drawable = False
        except KeyError:
            warnings.warn(f"Diagram {to_knotpy_notation(k)} yields a a key error (skipping)", UserWarning)
            error_text.append("key error")
            diagram_drawable = False


    if not diagram_drawable:
        _draw_error_diagram(k, error_text)


def export_png(k, filename, draw_circles=False, with_labels=False, with_title=False):
    try:
        plt.close()
    except:
        pass

    draw(k, draw_circles=draw_circles, with_labels=with_labels, with_title=with_title)
    plt.savefig(filename)


def export_pdf(diagrams, filename, draw_circles=False, with_labels=False, with_title=False, show_progress=True):
    """
    Draw the planar diagram(s) using Matplotlib and save to a PDF file.

    This function takes a planar diagram or a list of planar diagrams, draws
    them using Matplotlib, and exports the resulting visualizations to a PDF
    file. The drawing behavior can be customized using the optional parameters.
    If the diagrams contain unsupported features such as loops or bridges,
    they will be skipped, and a warning message will be generated. Progress
    indicators can be displayed if the export involves multiple diagrams.

    Parameters:
    diagrams: PlanarDiagram | list[PlanarDiagram]
        A planar diagram or a list of planar diagrams to be drawn.
    filename: str
        The name of the output PDF file where the drawings will be saved.
    draw_circles: bool, optional
        If True, circles will be drawn around the diagrams. Defaults to False.
    with_labels: bool, optional
        If True, labels will be displayed on the diagrams. Defaults to False.
    with_title: bool, optional
        If True, titles will be added to the diagrams. Defaults to False.
    show_progress: bool, optional
        If True, progress indicators will be displayed if the number of diagrams
        is 10 or more. Defaults to True.

    Returns:
    None
    """


    diagrams = [diagrams] if isinstance(diagrams, PlanarDiagram) else diagrams
    show_progress = show_progress and len(diagrams) >= 10

    if with_title:
        for k in diagrams:
            if k.name is None or len(str(k.name)) == 0:
                k.attr["_title"] = to_knotpy_notation(k)
            else:
                k.attr["_title"] = str(k.name)


    if plt.get_fignums():  # returns a list of open figure numbers
        plt.close()
    pdf = PdfPages(filename)

    for k in (Bar(diagrams, comment="exporting to PDF") if show_progress else diagrams):
        #
        # print()
        # print(k)



        draw(k,
             draw_circles=draw_circles,
             with_labels=with_labels,
             with_title=with_title)


        pdf.savefig(bbox_inches="tight", pad_inches=0)  # saves the current figure into a pdf page
        plt.close()

    # if author is not None:
    #     pdf.infodict()["Author"] = author
    pdf.close()


    if with_title:
        for k in diagrams:
            del k.attr["_title"]




def export_pdf_groups(groups, filename, draw_circles=False, with_labels=False, with_title=False, show_progress=True):
    """
    Draw the planar diagram(s) using Matplotlib and save to a PDF file.

    This function takes a planar diagram or a list of planar diagrams, draws
    them using Matplotlib, and exports the resulting visualizations to a PDF
    file. The drawing behavior can be customized using the optional parameters.
    If the diagrams contain unsupported features such as loops or bridges,
    they will be skipped, and a warning message will be generated. Progress
    indicators can be displayed if the export involves multiple diagrams.

    Parameters:
    diagrams: PlanarDiagram | list[PlanarDiagram]
        A planar diagram or a list of planar diagrams to be drawn.
    filename: str
        The name of the output PDF file where the drawings will be saved.
    draw_circles: bool, optional
        If True, circles will be drawn around the diagrams. Defaults to False.
    with_labels: bool, optional
        If True, labels will be displayed on the diagrams. Defaults to False.
    with_title: bool, optional
        If True, titles will be added to the diagrams. Defaults to False.
    show_progress: bool, optional
        If True, progress indicators will be displayed if the number of diagrams
        is 10 or more. Defaults to True.

    Returns:
    None
    """

    if not isinstance(groups, (list, set, tuple)):
        raise TypeError("groups must be a list")
    if not groups:
        return
    if not isinstance(groups[0], (list, set, tuple)):
        raise TypeError("groups must be a list of lists of diagrams")

    show_progress = show_progress and sum(len(g) for g in groups) >= 10

    if plt.get_fignums():  # returns a list of open figure numbers
        plt.close()

    pdf = PdfPages(filename)

    for group in (Bar(groups, comment="exporting to PDF") if show_progress else groups):
        n = len(group)
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
        fig, axes = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows))  # Adjust size per diagram
        axes = axes.flatten() if isinstance(axes, (list, np.ndarray)) else [axes]

        for k, ax in zip(group, axes):
            draw(k,
                 draw_circles=draw_circles,
                 with_labels=with_labels,
                 with_title=with_title,
                 ax=ax)

        plt.tight_layout(pad=0)
        pdf.savefig(bbox_inches="tight", pad_inches=0)  # saves the current figure into a pdf page
        plt.close()

    # if author is not None:
    #     pdf.infodict()["Author"] = author

    pdf.close()



if __name__ == '__main__':
    import knotpy as kp

    k = kp.from_knotpy_notation("a=V(b0 i2 j1) b=X(a0 j0 p0 i0) c=X(j2 l0 e0 k0) d=X(m1 n1 o1 p1) e=V(c2 l2 k1) f=X(h3 h2 g1 m0) g=X(n0 f2 h1 h0) h=X(g3 g2 f1 f0) i=V(b3 l1 a1) j=V(b1 a2 c0) k=V(c3 e2 o0) l=V(c1 i1 e1) m=V(f3 p2 n1) n=V(g0 m2 o1) o=V(k2 n2 p1) p=V(b2 o2 m1) ['name'='koko'; i:{'__support__'=True} j:{'__support__'=True} k:{'__support__'=True} l:{'__support__'=True} m:{'__support__'=True} n:{'__support__'=True} o:{'__support__'=True} p:{'__support__'=True}; a1:{'__support__'=True} a2:{'__support__'=True} e1:{'__support__'=True} e2:{'__support__'=True} i2:{'__support__'=True} j1:{'__support__'=True} k1:{'__support__'=True} l2:{'__support__'=True} m1:{'__support__'=True} m2:{'__support__'=True} n1:{'__support__'=True} n2:{'__support__'=True} o1:{'__support__'=True} o2:{'__support__'=True} p1:{'__support__'=True} p2:{'__support__'=True}]")
    print(k)
    print(kp.sanity_check(k))
    exit()# draw a knot
    k = kp.PlanarDiagram("10_12")
    #print(k)
    # draw(k)
    # plt.show()
    #
    k = kp.PlanarDiagram("t7_20")
    #print(k)
    # draw(k)
    # plt.show()

    # knotoid
    k = kp.from_knotpy_notation("a=V(c3) b=V(d1) c=X(d2 d0 d3 a0) d=X(c1 b0 c0 c2)")
    #print(k)
    # draw(k)
    # plt.show()
    #
    # knotoid
    k = kp.PlanarDiagram("h0_1")
    draw(k)
    plt.show()
