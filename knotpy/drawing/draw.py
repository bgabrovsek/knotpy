"""
Drawing planar diagrams using Matplotlib.

This module renders planar diagrams given a geometric layout.
It draws arcs/segments, endpoints (with gaps at undercrossings), vertices,
orientation arrows, and optional labels.


Notes
-----
- Layouts are expected to be produced by `knotpy.drawing.layout_circle_packing`.
- Elements in the layout are instances of `CircularArc` or `Segment`.
- A small gap is rendered at underpassing endpoints of crossings to visualize
  over/under information.
"""


import math

from knotpy import sanity_check
from knotpy.classes.endpoint import IngoingEndpoint
from knotpy.classes.node import Crossing
from knotpy.algorithms.disjoint_union import disjoint_union_decomposition
from knotpy.classes.planardiagram import Diagram  # alias: PlanarDiagram | OrientedPlanarDiagram
from knotpy.drawing.layout_circle_packing import layout_circle_packing
from knotpy.utils.geometry import CircularArc, Segment, middle
from knotpy.drawing.alignment import align_layouts
from knotpy.drawing._support import _add_support_arcs
from knotpy.algorithms.topology import edges

__all__ = [
    "draw",
    "draw_from_layout",
]
__version__ = "0.2"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

import knotpy.drawing.drawing_defaults as DEFAULTS

def _mpl_axes():
    """Local Matplotlib imports to keep package import time low."""
    import matplotlib.pyplot as plt
    from matplotlib.axes import Axes  # noqa: F401  # type-only style import
    return plt

def _endpoint_and_arc_colors(k:Diagram, cmap):
    """Return a dictionary where keys are elements (endpoints or arcs) and values are RGBA colors according to the cmap."""
    from matplotlib.pyplot import get_cmap
    if cmap is None:
        return None
    if isinstance(cmap, str):
        cmap = get_cmap(cmap)
    result = {}
    all_edges = edges(k)
    for edge in all_edges:
        seq = [_ for i in range(len(edge) - 1) for _ in (edge[i], frozenset([edge[i], edge[i + 1]]))] + [edge[-1]]
        for i, item in enumerate(seq):
            result[item] = cmap(i / (len(seq) - 1))
    return result


def draw_arcs(
        k: Diagram,
        layout: dict,
        arcs_to_draw: list | None = None,
        ax=None,
        arc_color=DEFAULTS._DEFAULT_ARC_COLOR,
        arc_width=DEFAULTS._DEFAULT_ARC_WIDTH,
        arc_style=DEFAULTS._DEFAULT_ARC_STYLE,
        arc_alpha=DEFAULTS._DEFAULT_ARC_ALPHA,
        arc_stroke_color=DEFAULTS._DEFAULT_ARC_STROKE_COLOR,
        arc_stroke_width=DEFAULTS._DEFAULT_ARC_STROKE_WIDTH,
        arc_stroke_alpha=DEFAULTS._DEFAULT_ARC_STROKE_ALPHA,
        cmap=DEFAULTS._DEFAULT_CMAP,
    ):
    """Draw circular arcs and straight segments corresponding to diagram arcs.

    Args:
        k (Diagram): Diagram whose arcs will be drawn.
        layout (dict): Mapping from each arc (frozenset of two endpoints) to a
            `CircularArc` or `Segment`.
        arcs_to_draw (list | None): Subset of arcs to draw. If None, draw all `k.arcs`.
        ax: Optional Matplotlib axes. If None, uses `plt.gca()`.
    """
    from matplotlib.patches import Arc
    from matplotlib.lines import Line2D
    plt = _mpl_axes()
    element_colors = None

    if ax is None:
        ax = plt.gca()

    colors = _endpoint_and_arc_colors(k, cmap)

    if arcs_to_draw is None:
        arcs_to_draw = list(k.arcs)

    for arc in arcs_to_draw:
        if arc not in layout:
            continue
        g_element = layout[arc]
        color = arc_color if colors is None or arc not in colors else colors[arc]

        if isinstance(g_element, CircularArc):

            if arc_stroke_width:
                # border around the arc
                ax.add_patch(
                    Arc(
                        xy=(g_element.center.real, g_element.center.imag),
                        width=2 * g_element.radius,
                        height=2 * g_element.radius,
                        theta1=math.degrees(g_element.theta1),
                        theta2=math.degrees(g_element.theta2),
                        color=arc_stroke_color,
                        linewidth=arc_width + arc_stroke_width * 2,
                        linestyle="solid",
                        alpha=arc_stroke_alpha,
                        zorder=DEFAULTS._Z_ARC_STROKE,
                    )
                )

            ax.add_patch(
                Arc(
                    xy=(g_element.center.real, g_element.center.imag),
                    width=2 * g_element.radius,
                    height=2 * g_element.radius,
                    theta1=math.degrees(g_element.theta1),
                    theta2=math.degrees(g_element.theta2),
                    color=color,
                    linewidth=arc_width,
                    linestyle=arc_style,
                    alpha=arc_alpha,
                    zorder=DEFAULTS._Z_ARC,
                )
            )

        elif isinstance(g_element, Segment):

            if arc_stroke_width:
                # border around the arc
                ax.add_line(
                    Line2D(
                        (g_element.A.real, g_element.B.real),
                        (g_element.A.imag, g_element.B.imag),
                        color=color,
                        linewidth=arc_width + arc_stroke_width * 2,
                        linestyle="solid",
                        alpha=arc_stroke_alpha,
                        zorder=DEFAULTS.DEFAULTS._Z_ARC_STROKE,
                    )
                )

            ax.add_line(
                Line2D(
                    (g_element.A.real, g_element.B.real),
                    (g_element.A.imag, g_element.B.imag),
                    color=color,
                    linewidth=arc_width,
                    linestyle=arc_style,
                    alpha=arc_alpha,
                    zorder=DEFAULTS._Z_ARC,
                )
            )


def _is_start(element, point):
    """Return True if `point` is closer to the start of `element` than to its end."""
    if isinstance(element, CircularArc):
        return abs(element(element.theta1) - point) < abs(element(element.theta2) - point)
    if isinstance(element, Segment):
        return abs(element(element.A) - point) < abs(element(element.B) - point)
    raise ValueError(f"Unsupported element type: {type(element)}")


def draw_endpoints(
        k: Diagram,
        layout: dict,
        endpoints_to_draw: list | None = None,
        ax=None,
        arc_color=DEFAULTS._DEFAULT_ARC_COLOR,
        arc_width=DEFAULTS._DEFAULT_ARC_WIDTH,
        arc_style=DEFAULTS._DEFAULT_ARC_STYLE,
        arc_alpha=DEFAULTS._DEFAULT_ARC_ALPHA,
        arc_stroke_color=DEFAULTS._DEFAULT_ARC_STROKE_COLOR,
        arc_stroke_width=DEFAULTS._DEFAULT_ARC_STROKE_WIDTH,
        arc_stroke_alpha=DEFAULTS._DEFAULT_ARC_STROKE_ALPHA,
        gap=DEFAULTS._DEFAULT_GAP,
        cmap=DEFAULTS._DEFAULT_CMAP,
    ):
    """Draw endpoint-adjacent sub-arcs for all endpoints, adding gaps under crossings.

    Args:
        k (Diagram): Diagram whose endpoint sub-arcs will be drawn.
        layout (dict): Mapping from endpoint to `CircularArc` or `Segment` (or None).
        endpoints_to_draw (list | None): Subset of endpoints to draw. If None, draw all endpoints.
        gap (float): Width of the gap carved out at under-passing endpoints of crossings.
        ax: Optional Matplotlib axes. If None, uses `plt.gca()`.

    Notes:
        Uses a small shortening near under-passing endpoints (even positions) to visualize over/under.
    """
    plt = _mpl_axes()
    from matplotlib.patches import Arc
    from matplotlib.lines import Line2D

    if ax is None:
        ax = plt.gca()

    colors = _endpoint_and_arc_colors(k, cmap)  # TODO: do not call this again, somehow pass it

    if endpoints_to_draw is None:
        endpoints_to_draw = list(k.endpoints)

    for ep in endpoints_to_draw:
        g_arc = layout[ep]
        color = arc_color if colors is None or ep not in colors else colors[ep]

        z, z_stroke = DEFAULTS._Z_ENDPOINT_UNDER, DEFAULTS._Z_ENDPOINT_STROKE_UNDER
        # Shorten at under-passing endpoints of crossings (even positions).
        if ep.node in k.crossings:
            # make a gap for under-passing endpoints
            if gap > 0 and not ep.position % 2 and g_arc is not None:
                g_arc = g_arc.shorten(gap, side="A", inplace=False)
            # increase z-value for over-passing endpoint
            if ep.position % 2:
                z, z_stroke = DEFAULTS._Z_ENDPOINT_OVER, DEFAULTS._Z_ENDPOINT_STROKE_OVER

        if isinstance(g_arc, CircularArc):

            if arc_stroke_width:
                ax.add_patch(
                    Arc(
                        xy=(g_arc.center.real, g_arc.center.imag),
                        width=2 * g_arc.radius,
                        height=2 * g_arc.radius,
                        theta1=math.degrees(g_arc.theta1),
                        theta2=math.degrees(g_arc.theta2),
                        color=arc_stroke_color,
                        linewidth=arc_width + arc_stroke_width * 2,
                        linestyle="solid",
                        alpha=arc_stroke_alpha,
                        zorder=z_stroke,
                    )
                )

            ax.add_patch(
                Arc(
                    xy=(g_arc.center.real, g_arc.center.imag),
                    width=2 * g_arc.radius,
                    height=2 * g_arc.radius,
                    theta1=math.degrees(g_arc.theta1),
                    theta2=math.degrees(g_arc.theta2),
                    color=color,
                    linewidth=arc_width,
                    linestyle=arc_style,
                    alpha=arc_alpha,
                    zorder=z,
                )
            )
        elif isinstance(g_arc, Segment):

            if arc_stroke_width:
                ax.add_line(
                    Line2D(
                        (g_arc.A.real, g_arc.B.real),
                        (g_arc.A.imag, g_arc.B.imag),
                        color=arc_stroke_color,
                        linewidth=arc_width + arc_stroke_width * 2,
                        linestyle="solid",
                        alpha=arc_stroke_alpha,
                        zorder=z_stroke,
                    )
                )

            ax.add_line(
                Line2D(
                    (g_arc.A.real, g_arc.B.real),
                    (g_arc.A.imag, g_arc.B.imag),
                    color=color,
                    linewidth=arc_width,
                    linestyle=arc_style,
                    alpha=arc_alpha,
                    zorder=z,
                )
            )


def draw_vertices(
        k: Diagram,
        layout: dict,
        vertices_to_draw: list | None = None,
        ax=None,
        vertex_color=DEFAULTS._DEFAULT_VERTEX_COLOR,
        vertex_size=DEFAULTS._DEFAULT_VERTEX_SIZE,
        vertex_alpha=DEFAULTS._DEFAULT_VERTEX_ALPHA,
        vertex_stroke_color=DEFAULTS._DEFAULT_VERTEX_STROKE_COLOR,
        vertex_stroke_width=DEFAULTS._DEFAULT_VERTEX_STROKE_WIDTH,
        vertex_stroke_alpha=DEFAULTS._DEFAULT_VERTEX_STROKE_ALPHA,
    ):

    #print("draw v", k)

    """Draw solid disks for vertex nodes.

    Args:
        k (Diagram): Diagram whose vertices will be drawn.
        layout (dict): Mapping from node -> complex center for vertices.
        vertices_to_draw (list | None): Subset of vertices to draw. If None, draw all vertices.
        ax: Optional Matplotlib axes. If None, uses `plt.gca()`.
    """
    plt = _mpl_axes()

    if ax is None:
        ax = plt.gca()

    if vertices_to_draw is None:
        vertices_to_draw = list(k.vertices)

    vertices_to_draw = [v for v in vertices_to_draw if v in layout]
    """
     edgecolor=None,
                 facecolor=None,
                 color=None,
                 linewidth=None,
                 linestyle=None,
                 antialiased=None,
                 hatch=None,
                 fill=True,
                 capstyle=None,
                 joinstyle=None,
                 """

    for v in vertices_to_draw:
        xy = layout[v]
        if xy is None:
            continue
        ax.add_patch(
            plt.Circle(
                xy=(xy.real, xy.imag),
                radius=vertex_size / 2,
                facecolor=vertex_color,
                alpha=vertex_alpha,
                edgecolor=vertex_stroke_color,
                linewidth=vertex_stroke_width,
                zorder=DEFAULTS._Z_VERTEX,
            )
        )


def draw_arrows(
        k: Diagram,
        layout: dict,
        endpoint_to_draw: list | None = None,
        ax=None,
        arrow_line_width=DEFAULTS._DEFAULT_ARC_WIDTH,
        arrow_color=DEFAULTS._DEFAULT_ARROW_COLOR,
        arrow_width=DEFAULTS._DEFAULT_ARROW_WIDTH,
        arrow_length=DEFAULTS._DEFAULT_ARROW_LENGTH,
        arrow_style=DEFAULTS._DEFAULT_ARROW_STYLE,
        arrow_cap_style=DEFAULTS._DEFAULT_ARROW_CAP_STYLE,
        arrow_position=DEFAULTS._DEFAULT_ARROW_POSITION,
        arrow_alpha=DEFAULTS._DEFAULT_ARROW_ALPHA,
        arc_stroke_color=DEFAULTS._DEFAULT_ARC_STROKE_COLOR,
        arc_stroke_width=DEFAULTS._DEFAULT_ARC_STROKE_WIDTH,
        arc_stroke_alpha=DEFAULTS._DEFAULT_ARC_STROKE_ALPHA,
        cmap=DEFAULTS._DEFAULT_CMAP,
):
    """Draw orientation arrows along arcs (for ingoing endpoints).

    Args:
        k (Diagram): Diagram whose orientation will be drawn.
        layout (dict): Mapping for arcs and endpoints to their geometric elements.
        endpoint_to_draw (list | None): Optional subset of endpoints; if None, all endpoints are considered.
        position (str): Where to place arrows. Currently only "middle" is supported.
        style (str): "open" (V-shaped) or "closed" (filled triangle).
        ax: Optional Matplotlib axes. If None, uses `plt.gca()`.
    """
    plt = _mpl_axes()
    from matplotlib.patches import Polygon
    from matplotlib.lines import Line2D

    if ax is None:
        ax = plt.gca()

    colors = _endpoint_and_arc_colors(k, cmap)  # TODO: do not call this again, somehow pass it

    if endpoint_to_draw is None:
        endpoint_to_draw = list(k.endpoints)
    endpoint_to_draw = [k.endpoint_from_pair(ep) for ep in endpoint_to_draw]
    endpoint_to_draw = [ep for ep in endpoint_to_draw if type(ep) is IngoingEndpoint]

    if arrow_position == "middle":
        for arc in k.arcs:
            if arc not in layout:
                continue
            ep1, ep2 = arc
            ep = ep1 if ep1 in endpoint_to_draw else (ep2 if ep2 in endpoint_to_draw else None)
            if not ep:
                continue

            element = layout[arc]
            color = arrow_color if colors is None or ep not in colors else colors[ep]
            sign = 1 if _is_start(element, layout[ep.node]) else -1

            # Arrow geometry on circular arcs/segments.
            arrow_angle = arrow_length / element.radius
            a = element(element.theta1)  # arrow head
            b = element(element.theta1 + sign * arrow_angle)  # arrow tail
            d = b - a
            p = 1j * d / abs(d)  # unit perpendicular
            pts = [b + p * (arrow_width * 0.5), a, b - p * (arrow_width * 0.5)]
            pts_xy = [(w.real, w.imag) for w in pts]

            if arrow_style == "open":
                x, y = zip(*pts_xy)

                if arc_stroke_width:
                    ax.add_line(
                        Line2D(x[:2], y[:2],
                               color=arc_stroke_color, linewidth=arrow_line_width + 2 * arc_stroke_width,
                               zorder=DEFAULTS._Z_ENDPOINT_STROKE_UNDER, solid_capstyle=arrow_cap_style, alpha=arc_stroke_alpha,)
                    )
                    ax.add_line(
                        Line2D(x[1:], y[1:],
                               color=arc_stroke_color, linewidth=arrow_line_width + 2 * arc_stroke_width,
                               zorder=DEFAULTS._Z_ENDPOINT_STROKE_UNDER, solid_capstyle=arrow_cap_style, alpha=arc_stroke_alpha )
                    )

                ax.add_line(
                    Line2D(x[:2], y[:2],
                           color=color, linewidth=arrow_line_width,
                           zorder=DEFAULTS._Z_ARROW, solid_capstyle=arrow_cap_style, alpha=arrow_alpha,)
                )
                ax.add_line(
                    Line2D(x[1:], y[1:],
                           color=color, linewidth=arrow_line_width,
                           zorder=DEFAULTS._Z_ARROW, solid_capstyle=arrow_cap_style, alpha=arrow_alpha,)
                )

            elif arrow_style == "closed":
                # TODO: add stroke, add z-order
                ax.add_patch(
                    Polygon(pts_xy, closed=True, edgecolor="none", facecolor=arrow_color, alpha=arrow_alpha, linewidth=0)
                )
            else:
                raise ValueError(f"Unsupported arrow style: {arrow_style}")


def draw_node_labels(
        k: Diagram,
        layout: dict,
        nodes_to_draw: list | None = None,
        ax=None,
        label_color=DEFAULTS._DEFAULT_LABEL_COLOR,
        label_font_size=DEFAULTS._DEFAULT_LABEL_FONT_SIZE,
        label_font_family=DEFAULTS._DEFAULT_LABEL_FONT_FAMILY,
        label_horizontal_alignment=DEFAULTS._DEFAULT_LABEL_HORIZONTAL_ALIGNMENT,
        label_vertical_alignment=DEFAULTS._DEFAULT_LABEL_VERTICAL_ALIGNMENT,
        label_alpha=DEFAULTS._DEFAULT_LABEL_ALPHA,
    ):
    """Annotate nodes (crossings/vertices) with their identifiers.

    Args:
        k (Diagram): Diagram whose node labels will be drawn.
        layout (dict): Mapping node -> complex position for label placement.
        nodes_to_draw (list | None): Subset of nodes; if None, label all nodes in layout.
        font_size (int): Font size.
        font_color (str): Text color.
        verticalalignment (str): Matplotlib text vertical alignment.
        horizontalalignment (str): Matplotlib text horizontal alignment.
        ax: Optional Matplotlib axes. If None, uses `plt.gca()`.
    """
    plt = _mpl_axes()

    if ax is None:
        ax = plt.gca()

    if nodes_to_draw is None:
        nodes_to_draw = list(k.nodes)

    nodes_to_draw = [v for v in nodes_to_draw if v in layout]

    for v in nodes_to_draw:
        xy = layout[v]
        if xy is None:
            continue
        ax.text(
            xy.real,
            xy.imag,
            str(v),
            fontsize=label_font_size,
            color=label_color,
            alpha=label_alpha,
            verticalalignment=label_vertical_alignment,
            horizontalalignment=label_horizontal_alignment,
            zorder=DEFAULTS._Z_TEXT,
        )
        #TODO font family


def draw_endpoint_labels(
        k: Diagram,
        layout: dict,
        endpoints_to_draw: list | None = None,
        ax=None,
        label_color=DEFAULTS._DEFAULT_LABEL_COLOR,
        label_font_size=DEFAULTS._DEFAULT_LABEL_FONT_SIZE,
        label_font_family=DEFAULTS._DEFAULT_LABEL_FONT_FAMILY,
        label_horizontal_alignment=DEFAULTS._DEFAULT_LABEL_HORIZONTAL_ALIGNMENT,
        label_vertical_alignment=DEFAULTS._DEFAULT_LABEL_VERTICAL_ALIGNMENT,
        label_alpha=DEFAULTS._DEFAULT_LABEL_ALPHA,
    ):
    """Annotate endpoints with their (node, position) labels near the middle of their sub-arc.

    Args:
        k (Diagram): Diagram whose endpoint labels will be drawn.
        layout (dict): Mapping endpoint -> `CircularArc` or `Segment`.
        endpoints_to_draw (list | None): Subset of endpoints; if None, label all.
        font_size (int): Font size.
        font_color (str): Text color.
        verticalalignment (str): Matplotlib text vertical alignment.
        horizontalalignment (str): Matplotlib text horizontal alignment.
        ax: Optional Matplotlib axes. If None, uses `plt.gca()`.
    """
    plt = _mpl_axes()

    if ax is None:
        ax = plt.gca()

    endpoints = list(k.endpoints) if endpoints_to_draw is None else [k.endpoint_from_pair(ep) for ep in endpoints_to_draw]

    for ep in endpoints:
        garc = layout[ep]
        if garc is None:
            continue
        xy = middle(garc)
        ax.text(
            xy.real,
            xy.imag,
            str(ep),
            fontsize=label_font_size,
            color=label_color,
            verticalalignment=label_vertical_alignment,
            horizontalalignment=label_horizontal_alignment,
            alpha=label_alpha,
            zorder=DEFAULTS._Z_TEXT,
        )
        # TODO font family


def draw_arc_labels(
        k: Diagram,
        layout: dict,
        arcs_to_draw: list | None = None,
        ax=None,
        label_color=DEFAULTS._DEFAULT_LABEL_COLOR,
        label_font_size=DEFAULTS._DEFAULT_LABEL_FONT_SIZE,
        label_font_family=DEFAULTS._DEFAULT_LABEL_FONT_FAMILY,
        label_horizontal_alignment=DEFAULTS._DEFAULT_LABEL_HORIZONTAL_ALIGNMENT,
        label_vertical_alignment=DEFAULTS._DEFAULT_LABEL_VERTICAL_ALIGNMENT,
        label_alpha=DEFAULTS._DEFAULT_LABEL_ALPHA,
    ):
    """Annotate arcs by listing their two endpoint labels near the middle of the arc.

    Args:
        k (Diagram): Diagram whose arc labels will be drawn.
        layout (dict): Mapping arc -> `CircularArc` or `Segment`.
        arcs_to_draw (list | None): Subset of arcs; if None, label all `k.arcs`.
        font_size (int): Font size.
        font_color (str): Text color.
        verticalalignment (str): Matplotlib text vertical alignment.
        horizontalalignment (str): Matplotlib text horizontal alignment.
        ax: Optional Matplotlib axes. If None, uses `plt.gca()`.
    """
    plt = _mpl_axes()

    if ax is None:
        ax = plt.gca()

    if arcs_to_draw is None:
        arcs_to_draw = list(k.arcs)

    for arc in arcs_to_draw:
        garc = layout[arc]
        if garc is None:
            continue
        xy = middle(garc)
        ax.text(
            xy.real,
            xy.imag,
            ",".join(str(ep) for ep in arc),
            fontsize=label_font_size,
            color=label_color,
            verticalalignment=label_vertical_alignment,
            horizontalalignment=label_horizontal_alignment,
            alpha=label_alpha,
        )
        # TODO font family

def autoscale_with_padding(ax, pad_frac: float = 0.05):
    """Autoscale the axes to fit current artists, apply padding, and set equal aspect.

    Args:
        ax: Matplotlib axes.
        pad_frac (float): Fractional padding to apply to both x and y ranges.
    """
    ax.relim()
    ax.autoscale_view()

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    xpad = (xlim[1] - xlim[0]) * pad_frac
    ypad = (ylim[1] - ylim[0]) * pad_frac

    ax.set_xlim(xlim[0] - xpad, xlim[1] + xpad)
    ax.set_ylim(ylim[0] - ypad, ylim[1] + ypad)

    ax.set_aspect("equal", adjustable="box")


def draw_from_layout(
        k: Diagram,
        layout: dict,
        ax=None,
        # Arc
        arc_color=DEFAULTS._DEFAULT_ARC_COLOR,
        arc_width=DEFAULTS._DEFAULT_ARC_WIDTH,
        arc_style=DEFAULTS._DEFAULT_ARC_STYLE,
        arc_alpha=DEFAULTS._DEFAULT_ARC_ALPHA,
        arc_stroke_color=DEFAULTS._DEFAULT_ARC_STROKE_COLOR,
        arc_stroke_width=DEFAULTS._DEFAULT_ARC_STROKE_WIDTH,
        arc_stroke_alpha=DEFAULTS._DEFAULT_ARC_STROKE_ALPHA,
        gap=DEFAULTS._DEFAULT_GAP,
        cmap=DEFAULTS._DEFAULT_CMAP,
        # Vertex
        vertex_color=DEFAULTS._DEFAULT_VERTEX_COLOR,
        vertex_size=DEFAULTS._DEFAULT_VERTEX_SIZE,
        vertex_alpha=DEFAULTS._DEFAULT_VERTEX_ALPHA,
        vertex_stroke_color=DEFAULTS._DEFAULT_VERTEX_STROKE_COLOR,
        vertex_stroke_width=DEFAULTS._DEFAULT_VERTEX_STROKE_WIDTH,
        vertex_stroke_alpha=DEFAULTS._DEFAULT_VERTEX_STROKE_ALPHA,
        # Arrow
        arrow_color=DEFAULTS._DEFAULT_ARROW_COLOR,
        arrow_width=DEFAULTS._DEFAULT_ARROW_WIDTH,
        arrow_length=DEFAULTS._DEFAULT_ARROW_LENGTH,
        arrow_style=DEFAULTS._DEFAULT_ARROW_STYLE,
        arrow_cap_style=DEFAULTS._DEFAULT_ARROW_CAP_STYLE,
        arrow_position=DEFAULTS._DEFAULT_ARROW_POSITION,
        arrow_alpha=DEFAULTS._DEFAULT_ARROW_ALPHA,
        # Labels
        label_endpoints=DEFAULTS._DEFAULT_LABEL_ENDPOINTS,
        label_arcs=DEFAULTS._DEFAULT_LABEL_ARCS,
        label_nodes=DEFAULTS._DEFAULT_LABEL_NODES,
        label_color=DEFAULTS._DEFAULT_LABEL_COLOR,
        label_font_size=DEFAULTS._DEFAULT_LABEL_FONT_SIZE,
        label_font_family=DEFAULTS._DEFAULT_LABEL_FONT_FAMILY,
        label_horizontal_alignment=DEFAULTS._DEFAULT_LABEL_HORIZONTAL_ALIGNMENT,
        label_vertical_alignment=DEFAULTS._DEFAULT_LABEL_VERTICAL_ALIGNMENT,
        label_alpha=DEFAULTS._DEFAULT_LABEL_ALPHA,
        # Title
        title=DEFAULTS._DEFAULT_TITLE,  # bool or string
        title_color=DEFAULTS._DEFAULT_TITLE_COLOR,
        title_font_size=DEFAULTS._DEFAULT_TITLE_FONT_SIZE,
        title_font_family=DEFAULTS._DEFAULT_TITLE_FONT_FAMILY,
        title_alpha=DEFAULTS._DEFAULT_TITLE_ALPHA,
        # Other
        padding_fraction=DEFAULTS._DEFAULT_PADDING_FRACTION,
        show_axis=DEFAULTS._DEFAULT_SHOW_AXIS,
        show=DEFAULTS._DEFAULT_SHOW,
        ):
    """Render a diagram from a precomputed layout onto given axes.

    Args:
        k (Diagram): Diagram to draw.
        layout (dict): Mapping of arcs/endpoints/nodes to geometric elements or positions.
        ax: Matplotlib axes to draw on.
        with_labels (bool): If True, draw node/endpoint/arc labels.
    """
    if arrow_color is None:
        arrow_color = arc_color
    args = dict(locals())
    plt = _mpl_axes()

    # Prepare axes.
    if ax is None:
        _, ax = plt.subplots()
        ax = plt.gca()


    args_arcs = {key: value for key, value in args.items() if key.startswith("arc")}
    draw_arcs(k, layout, ax=ax, cmap=cmap, **args_arcs)
    draw_endpoints(k, layout, ax=ax, gap=gap, cmap=cmap, **args_arcs)

    args_arcs = {key: value for key, value in args.items() if key.startswith("arrow")}
    draw_arrows(k, layout, ax=ax, cmap=cmap,
                arc_stroke_color=arc_stroke_color, arc_stroke_width=arc_stroke_width, arc_stroke_alpha=arc_stroke_alpha,
                **args_arcs)

    args_vertex = {key: value for key, value in args.items() if key.startswith("vertex")}
    draw_vertices(k, layout, ax=ax, **args_vertex)


    args_label = {key: value for key, value in args.items() if key.startswith("label")}
    for key in ("label_endpoints", "label_arcs", "label_nodes"):
        del args_label[key]

    if label_nodes:
        draw_node_labels(k, layout, ax=ax, **args_label)
    if label_endpoints:
        draw_endpoint_labels(k, layout, ax=ax, **args_label)
    if label_arcs:
        draw_arc_labels(k, layout, ax=ax, **args_label)


    autoscale_with_padding(ax, pad_frac=padding_fraction)

    if not show_axis:
        ax.set_axis_off()

    if show:
        plt.show()


def draw(
        k: Diagram,
        ax=None,
        rotation=DEFAULTS._DEFAULT_ROTATION,  # degrees, counterclockwise
        # Arc
        arc_color=DEFAULTS._DEFAULT_ARC_COLOR,
        arc_width=DEFAULTS._DEFAULT_ARC_WIDTH,
        arc_style=DEFAULTS._DEFAULT_ARC_STYLE,
        arc_alpha=DEFAULTS._DEFAULT_ARC_ALPHA,
        arc_stroke_color=DEFAULTS._DEFAULT_ARC_STROKE_COLOR,
        arc_stroke_width=DEFAULTS._DEFAULT_ARC_STROKE_WIDTH,
        arc_stroke_alpha=DEFAULTS._DEFAULT_ARC_STROKE_ALPHA,
        gap=DEFAULTS._DEFAULT_GAP,
        cmap=DEFAULTS._DEFAULT_CMAP,
        # Vertex
        vertex_color=DEFAULTS._DEFAULT_VERTEX_COLOR,
        vertex_size=DEFAULTS._DEFAULT_VERTEX_SIZE,
        vertex_alpha=DEFAULTS._DEFAULT_VERTEX_ALPHA,
        vertex_stroke_color=DEFAULTS._DEFAULT_VERTEX_STROKE_COLOR,
        vertex_stroke_width=DEFAULTS._DEFAULT_VERTEX_STROKE_WIDTH,
        vertex_stroke_alpha=DEFAULTS._DEFAULT_VERTEX_STROKE_ALPHA,
        # Arrow
        arrow_color=DEFAULTS._DEFAULT_ARROW_COLOR,
        arrow_width=DEFAULTS._DEFAULT_ARROW_WIDTH,
        arrow_length=DEFAULTS._DEFAULT_ARROW_LENGTH,
        arrow_style=DEFAULTS._DEFAULT_ARROW_STYLE,
        arrow_cap_style=DEFAULTS._DEFAULT_ARROW_CAP_STYLE,
        arrow_position=DEFAULTS._DEFAULT_ARROW_POSITION,
        arrow_alpha=DEFAULTS._DEFAULT_ARROW_ALPHA,
        # Labels
        label_endpoints=DEFAULTS._DEFAULT_LABEL_ENDPOINTS,
        label_arcs=DEFAULTS._DEFAULT_LABEL_ARCS,
        label_nodes=DEFAULTS._DEFAULT_LABEL_NODES,
        label_color=DEFAULTS._DEFAULT_LABEL_COLOR,
        label_font_size=DEFAULTS._DEFAULT_LABEL_FONT_SIZE,
        label_font_family=DEFAULTS._DEFAULT_LABEL_FONT_FAMILY,
        label_horizontal_alignment=DEFAULTS._DEFAULT_LABEL_HORIZONTAL_ALIGNMENT,
        label_vertical_alignment=DEFAULTS._DEFAULT_LABEL_VERTICAL_ALIGNMENT,
        label_alpha=DEFAULTS._DEFAULT_LABEL_ALPHA,
        # Title
        title=DEFAULTS._DEFAULT_TITLE,  # bool or string
        title_color=DEFAULTS._DEFAULT_TITLE_COLOR,
        title_font_size=DEFAULTS._DEFAULT_TITLE_FONT_SIZE,
        title_font_family=DEFAULTS._DEFAULT_TITLE_FONT_FAMILY,
        title_alpha=DEFAULTS._DEFAULT_TITLE_ALPHA,
        # Other
        show_circle_packing=DEFAULTS._DEFAULT_SHOW_CIRCLE_PACKING,
        padding_fraction=DEFAULTS._DEFAULT_PADDING_FRACTION,
        show_axis=DEFAULTS._DEFAULT_SHOW_AXIS,
        show=DEFAULTS._DEFAULT_SHOW,
    ):

    """High-level convenience function to draw a diagram.

    This function:
      1) Adds support arcs (to eliminate bridges etc.) for robust drawing,
      2) Decomposes the diagram into disjoint components,
      3) Computes a circle-packing layout for each component,
      4) Aligns components horizontally,
      5) Renders the composed result to Matplotlib.

    Args:
        k (Diagram): The diagram to draw.
        **kwds: Optional keyword arguments:
            - ax: Matplotlib axes to draw on. If omitted, a new figure/axes is created.
            - with_labels (bool): If True, draw node/endpoint/arc labels. Default False.
            - show (bool): If True, call `plt.show()` at the end. Default False.
    """
    #TODO: minimize the number of arguments by adding **kwargs with non-essential arguments (alpha,...)

    if not sanity_check(k):
        raise ValueError("Diagram is not a valid knotted diagram.")

    if arrow_color is None:
        arrow_color = arc_color
    args = dict(locals())

    plt = _mpl_axes()

    # add support arcs (bridges/cut-vertices handling for reliable plotting)
    supported_k = _add_support_arcs(k)

    # decompose into disjoint components
    components = disjoint_union_decomposition(supported_k)


    # compute layout per component (and keep the circle packing for alignment)
    layout_circles_pairs = [layout_circle_packing(comp, rotation=rotation, return_circles=True) for comp in components]
    # align components horizontally
    align_layouts(layout_circles_pairs)

    # for l in layout_circles_pairs:
    #     print(l)
    #     for o in l:
    #         print("   ", o)
    #         for key, value in o.items():
    #             print("      ", key, value)

    # merge per-component layouts into a joint layout
    joint_layout, joint_circles = {}, {}
    for layout, circles in layout_circles_pairs:
        joint_layout.update(layout)
        joint_circles.update(circles)

    # prepare axes
    if ax is None:
        _, ax = plt.subplots(constrained_layout=True)
        #plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
        #ax = plt.gca()

    align_layouts(layout_circles_pairs)  # keeps relative spacing if recomputed upstream

    # optional: visualize circle regions used in packing
    if show_circle_packing:
        _plot_circles(supported_k, joint_circles, ax=ax)

    # render
    for key in ("show_circle_packing", "rotation", "ax", "k") :
        del args[key]
    draw_from_layout(k=supported_k, layout=joint_layout, ax=ax, **args)





def _plot_circles(k: Diagram, circles: dict, ax=None):
    """Lightweight visualization of circle-packing regions (useful for debugging/alignment)."""
    plt = _mpl_axes()

    if ax is None:
        ax = plt.gca()

    for key, circle in circles.items():
        if key in k.nodes:
            color = "b"
        elif key in list(k.arcs):
            color = "r"
        else:
            color = "g"
        ax.add_patch(
            plt.Circle(
                (circle.center.real, circle.center.imag),
                circle.radius,
                alpha=0.05,
                facecolor=color,
                ls="none",
                zorder=DEFAULTS._Z_CIRCLES,
            )
        )


if __name__ == "__main__":
    import knotpy as kp
    k = kp.knot("3_1")
    kp.draw(k, show=True)
    exit()

    k3 = kp.orient(kp.knot("3_1"))
    #kp.draw(k3, show=True, gap=0, arc_stroke_width=6, arc_width=4, arc_stroke_color="white") #cmap="jet"
    #kp.draw(k3, show=True, gap=0, arc_color="white", arc_stroke_width=6, arc_width=4, arc_stroke_color="black") #cmap="jet"
    k = kp.theta("t3_1")
    # kp.draw(k, show=True, gap=0, arc_stroke_width=6, arc_width=4, arc_stroke_color="white",
    #         vertex_color="white", vertex_stroke_color="black", vertex_stroke_width=4)
    a = kp.orient(kp.knot("3_1"))
    b = kp.orient(kp.knot("4_1"))
    k = kp.connected_sum(a, b )
    #kp.add_unknot(k, inplace=True)
    kk = kp.reidemeister_1_add_kink(k, kp.choose_reidemeister_1_add_kink(k))
    kp.draw(kk, show=True) #cmap="jet"

    pass