"""Draw a planar graph from a PlanarGraph object.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection, LineCollection, PolyCollection
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import to_rgb
from collections import defaultdict

from tqdm import tqdm
import math
import cmath

import knotpy as kp
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.spatialgraph import SpatialGraph
from knotpy.drawing.layout import circlepack_layout, bezier
from knotpy.algorithms.structure import loops, bridges
from knotpy.utils.geometry import Circle, CircularArc, Line, Segment
from knotpy.utils.geometry import (perpendicular_arc, is_angle_between, antipode, tangent_line, middle, bisector, bisect, split,
                                   perpendicular_arc_through_point, BoundingBox)

from knotpy.notation.native import from_knotpy_notation
from knotpy.notation import to_pd_notation
from knotpy.classes.endpoint import IngoingEndpoint, Endpoint

from knotpy.classes.node import Vertex, Crossing, Bond
from knotpy.manipulation.phantom import is_node_phantom


__all__ = ['draw', 'export_pdf', "circlepack_layout", "draw_from_layout"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'



# default plotting properties
# node
DEFAULT_NODE_SIZE = 0.2
DEFAULT_NODE_COLOR = "black"
PHANTOM_NODE_COLOR = "gray"
PHANTOM_NODE_ALPHA = 0.5

BONDED_NODE_COLOR = "black"
# arcs
DEFAULT_LINE_WIDTH = 3.5
DEFAULT_LINE_COLOR = "steelblue"
DEFAULT_BRAKE_WIDTH = 0.15  # arc break marking the under-passing
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

        if is_node_phantom(k, node):
            # PHANTOM NODE
            circle_patch = plt.Circle(xy, DEFAULT_NODE_SIZE / 2, color=PHANTOM_NODE_COLOR, zorder=3)
            ax.add_patch(circle_patch)
        else:
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
        if "__BOND__" in key:
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


def _plot_arc(k, circles):
    """The middle "arc" part that is a path through the arc circle and starts and ends on the intersection of the arc
    circle and the adjacent tangent node circles.
    :param k:
    :param circles:
    :return:
    """
    result_curves = []
    for arc in k.arcs.keys():
        ep0, ep1 = arc
        # compute the arc that is perpendicular to the arc circle
        g_arc = perpendicular_arc(circles[arc], circles[ep0.node], circles[ep1.node])
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


def _plot_endpoint(k: PlanarDiagram, circles: dict, arc, ep: Endpoint, gap=False, arrow=False):
    """ Plot the node endpoint presented by the arc. Also plot arrows, gaps, etc.
    :param k: planar diagram
    :param circles: circle-packing
    :param arc: the geometric arc to draw
    :param ep: endpoint to draw
    :return:
    """
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
            gap_angle = DEFAULT_BRAKE_WIDTH / arc.radius  # circular arc length is s = theta * radius
            arrow_angle = ARROW_LENGTH / arc.radius  # circular arc length is s = theta * radius
            if arc.length() > DEFAULT_BRAKE_WIDTH:
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
        return_curves.append((seg, color))
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
    result_curves = []

    for v in k.nodes:
        node = k.nodes[v]
        arcs = k.arcs[v]
        endpoints = k.endpoints[v]
        colors = [to_color(k.nodes[ep].get("color", DEFAULT_LINE_COLOR)) for ep in endpoints]
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
                color = to_color(k.nodes[ep0].get("color", DEFAULT_LINE_COLOR))  # assume 1st endpoint is at vertex
                int_point = circles[arc] * circles[v]  # intersection point
                int_point = int_point[0]

                result_curves.append((Segment(int_point, circles[v].center), color))


        elif isinstance(node, Crossing):
            """Connect crossing endpoints. Plot two circular arcs from the crossing to the endpoint. The over-arc is a single
            circular arc, the under-arc splits into two sub-arcs, the gap represents the arc break emphasizing that the 
            under-arc travels below the over-arc."""

            # get circular arcs
            over_arc = perpendicular_arc(circles[v], circles[arcs[1]], circles[arcs[3]], over_order := [])
            under_arc = perpendicular_arc(circles[v], circles[arcs[0]], circles[arcs[2]], under_order := [])
            #print("OO", over_arc, under_arc)
            point = (over_arc * under_arc)
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
    new_vertices = dict()  # coordinates of vertices given by intersections

    # draw middle arc
    curves += _plot_arc(k, circles)

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

    # if save_to_file is not None:
    #     #DPI = fig.get_dpi()
    #     #fig.set_size_inches(512.0 / float(DPI), 512.0 / float(DPI))
    #
    #     plt.savefig(save_to_file, bbox_inches='tight')
    # else:
    #     plt.show()

    # plt.close(fig)


def draw(k, draw_circles=True, with_labels=False, with_title=False):
    """Draw the planar diagram k using Matplotlib.
    :param k: A planar diagram
    :param draw_circles: draw the circle that define the positions of node, arcs, and areas/faces
    :param with_labels: set True to draw node labels
    :param with_title: set True to draw diagram title
    :return:
    """
    #print()
    #print("Drawing graph", g)

    if bridges(k) or loops(k):
        print(f"Skipping drawing {k}, since drawing loops or bridges in not yet supported.")

    # compute the layout
    circles = circlepack_layout(k)

    draw_from_layout(k, circles, draw_circles, with_labels, with_title)

def export_pdf(k, filename, draw_circles=True, with_labels=False, with_title=False, author=None):
    """Draw the planar diagram(s) k using Matplotlib and save to pdf.
    :param k: the planar diagram or a list of planar diagrams
    :param filename: pdf name
    :param author: add pdf author information
    :return:
    """

    #print(k)

    pdf = PdfPages(filename)
    warnings = []
    k = [k] if isinstance(k, PlanarDiagram) else k
    for pd in (tqdm(k, desc="Exporting to pdf", unit="diagrams") if len(k) >= 5 else k):
        #print("exporting", pd)
        #print("Exporting", to_pd_notation(pd))
        if bridges(pd) or loops(pd):
            warnings.append(f"Skipped drawing {pd}, since drawing loops or bridges in not yet supported.")
            continue
        draw(pd,
             draw_circles=draw_circles,
             with_labels=with_labels,
             with_title=with_title)
        #plt.show()
        pdf.savefig(bbox_inches="tight", pad_inches=0)  # saves the current figure into a pdf page
        plt.close()

    if author is not None:
        pdf.infodict()["Author"] = author

    pdf.close()

    print("\n".join(warnings))




if __name__ == '__main__':
    """
    
    
    "('OrientedSpatialGraph', {'name': 't0_1(0).0'}, 
    [('Vertex', 'a', (('OutgoingEndpoint', 'b', 0, {'color': 1}), ('OutgoingEndpoint', 'b', 2, {}), ('OutgoingEndpoint', 'b', 1, {})), {}), 
    ('Vertex', 'b', (('IngoingEndpoint', 'a', 0, {'color': 1}), ('IngoingEndpoint', 'a', 2, {}), ('IngoingEndpoint', 'a', 1, {})), {})])"



"""

    import matplotlib.pyplot as plt
    #s = "('OrientedSpatialGraph', {'name': '+t3_1#-3_1(1).2'}, [('Vertex', 'a', (('IngoingEndpoint', 'c', 2, {}), ('OutgoingEndpoint', 'b', 1, {'color': 1}), ('OutgoingEndpoint', 'd', 0, {})), {}), ('Vertex', 'b', (('IngoingEndpoint', 'd', 1, {}), ('IngoingEndpoint', 'a', 1, {'color': 1}), ('OutgoingEndpoint', 'g', 0, {})), {}), ('Crossing', 'c', (('IngoingEndpoint', 'f', 3, {}), ('IngoingEndpoint', 'f', 2, {}), ('OutgoingEndpoint', 'a', 0, {}), ('OutgoingEndpoint', 'e', 0, {})), {}), ('Crossing', 'd', (('IngoingEndpoint', 'a', 2, {}), ('OutgoingEndpoint', 'b', 0, {}), ('OutgoingEndpoint', 'g', 3, {}), ('IngoingEndpoint', 'h', 2, {})), {}), ('Crossing', 'e', (('IngoingEndpoint', 'c', 3, {}), ('IngoingEndpoint', 'h', 1, {}), ('OutgoingEndpoint', 'f', 1, {}), ('OutgoingEndpoint', 'f', 0, {})), {}), ('Crossing', 'f', (('IngoingEndpoint', 'e', 3, {}), ('IngoingEndpoint', 'e', 2, {}), ('OutgoingEndpoint', 'c', 1, {}), ('OutgoingEndpoint', 'c', 0, {})), {}), ('Crossing', 'g', (('IngoingEndpoint', 'b', 2, {}), ('OutgoingEndpoint', 'h', 0, {}), ('OutgoingEndpoint', 'h', 3, {}), ('IngoingEndpoint', 'd', 2, {})), {}), ('Crossing', 'h', (('IngoingEndpoint', 'g', 1, {}), ('OutgoingEndpoint', 'e', 1, {}), ('OutgoingEndpoint', 'd', 3, {}), ('IngoingEndpoint', 'g', 2, {})), {})])"
    #s = "('SpatialGraph', {'name': 't0_1(1)'}, [('Vertex', 'a', (('Endpoint', 'b', 0, {}), ('Endpoint', 'b', 2, {'color': 1}), ('Endpoint', 'b', 1, {})), {}), ('Vertex', 'b', (('Endpoint', 'a', 0, {}), ('Endpoint', 'a', 2, {}), ('Endpoint', 'a', 1, {'color': 1})), {})])"
    s = "('OrientedSpatialGraph', {'name': 't0_1(0).0'}, [('Vertex', 'a', (('OutgoingEndpoint', 'b', 0, {'color': 1}), ('OutgoingEndpoint', 'b', 2, {}), ('OutgoingEndpoint', 'b', 1, {})), {}), ('Vertex', 'b', (('IngoingEndpoint', 'a', 0, {'color': 1}), ('IngoingEndpoint', 'a', 2, {}), ('IngoingEndpoint', 'a', 1, {})), {})])"
    k = from_knotpy_notation(s)
    # print(k)
    # k.permute_node("a", {0:1,1:2,2:0})
    # print(k)
    # exit()

    draw(k, draw_circles=True, with_labels=True, with_title=True)

    plt.show()

    from knotpy.manipulation.phantom import insert_phantom_node
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
