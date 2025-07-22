import math
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Polygon
from matplotlib.lines import Line2D

from knotpy.classes.endpoint import IngoingEndpoint
from knotpy.algorithms.disjoint_union import disjoint_union, disjoint_union_decomposition
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.drawing.layout_circle_packing import layout_circle_packing
from knotpy.utils.geometry import CircularArc, Segment, middle
from knotpy.drawing.alignment import align_layouts
from knotpy.drawing._support import _add_support_arcs
from knotpy.algorithms.connected_sum import connected_sum

"""
TODO:
- bridges
- loops
- nicer connected sums
- with support labels are wrong
- two adjacent leafs (a=V(b0) b=X(a0 c3 c0 d0) c=X(b2 e3 f0 b1) d=V(b3) e=X(f3 g3 h0 c1) f=X(c2 h3 g0 e0) g=X(f2 h2 h1 e1) h=X(e2 g2 g1 f1))

this case:
    # s = kp.from_knotpy_notation("a → X(b3 b2 c3 c2), b → X(d3 e0 a1 a0), c → X(e3 d0 a3 a2), d → X(c1 f3 g0 b0), e → X(b1 g3 h0 c0), f → X(i0 j0 k0 d1), g → X(d2 k3 k2 e1), h → X(e2 l0 l3 j2), i → X(f0 i2 i1 j1), j → X(f1 i3 h3 l2), k → X(f2 l1 g2 g1), l → X(h1 k1 j3 h2)")

"""


__all__ = ['draw']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

_DEFAULT_ARC_COLOR = "tab:blue"  # knot strand color
_DEFAULT_ARC_WIDTH = 4.0  # knot strand width
_DEFAULT_GAP_WIDTH = 0.1   # arc break gap the under-passing

_DEFAULT_VERTEX_SIZE = 0.1
_DEFAULT_VERTEX_COLOR = "black"

_DEFAULT_TEXT_COLOR = "black"
_DEFAULT_FONT_SIZE = 14

_ARROW_LENGTH = 0.15
_ARROW_WIDTH = 0.15
#_ARROW_FLOW = 0.5  # arrow slant so it appears more natural, 0 = tangent
_DEFAULT_ARROW_COLOR = _DEFAULT_ARC_COLOR
_DEFAULT_ARROW_POSITION = "middle"  # options: "middle"
_DEFAULT_ARROW_STYLE = "open"  # options: "open", "closed"

_PLOT_CIRCLES = True  # mostly for debugging

# Drawing order (stacking order) of plot elements, lower z-order values are drawn first.
_Z_CIRCLES = 0
_Z_ARC = 1
_Z_ENDPOINT = 1
_Z_ARROW = 2
_Z_VERTEX = 3
_Z_TEXT = 4


def draw_arcs(k: PlanarDiagram | OrientedPlanarDiagram, layout:dict, arcs_to_draw: None | list=None, ax=None):
    """
    Draws the circular arcs and segments of a diagram
    Args:
        k (PlanarDiagram | OrientedPlanarDiagram): The diagram whose arcs are drawn.
        layout (dict): A layout map where keys are arcs and values are the respective graphical
            elements (e.g., `CircularArc` or `Segment`) describing the visualization.
        arcs_to_draw (None | list, optional): List of arcs to be drawn. If None, defaults to all arcs in
            the diagram `k`.
        ax (matplotlib.axes.Axes, optional): The matplotlib axis to which the arcs and segments are
            drawn. If None, the current axis is used.
    """

    if ax is None:
        ax = plt.gca()

    if arcs_to_draw is None:
        arcs_to_draw = list(k.arcs)

    for arc in arcs_to_draw:
        element = layout[arc]
        if isinstance(element, CircularArc):

            ax.add_patch(
                Arc(xy=(element.center.real, element.center.imag),
                    width=2 * element.radius,
                    height=2 * element.radius,
                    theta1=math.degrees(element.theta1),
                    theta2=math.degrees(element.theta2),
                    color=_DEFAULT_ARC_COLOR,
                    linewidth=_DEFAULT_ARC_WIDTH,
                    zorder=_Z_ARC
                    )
            )

        elif isinstance(element, Segment):
            ax.add_line(
                Line2D((element.A.real, element.B.real), (element.A.imag, element.B.imag),
                       color=_DEFAULT_ARC_COLOR,
                       linewidth=_DEFAULT_ARC_WIDTH,
                       zorder=_Z_ARC)
            )

def _is_start(element, point):
    # On which side is the point (start or end of the element?)
    if isinstance(element, CircularArc):
        return abs(element(element.theta1) - point) < abs(element(element.theta2) - point)
    if isinstance(element, Segment):
        return abs(element(element.A) - point) < abs(element(element.B) - point)

    raise ValueError(f"Unsupported element type: {type(element)}")

def draw_endpoints(k: PlanarDiagram | OrientedPlanarDiagram,
                   layout:dict,
                   endpoints_to_draw: None | list=None,
                   gap=_DEFAULT_GAP_WIDTH,
                   ax=None):
    """
    Draws the circular arcs and segments of a diagram
    Args:
        k (PlanarDiagram | OrientedPlanarDiagram): The diagram whose arcs are drawn.
        layout (dict): A layout map where keys are arcs and values are the respective graphical
            elements (e.g., `CircularArc` or `Segment`) describing the visualization.
        endpoints_to_draw (None | list, optional): List of arcs to be drawn. If None, defaults to all arcs in
            the diagram `k`.
        gap (float, optional): The width of the gap between the endpoints of the crossing.
        ax (matplotlib.axes.Axes, optional): The matplotlib axis to which the arcs and segments are
            drawn. If None, the current axis is used.

    # TODO: Use LineCollection and PatchCollection for faster rendering (but this complicates the bounding box).
    """

    if ax is None:
        ax = plt.gca()

    if endpoints_to_draw is None:
        endpoints_to_draw = list(k.endpoints)

    for ep in endpoints_to_draw:
        g_arc = layout[ep]

        # do we need to make a gap?
        if ep.node in k.crossings and not ep.position % 2:
            if g_arc is not None:
                g_arc = g_arc.shorten(_DEFAULT_GAP_WIDTH, side="A", inplace=False)


        if isinstance(g_arc, CircularArc):
            ax.add_patch(
                Arc(xy=(g_arc.center.real, g_arc.center.imag),
                    width=2 * g_arc.radius,
                    height=2 * g_arc.radius,
                    theta1=math.degrees(g_arc.theta1),
                    theta2=math.degrees(g_arc.theta2),
                    color=_DEFAULT_ARC_COLOR,
                    linewidth=_DEFAULT_ARC_WIDTH,
                    zorder=_Z_ENDPOINT
                    )
                )

        elif isinstance(g_arc, Segment):
            ax.add_line(
                Line2D((g_arc.A.real, g_arc.B.real), (g_arc.A.imag, g_arc.B.imag),
                       color=_DEFAULT_ARC_COLOR,
                       linewidth=_DEFAULT_ARC_WIDTH,
                       zorder=_Z_ENDPOINT)
            )


def draw_vertices(
        k: PlanarDiagram | OrientedPlanarDiagram,
        layout:dict,
        vertices_to_draw:None | list=None,
        ax=None):

    if ax is None:
        ax = plt.gca()

    # if vertices to be drawn are not given, draw them all.
    if vertices_to_draw is None:
        vertices_to_draw = list(k.vertices)

    # remove non-visible vertices
    vertices_to_draw = [v for v in vertices_to_draw if v in layout]

    for v in vertices_to_draw:
        xy = layout[v]

        ax.add_patch(plt.Circle(
            xy=(xy.real, xy.imag),
            radius=_DEFAULT_VERTEX_SIZE / 2,
            color=_DEFAULT_VERTEX_COLOR,
            zorder=_Z_VERTEX)
        )


def draw_arrows(
        k: PlanarDiagram | OrientedPlanarDiagram,
        layout:dict,
        endpoint_to_draw: None | list=None,
        position=_DEFAULT_ARROW_POSITION,
        style=_DEFAULT_ARROW_STYLE,
        ax=None):

        if ax is None:
            ax = plt.gca()

        if endpoint_to_draw is None:
            endpoint_to_draw = list(k.endpoints)
        endpoint_to_draw = [k.endpoint_from_pair(ep) for ep in endpoint_to_draw]
        endpoint_to_draw = [ep for ep in endpoint_to_draw if type(ep) is IngoingEndpoint]  # filter only ingoing endpoints

        # Plot arrow on the arc
        if position == "middle":
            for arc in k.arcs:
                ep1, ep2 = arc
                if not (ep := ep1 if ep1 in endpoint_to_draw else (ep2 if ep2 in endpoint_to_draw else None)):
                    continue

                sign = 1 if _is_start(layout[arc], layout[ep.node]) else -1 # the direction of the arrrow

                element = layout[arc]
                arrow_angle = _ARROW_LENGTH / element.radius  # circular arc length is s = theta * radius
                # compute arrow points
                a = element(element.theta1)  # arrow head
                b = element(element.theta1 + sign * arrow_angle)  # arrow tail
                d = b - a  # distance vector
                p = 1j * d / abs(d)  # unit perpendicular vector
                points = [b + p * _ARROW_WIDTH * 0.5, a, b - p * _ARROW_WIDTH * 0.5]
                points = [(p.real, p.imag) for p in points]

                if style == "open":
                    x, y = zip(*points)
                    ax.add_line(Line2D(x[:2], y[:2], color=_DEFAULT_ARROW_COLOR, linewidth=_DEFAULT_ARC_WIDTH, zorder=_Z_ARROW, solid_capstyle='round'))
                    ax.add_line(Line2D(x[1:], y[1:], color=_DEFAULT_ARROW_COLOR, linewidth=_DEFAULT_ARC_WIDTH, zorder=_Z_ARROW, solid_capstyle='round'))
                elif style == "closed":
                    ax.add_patch(Polygon(points, closed=True, edgecolor='none', facecolor=_DEFAULT_ARROW_COLOR, linewidth=0))
                else:
                    raise ValueError(f"Unsupported arrow style: {style}")


def draw_node_labels(
        k: PlanarDiagram | OrientedPlanarDiagram,
        layout:dict,
        nodes_to_draw: None | list=None,
        font_size=_DEFAULT_FONT_SIZE,
        font_color=_DEFAULT_TEXT_COLOR,
        verticalalignment='bottom',
        horizontalalignment='left',
        ax=None):

    if ax is None:
        ax = plt.gca()

    if nodes_to_draw is None:
        nodes_to_draw = list(k.nodes)

    # remove non-visible vertices
    nodes_to_draw = [v for v in nodes_to_draw if v in layout]

    for v in nodes_to_draw:
        xy = layout[v]
        if xy is None:
            continue
        ax.text(
            xy.real,
            xy.imag,
            str(v),
            fontsize=font_size,
            color=font_color,
            verticalalignment=verticalalignment,
            horizontalalignment=horizontalalignment,
            zorder=_Z_TEXT
        )


def draw_endpoint_labels(
        k: PlanarDiagram | OrientedPlanarDiagram,
        layout:dict,
        endpoints_to_draw:None | list=None,
        font_size=_DEFAULT_FONT_SIZE,
        font_color=_DEFAULT_TEXT_COLOR,
        verticalalignment='bottom',
        horizontalalignment='left',
        ax=None):

    if ax is None:
        ax = plt.gca()

    endpoints_to_draw = list(k.endpoints) if endpoints_to_draw is None else [k.endpoint_from_pair(ep) for ep in endpoints_to_draw]

    for ep in endpoints_to_draw:
        garc = layout[ep]
        if garc is None:
            continue
        xy = middle(garc)
        ax.text(
            xy.real,
            xy.imag,
            str(ep),
            fontsize=font_size,
            color=font_color,
            verticalalignment=verticalalignment,
            horizontalalignment=horizontalalignment,
            zorder=_Z_TEXT
        )


def draw_arc_labels(
        k: PlanarDiagram | OrientedPlanarDiagram,
        layout:dict,
        arcs_to_draw:None | list=None,
        font_size=_DEFAULT_FONT_SIZE,
        font_color=_DEFAULT_TEXT_COLOR,
        verticalalignment='bottom',
        horizontalalignment='left',
        ax=None):
    if ax is None:
        ax = plt.gca()
    if arcs_to_draw is None:
        arcs_to_draw = list(k.arcs)

    for arc in arcs_to_draw:
        if (garc := layout[arc]) is None:
            continue
        xy = middle(garc)
        ax.text(
            xy.real,
            xy.imag,
            ",".join(str(ep) for ep in arc),
            fontsize=font_size,
            color=font_color,
            verticalalignment=verticalalignment,
            horizontalalignment=horizontalalignment,
        )

def autoscale_with_padding(ax, pad_frac=0.05):
    # Get bounding box from all elements in the Axes
    ax.relim()             # Recompute limits based on current artists
    ax.autoscale_view()    # Update view based on relim
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # Apply padding
    xpad = (xlim[1] - xlim[0]) * pad_frac
    ypad = (ylim[1] - ylim[0]) * pad_frac

    ax.set_xlim(xlim[0] - xpad, xlim[1] + xpad)
    ax.set_ylim(ylim[0] - ypad, ylim[1] + ypad)

    # Ensure equal aspect ratio
    ax.set_aspect('equal', adjustable='box')


def draw_from_layout(k: PlanarDiagram | OrientedPlanarDiagram, layout:dict, ax, with_labels):
    draw_arcs(k, layout, ax=ax)
    draw_endpoints(k, layout, ax=ax)
    draw_arrows(k, layout, ax=ax)
    draw_vertices(k, layout, ax=ax)

    if with_labels:
        draw_node_labels(k, layout, ax=ax)
        draw_endpoint_labels(k, layout, ax=ax)
        draw_arc_labels(k, layout, ax=ax)
    autoscale_with_padding(ax)
    ax.set_axis_off()


def draw(k: PlanarDiagram | OrientedPlanarDiagram, **kwds):

    #print(k)
    # TODO: analyse keywords (title,...)

    # add bridge and loop support arcs
    supported_k = _add_support_arcs(k)

    # Split the knot into disjoint components (which will be aligned)
    components = disjoint_union_decomposition(supported_k)


    # Compute the layout for each component separately.
    layout_circles_pairs = [layout_circle_packing(_, return_circles=True) for _ in components]

    # Align the components.
    align_layouts(layout_circles_pairs)

    with_labels = kwds.get("with_labels", False)
    show = kwds.get("show", False)

    # Join the layout to a common one.
    joint_layout, joint_circles = {}, {}
    for layout, circles in layout_circles_pairs:
        joint_layout.update(layout)
        joint_circles.update(circles)

    # Plot the joint layout.
    if "ax" in kwds:
        ax = kwds['ax']
    else:
        fig, ax = plt.subplots()
        ax = plt.gca()


    align_layouts(layout_circles_pairs)  # TODO: do we need this?
    if _PLOT_CIRCLES:
        _plot_circles(supported_k, joint_circles, ax=ax)
    draw_from_layout(supported_k, joint_layout, ax=ax, with_labels=with_labels)

    if show:
        plt.show()


def _plot_circles(k: PlanarDiagram | OrientedPlanarDiagram, circles:dict, ax=None):
    if ax is None:
        ax = plt.gca()
    colors = ['#ffeecc', '#ccf2ff', '#e6ffcc']

    for key, circle in circles.items():
        if key in k.nodes:
            color = "b"
        elif key in list(k.arcs):
            color = "r"
        else:
            color = "g"
        ax.add_patch(plt.Circle((circle.center.real, circle.center.imag), circle.radius,
                                  alpha=0.05,
                                  facecolor=color,
                                  ls="none",
                                  zorder=_Z_CIRCLES))





if __name__ == '__main__':
    pass