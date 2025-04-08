"""Draw a planar graph from a PlanarGraph object.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection, LineCollection, PolyCollection
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import to_rgb
from collections import defaultdict


import math

from knotpy.classes.planardiagram import PlanarDiagram

from knotpy.drawing.layout import circlepack_layout, bezier
from knotpy import bridges, loops
from knotpy.utils.geometry import Circle, CircularArc, Line, Segment
from knotpy.utils.geometry import (perpendicular_arc, is_angle_between, antipode, tangent_line, middle, bisector, bisect, split,
                                   perpendicular_arc_through_point, BoundingBox, weighted_circle_center_mean)

from knotpy.classes.endpoint import IngoingEndpoint, Endpoint

from knotpy.classes.node import Vertex, Crossing #, Bond
from knotpy.algorithms.topology import bridges
from knotpy.manipulation.insert import insert_arc
from knotpy.utils.multiprogressbar import Bar
from knotpy.manipulation.subdivide import subdivide_arc, subdivide_endpoint

__all__ = ['draw', 'export_pdf', "circlepack_layout", "draw_from_layout", "add_support_arcs", "plt", "export_png"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'



# default plotting properties
# default plotting properties
# node
DEFAULT_NODE_SIZE = 0.1
DEFAULT_NODE_COLOR = "black"
PHANTOM_NODE_COLOR = "gray"
PHANTOM_NODE_ALPHA = 0.5

BONDED_NODE_COLOR = "black"
# arcs
DEFAULT_LINE_WIDTH = 0.5
DEFAULT_LINE_COLOR = "steelblue"
DEFAULT_GAP_WIDTH = 0.08  # arc break marking the under-passing
# text
DEFAULT_TEXT_COLOR = "black"
DEFAULT_FONT_SIZE = 16
DEFAULT_FONT_SIZE_PIXELS = DEFAULT_FONT_SIZE * 72 / 100 / 100  # default 100 DPI
# circles
DEFAULT_CIRCLE_ALPHA = 0.15
DEFAULT_CIRCLE_COLOR = "cadetblue"
# edge colors
EDGE_COLORS = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray',
               'tab:olive', 'tab:cyan']

DEFAULT_BOND_COLOR = "black"

# arrows
ARROW_LENGTH = 0.25
ARROW_WIDTH = 0.25
ARROW_FLOW = 0.5  # arrow slant so it appears more natural, 0 = tangent
DEFAULT_ARROW_COLOR = DEFAULT_LINE_COLOR


class Arrow:
    """Class representing a graphical arrow"""
    def __init__(self, pointy_end: complex, direction: complex):
        """
        :param pointy_end: the position of the pointy end of the arrow (end point)
        :param direction: direction of arrow from start point to end point
        """
        self.point = pointy_end
        self.direction = direction / abs(direction)

    def triangle(self):
        point0 = self.point
        point_ = self.point - self.direction * ARROW_LENGTH
        point1 = point_ + 1j * self.direction * 0.5 * ARROW_WIDTH
        point2 = point_ - 1j * self.direction * 0.5 * ARROW_WIDTH
        return [(point0.real, point0.imag), (point1.real, point1.imag), (point2.real, point2.imag)]


def to_color(item):
    return EDGE_COLORS[item % len(EDGE_COLORS)] if isinstance(item, int) else item


def average_color(color1, color2):
    rgb1, rgb2 = to_rgb(to_color(color1)), to_rgb(to_color(color2))
    return (rgb1[0] + rgb2[0])/2, (rgb1[1] + rgb2[1])/2, (rgb1[2] + rgb2[2])/2



def add_support_arcs(k: PlanarDiagram):
    """ Ads support arcs so there are no bridges in the diagram. For every bridge, add two parallel arcs. In the case
    the bridge is a leaf, add two adjacent arcs to the leaf.

    :param k:
    :return:
    """

    k = k.copy()
    is_oriented = k.is_oriented()

    #print(k)
    for bridge in bridges(k):
        # the bridge from node a to node b
        #print("  ", bridge)
        endpoint_a, endpoint_b = bridge
        node_a, pos_a = endpoint_a
        node_b, pos_b = endpoint_b
        deg_a = k.degree(node_a)
        deg_b = k.degree(node_b)
        if deg_a == 2 or deg_b == 2:
            raise NotImplementedError("Support arcs for degree-2 vertices not supported")

        if deg_a == 1 and deg_b == 1:
            # just a line
            k.set_endpoint((node_a, 1), (node_b,2),  __support__=True)
            k.set_endpoint((node_a, 2), (node_b,1),  __support__=True)
            k.set_endpoint((node_b, 1), (node_a,2),  __support__=True)
            k.set_endpoint((node_b, 2), (node_a,1),  __support__=True)
            return k
            #raise NotImplementedError("Support arcs for two degree-1 vertices not supported")

        # Looking from node a, one parallel arc if considered "right" and the other one "left.

        if k.degree(node_a) == 1:
            # we have a leaf/knotoid terminal at node a, do not create a parallel arc to the bridge, but two adjacent arcs
            node_a_right = node_a_left = node_a
            pos_a_right, pos_a_left = 1, 2
        else:
            # add two parallel endpoints (right and left)
            node_a_right = subdivide_endpoint(k, (node_a, (pos_a + 1) % 4))
            node_a_left = subdivide_endpoint(k, (node_a, (pos_a - 1) % 4))
            pos_a_right = 1 if k.nodes[node_a_right][0].node == node_a else 2
            pos_a_left = 2 if k.nodes[node_a_right][0].node == node_a else 1

            k.nodes[node_a_right].attr["__support__"] = True
            k.nodes[node_a_left].attr["__support__"] = True

        if k.degree(node_b) == 1:
            # we have a leaf/knotoid terminal at node a
            node_b_right = node_b_left = node_b
            pos_b_right, pos_b_left = 2, 1
        else:
            node_b_right = subdivide_endpoint(k, (node_b, (pos_b - 1) % 4))
            node_b_left = subdivide_endpoint(k, (node_b, (pos_b + 1) % 4))
            pos_b_right = 2 if k.nodes[node_b_right][0].node == node_b else 1
            pos_b_left = 1 if k.nodes[node_b_right][0].node == node_b else 2

            k.nodes[node_b_right].attr["__support__"] = True
            k.nodes[node_b_left].attr["__support__"] = True

        if k.degree(node_a) == 1:
            # if pos_a_right <  pos_a_left, first insert the smaller one, otherwise indices will not make sense
            insert_arc(k, ((node_a_right, pos_a_right), (node_b_right, pos_b_right)))
            insert_arc(k, ((node_a_left, pos_a_left), (node_b_left, pos_b_left)))
        else:
            insert_arc(k, ((node_a_left, pos_a_left), (node_b_left, pos_b_left)))
            insert_arc(k, ((node_a_right, pos_a_right), (node_b_right, pos_b_right)))

    return k

def _plot_vertices(k, circles, with_labels, ax):
    """Plot vertices as points or circles with label
    :param k: planar graph
    :param circles: dictionary containing vertices as keys and (position, radius) as value
    :param with_labels: set True to draw node labels
    :param ax: pyplot axis
    :return:
    """

    vertices = k.vertices if hasattr(k, "vertices") else []


    for node in vertices:
        circle = circles[node]
        xy = (circle.center.real, circle.center.imag) if isinstance(circle, Circle) else (circle.real, circle.imag)

        if not _visible(k.nodes[node]):
            continue

        # if is_node_phantom(k, node):
        #     # PHANTOM NODE
        #     circle_patch = plt.Circle(xy, DEFAULT_NODE_SIZE / 2, color=PHANTOM_NODE_COLOR, zorder=3)
        #     ax.add_patch(circle_patch)
        # NORMAL NODE
        if with_labels:
            circle_patch_out = plt.Circle(xy, DEFAULT_FONT_SIZE_PIXELS * 1.3 + DEFAULT_LINE_WIDTH / 100 * 1.5,
                                          color=k.nodes[node].attr.get("color", DEFAULT_NODE_COLOR), zorder=2)
            circle_patch_in = plt.Circle(xy, DEFAULT_FONT_SIZE_PIXELS * 1.3,
                                         color="white", zorder=3)
            ax.add_patch(circle_patch_out)
            ax.add_patch(circle_patch_in)
            ax.text(*xy,
                    s=str(node),
                    ha="center",
                    va="center",
                    fontsize=DEFAULT_FONT_SIZE,
                    color=DEFAULT_TEXT_COLOR,
                    zorder=4)
        else:
            color = k.nodes[node].attr.get("color", DEFAULT_NODE_COLOR)
            circle_patch = plt.Circle(xy, DEFAULT_NODE_SIZE / 2, color=color, zorder=3)
            ax.add_patch(circle_patch)

    # BOND NODES
    for key in circles:
        if isinstance(key, str) and "__BOND__" in key:
            # BONDED NODE

            value = circles[key]
            xy = (value.real, value.imag)
            circle_patch = plt.Circle(xy, DEFAULT_NODE_SIZE / 2 * 0.67, color=BONDED_NODE_COLOR, zorder=3)
            ax.add_patch(circle_patch)



def _plot_circles(circles, ax):
    """Plot circles obtained by the circle packing theorem to draw the diagram.
    :param circles:  dictionary containing vertices/edges/areas as keys and (position, radius) as value
    :param ax: pyplot axis
    :return:
    """
    #TODO: plot all at once
    # plot circles
    for circle in circles.values():
        circle_patch = plt.Circle((circle.center.real, circle.center.imag), circle.radius,
                                  alpha=DEFAULT_CIRCLE_ALPHA,
                                  facecolor=DEFAULT_CIRCLE_COLOR,
                                  ls="none")
        ax.add_patch(circle_patch)


def _plot_middle_arc(k, circles):
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
        color1 = k.nodes[ep0].get("color", DEFAULT_LINE_COLOR)
        color2 = k.nodes[ep1].get("color", DEFAULT_LINE_COLOR)
        if color1 != color2:
            print("Warning: different colored twin edges not yet supported.")
        color = average_color(color1, color2)

        # TODO: if endpoints are different color, split arcs in half using the bisect() method
        result_curves.append((g_arc, color))
    return result_curves


def _vertex_endpoints_colors(k, v):
    # return a list of colors of endpoints of v in order
    return [to_color(k.nodes[ep].get("color", DEFAULT_LINE_COLOR)) for ep in k.endpoints[v]]


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

    #print(ep, ep.attr)
    if not _visible(ep):
        return []
    return_curves = []
    color = to_color(ep.get("color", DEFAULT_LINE_COLOR))

    # get the two endpoints od the arc
    pt0 = arc(arc.theta1) if isinstance(arc, CircularArc) else arc(0)
    pt1 = arc(arc.theta2) if isinstance(arc, CircularArc) else arc(1)
    # which arc endpoint is the one at the vertex/crossing, 0 or 1?
    node_pt = 0 if abs(circles[ep.node].center - pt0) < abs(circles[ep.node].center - pt1) else pt1

    if isinstance(arc, CircularArc):
        if not gap:
            return_curves.append((arc, color))
            arrow_angle = ARROW_LENGTH / arc.radius  # circular arc length is s = theta * radius
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

            gap_angle = DEFAULT_GAP_WIDTH / arc.radius  # circular arc length is s = theta * radius
            arrow_angle = ARROW_LENGTH / arc.radius  # circular arc length is s = theta * radius
            if arc.length() > DEFAULT_GAP_WIDTH:
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
            gap_t = DEFAULT_GAP_WIDTH / seg.length()
            if node_pt == 0:
                return_curves.append((seg(gap_t, 1), color))
            else:
                return_curves.append((seg(0, 1-gap_t), color))

        if arrow and isinstance(ep, IngoingEndpoint):
            arrow_t = ARROW_WIDTH / seg.length()
            if node_pt == 0:
                a = Arrow(arc(0), arc(0) - arc(arrow_t))
                return_curves.append((a, color))
            else:
                a = Arrow(arc(1), arc(1) - arc(1-arrow_t))
                return_curves.append((a, color))


    else:
        raise TypeError(f"Arc {arc} is of type {type(arc)}, but should be of type CircularArc or Segment")

    return return_curves


def _plot_all_endpoints(k, circles, new_vertices: dict):

    approximate = False

    result_curves = []

    for v in k.nodes:
        node = k.nodes[v]
        arcs = k.arcs[v]
        endpoints = k.endpoints[v]
        colors = [to_color(k.nodes[ep].get("color", DEFAULT_LINE_COLOR)) if _visible(ep) else None for ep in endpoints]
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
            # print(k)
            # print(circles)
            # print(diff_arc)
            # print(ep_b)
            # print()


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

                color = to_color(k.nodes[ep0].get("color", DEFAULT_LINE_COLOR))  # assume 1st endpoint is at vertex
                int_point = circles[arc] * circles[v]  # intersection point
                int_point = int_point[0]

                result_curves.append((Segment(int_point, circles[v].center), color if _visible(ep0) else "red"))


        elif isinstance(node, Crossing):
            """Connect crossing endpoints. Plot two circular arcs from the crossing to the endpoint. The over-arc is a single
            circular arc, the under-arc splits into two sub-arcs, the gap represents the arc break emphasizing that the 
            under-arc travels below the over-arc."""

            # get circular arcs
            over_arc = perpendicular_arc(circles[v], circles[arcs[1]], circles[arcs[3]], over_order := [], approx=approximate)
            under_arc = perpendicular_arc(circles[v], circles[arcs[0]], circles[arcs[2]], under_order := [], approx=approximate)
            #print("OO", over_arc, under_arc)


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
                                      lw=DEFAULT_LINE_WIDTH,
                                      edgecolor=arc_colors,
                                      ))

    ax.add_collection(LineCollection(segments,
                                      facecolor='none',
                                      lw=DEFAULT_LINE_WIDTH,
                                      edgecolor=segment_colors,
                                      ))

    # Create a PolyCollection with the triangles
    # print(arrows)
    # for a in arrows:
    #     print("  ",a)
    #     print("    ", a.points())
    # print([a.points() for a in arrows])

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


    #

    #print("Principal Components:")
    #print(conjugated_principal_components, abs(conjugated_principal_components[0]), abs(conjugated_principal_components[1]))
    #print("Explained Variance:")
    #print(explained_variance)


# def canonically_rotate_layout(layout, PCA_degrees=0):
#     """
#
#     :param layout:
#     :param PCA_degrees: https://en.wikipedia.org/wiki/Principal_component_analysis
#     :return:
#     """
#     centers = [circle.center for circle in layout.values()]
#     radii = [circle.radius for circle in layout.values()]
#
#     mass_center = sum(c * r for c, r in zip(centers, radii)) / sum(radii)
#     centers = [c - mass_center for c in centers]
#     centers = aligned_centers = compute_PCA(centers)
#     # rotate centers
#     rotation = complex(math.cos(math.radians(PCA_degrees)), math.sin(math.radians(PCA_degrees)))
#     centers = [c * rotation for c in centers]
#     return {key: Circle(c, r) for key, c, r in zip(layout, centers, radii)}


def draw_from_layout(k,
                     layout,
                     draw_circles=True,
                     with_labels=False,
                     with_title=False,
                     ax=None):
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
        title = str(k.name) if len(str(k.name)) > 0 else str(type(k).__name__)
        ax.set_title(str(title))


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


def draw(k, draw_circles=False, with_labels=False, with_title=False):
    """Draw the planar diagram k using Matplotlib.
    :param k: A planar diagram
    :param draw_circles: draw the circle that define the positions of node, arcs, and areas/faces
    :param with_labels: set True to draw node labels
    :param with_title: set True to draw diagram title
    :return:
    """
    #print()
    #print("Drawing graph", g)
    #print(3)
    error = False
    if bridges(k):
        # print("*", k)
        # print("_", to_pd_notation(k))
        k = add_support_arcs(k)
    #print(4)
    if bridges(k) or loops(k):
        print(f"Skipping drawing {k}, since drawing loops or bridges in not yet supported.")
        error = True
        return

    # compute the layout
    try:
        circles = circlepack_layout(k)
        #circles = canonically_rotate_layout(circles, 0)
    except ZeroDivisionError:
        print(f"Skipping drawing {k}, since drawing loops or bridges in not yet supported.")
        error = True

    #print(5)
    if not error:
        draw_from_layout(k, circles, draw_circles, with_labels, with_title)
    else:
        ax = plt.gca()
        x_values_1 = [0, 1]
        y_values_1 = [0, 1]
        x_values_2 = [0, 1]
        y_values_2 = [1, 0]

        # Plot the "X" shape on the provided axis
        ax.plot(x_values_1, y_values_1, color="blue", linewidth=2)
        ax.plot(x_values_2, y_values_2, color="blue", linewidth=2)
        ax.set_xlim(-0.5, 1.5)
        ax.set_ylim(-0.5, 1.5)
        ax.set_aspect('equal')
        ax.axis("off")



def export_png(k, filename, draw_circles=False, with_labels=False, with_title=False):
    try:
        plt.close()
    except:
        pass

    draw(k, draw_circles=draw_circles, with_labels=with_labels, with_title=with_title)
    plt.savefig(filename)

def export_pdf(k, filename, draw_circles=False, with_labels=False, with_title=False, author=None, show_progress=True):
    """Draw the planar diagram(s) k using Matplotlib and save to pdf.
    :param k: the planar diagram or a list of planar diagrams
    :param filename: pdf name
    :param author: add pdf author information
    :param show_progress:
    :return:
    """
    plt.close()


    pdf = PdfPages(filename)
    warnings = []
    k = [k] if isinstance(k, PlanarDiagram) else k
    for pd in (Bar(k, comment="exporting to pdf") if len(k) >= 5 else k):

        # print(pd)
        # print(kp.to_pd_notation(pd))
        if loops(pd):
            warnings.append(f"Skipped drawing {pd}, since drawing loops or bridges in not yet supported.")
            continue

        draw(pd,
             draw_circles=draw_circles,
             with_labels=with_labels,
             with_title=with_title)

        pdf.savefig(bbox_inches="tight", pad_inches=0)  # saves the current figure into a pdf page
        plt.close()


    if author is not None:
        pdf.infodict()["Author"] = author

    pdf.close()
    if warnings:
        print("\n".join(warnings))




if __name__ == '__main__':

    from knotpy import from_pd_notation
    import random


    # EXAMPLE: draw non-perfect layout
    s = "[[1,13,2,12],[3,9,4,8],[5,1,6,14],[7,10,8,11],[9,3,10,2],[11,6,12,7],[13,5,14,4]]"
    k = from_pd_notation(s)
    print(k)

    # case 1: draw from perfect
    # draw(k, draw_circles=True)

    # case 2: draw from non-perfect
    l = circlepack_layout(k)
    # pertube the circles
    for key, circle in l.items():
        l[key] = Circle(center=circle.center, radius=circle.radius * (1-random.uniform(-0.3, 0.3)))
    # try to draw from the approximate layout (circles do not touch, circles overlap)
    draw_from_layout(k, l, draw_circles=True)
    kp.plt.show()
    exit()


    """
    
    
    "('OrientedSpatialGraph', {'name': 't0_1(0).0'}, 
    [('Vertex', 'a', (('OutgoingEndpoint', 'b', 0, {'color': 1}), ('OutgoingEndpoint', 'b', 2, {}), ('OutgoingEndpoint', 'b', 1, {})), {}), 
    ('Vertex', 'b', (('IngoingEndpoint', 'a', 0, {'color': 1}), ('IngoingEndpoint', 'a', 2, {}), ('IngoingEndpoint', 'a', 1, {})), {})])"



"""

    import matplotlib.pyplot as plt
    s = "V[0,1,2],V[3,4,5],X[6,0,7,8],X[8,9,3,10],X[1,6,10,5],X[9,7,11,12],X[12,11,2,4]"
    s = "V[0,1,2],V[3,4,5],X[5,2,6,7],X[1,8,9,6],X[10,8,11,12],X[12,11,0,4],X[13,14,7,9],X[14,13,10,3]"
    s = "V[0,1,2],V[3,4,5],X[6,7,8,9],X[10,11,12,13],X[4,11,2,7],X[13,12,14,15],X[16,0,10,17],X[1,16,18,8],X[5,6,9,18],X[15,14,3,17]"
    #s = "V[0,1,2],V[3,4,5],X[2,6,7,8],X[9,4,10,7],X[5,11,12,1],X[11,9,6,12],X[13,14,3,0],X[8,10,14,13]"
    k = from_pd_notation(s)
    t= time()
    draw(k, draw_circles=True, with_labels=True, with_title=True)
    print("Time:", time()- t)
    plt.show()
    exit()

    from knotpy.reidemeister.phantom import insert_phantom_node
    arcs = list(k.arcs)
    insert_phantom_node(k, arcs[0])
    print(k)
    draw(k, draw_circles=True, with_labels=True, with_title=True)

    plt.show()
    exit()
    #k = kp.from_pd_notation("X[3,1,0,0],X[2,1,3,2]", create_using=SpatialGraph)
    #k = kp.from_pd_notation("V[0,2],V[1,0],X[6,2,3,5],V[5,4,6],V[1,4,3]", create_using=SpatialGraph)

    # draw(k, draw_circles=True, with_labels=True, with_title=True)
    # plt.show()
    codes = ["V[0,1,2],V[3,4,5],X[6,0,7,8],X[8,9,3,10],X[1,6,10,5],X[9,7,11,12],X[12,11,2,4]"]
    codes = ["V[0,1,2],V[3,4,1],X[2,4,5,6],X[7,8,9,5],X[8,10,6,9],X[3,0,10,7]"]
    codes = ["V[0,1,2],V[3,4,5],X[5,2,6,7],X[1,8,9,6],X[10,8,11,12],X[12,11,0,4],X[13,14,7,9],X[14,13,10,3]"]
    codes = ["V[0,1,2],V[3,4,5],X[6,7,8,9],X[10,11,12,13],X[4,11,2,7],X[13,12,14,15],X[16,0,10,17],X[1,16,18,8],X[5,6,9,18],X[15,14,3,17]"]
    codes = ["V[0,1,2],V[3,4,5],X[2,6,7,8],X[9,4,10,7],X[5,11,12,1],X[11,9,6,12],X[13,14,3,0],X[8,10,14,13]"]



    thetas = [kp.from_pd_notation(code, create_using=SpatialGraph) for code in codes]
    for k in thetas:

        print("Drawing", k)
        print("verts", k.vertices)
        print("crossings", k.crossings)
        draw(k, draw_circles=True, with_labels=True, with_title=True)
        plt.show()

    #export_pdf(graphs,"slike.pdf", draw_circles=True, with_labels=True, with_title=True)
