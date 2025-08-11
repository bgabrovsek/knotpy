"""
High-level drawing utilities for KnotPy diagrams using Matplotlib.

This module renders planar (and oriented) diagrams given a geometric layout.
It draws arcs/segments, endpoints (with gaps at undercrossings), vertices,
orientation arrows, and optional labels. When a diagram has multiple disjoint
components, you can compute layouts per component and align them horizontally
for a tidy final composition.

To minimize import time for the package, heavy dependencies such as Matplotlib
are imported locally inside the drawing functions.

Notes
-----
- Layouts are expected to be produced by `knotpy.drawing.layout_circle_packing`.
- Elements in the layout are instances of `CircularArc` or `Segment`.
- A small gap is rendered at underpassing endpoints of crossings to visualize
  over/under information.
"""

import math

from knotpy.classes.endpoint import IngoingEndpoint
from knotpy.algorithms.disjoint_union import disjoint_union_decomposition
from knotpy.classes.planardiagram import Diagram  # alias: PlanarDiagram | OrientedPlanarDiagram
from knotpy.drawing.layout_circle_packing import layout_circle_packing
from knotpy.utils.geometry import CircularArc, Segment, middle
from knotpy.drawing.alignment import align_layouts
from knotpy.drawing._support import _add_support_arcs

__all__ = [
    "draw",
    "draw_from_layout",
    "draw_arcs",
    "draw_endpoints",
    "draw_vertices",
    "draw_arrows",
    "draw_node_labels",
    "draw_endpoint_labels",
    "draw_arc_labels",
    "autoscale_with_padding",
]
__version__ = "0.2"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

_DEFAULT_ARC_COLOR = "tab:blue"   # knot strand color
_DEFAULT_ARC_WIDTH = 4.0          # knot strand width
_DEFAULT_GAP_WIDTH = 0.1          # arc break gap at the under-passing

_DEFAULT_VERTEX_SIZE = 0.1
_DEFAULT_VERTEX_COLOR = "black"

_DEFAULT_TEXT_COLOR = "black"
_DEFAULT_FONT_SIZE = 14

_ARROW_LENGTH = 0.15
_ARROW_WIDTH = 0.15
_DEFAULT_ARROW_COLOR = _DEFAULT_ARC_COLOR
_DEFAULT_ARROW_POSITION = "middle"  # currently only "middle" is supported
_DEFAULT_ARROW_STYLE = "open"       # "open" or "closed"

# Debug helper to visualize circle packing regions.
_PLOT_CIRCLES = True

# Z-order (stacking) for plot elements; lower values are drawn first.
_Z_CIRCLES = 0
_Z_ARC = 1
_Z_ENDPOINT = 1
_Z_ARROW = 2
_Z_VERTEX = 3
_Z_TEXT = 4


def _mpl_axes():
    """Local Matplotlib imports to keep package import time low."""
    import matplotlib.pyplot as plt
    from matplotlib.axes import Axes  # noqa: F401  # type-only style import
    return plt


def draw_arcs(k: Diagram, layout: dict, arcs_to_draw: list | None = None, ax=None):
    """Draw circular arcs and straight segments corresponding to diagram arcs.

    Args:
        k (Diagram): Diagram whose arcs will be drawn.
        layout (dict): Mapping from each arc (frozenset of two endpoints) to a
            `CircularArc` or `Segment`.
        arcs_to_draw (list | None): Subset of arcs to draw. If None, draw all `k.arcs`.
        ax: Optional Matplotlib axes. If None, uses `plt.gca()`.
    """
    plt = _mpl_axes()
    from matplotlib.patches import Arc
    from matplotlib.lines import Line2D

    if ax is None:
        ax = plt.gca()

    if arcs_to_draw is None:
        arcs_to_draw = list(k.arcs)

    for arc in arcs_to_draw:
        element = layout[arc]
        if isinstance(element, CircularArc):
            ax.add_patch(
                Arc(
                    xy=(element.center.real, element.center.imag),
                    width=2 * element.radius,
                    height=2 * element.radius,
                    theta1=math.degrees(element.theta1),
                    theta2=math.degrees(element.theta2),
                    color=_DEFAULT_ARC_COLOR,
                    linewidth=_DEFAULT_ARC_WIDTH,
                    zorder=_Z_ARC,
                )
            )
        elif isinstance(element, Segment):
            ax.add_line(
                Line2D(
                    (element.A.real, element.B.real),
                    (element.A.imag, element.B.imag),
                    color=_DEFAULT_ARC_COLOR,
                    linewidth=_DEFAULT_ARC_WIDTH,
                    zorder=_Z_ARC,
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
    gap: float = _DEFAULT_GAP_WIDTH,
    ax=None,
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

    if endpoints_to_draw is None:
        endpoints_to_draw = list(k.endpoints)

    for ep in endpoints_to_draw:
        g_arc = layout[ep]

        # Shorten at under-passing endpoints of crossings (even positions).
        if ep.node in k.crossings and not ep.position % 2:
            if g_arc is not None:
                g_arc = g_arc.shorten(gap, side="A", inplace=False)

        if isinstance(g_arc, CircularArc):
            ax.add_patch(
                Arc(
                    xy=(g_arc.center.real, g_arc.center.imag),
                    width=2 * g_arc.radius,
                    height=2 * g_arc.radius,
                    theta1=math.degrees(g_arc.theta1),
                    theta2=math.degrees(g_arc.theta2),
                    color=_DEFAULT_ARC_COLOR,
                    linewidth=_DEFAULT_ARC_WIDTH,
                    zorder=_Z_ENDPOINT,
                )
            )
        elif isinstance(g_arc, Segment):
            ax.add_line(
                Line2D(
                    (g_arc.A.real, g_arc.B.real),
                    (g_arc.A.imag, g_arc.B.imag),
                    color=_DEFAULT_ARC_COLOR,
                    linewidth=_DEFAULT_ARC_WIDTH,
                    zorder=_Z_ENDPOINT,
                )
            )


def draw_vertices(k: Diagram, layout: dict, vertices_to_draw: list | None = None, ax=None):
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

    for v in vertices_to_draw:
        xy = layout[v]
        ax.add_patch(
            plt.Circle(
                xy=(xy.real, xy.imag),
                radius=_DEFAULT_VERTEX_SIZE / 2,
                color=_DEFAULT_VERTEX_COLOR,
                zorder=_Z_VERTEX,
            )
        )


def draw_arrows(
    k: Diagram,
    layout: dict,
    endpoint_to_draw: list | None = None,
    position: str = _DEFAULT_ARROW_POSITION,
    style: str = _DEFAULT_ARROW_STYLE,
    ax=None,
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

    if endpoint_to_draw is None:
        endpoint_to_draw = list(k.endpoints)
    endpoint_to_draw = [k.endpoint_from_pair(ep) for ep in endpoint_to_draw]
    endpoint_to_draw = [ep for ep in endpoint_to_draw if type(ep) is IngoingEndpoint]

    if position == "middle":
        for arc in k.arcs:
            ep1, ep2 = arc
            ep = ep1 if ep1 in endpoint_to_draw else (ep2 if ep2 in endpoint_to_draw else None)
            if not ep:
                continue

            element = layout[arc]
            sign = 1 if _is_start(element, layout[ep.node]) else -1

            # Arrow geometry on circular arcs/segments.
            arrow_angle = _ARROW_LENGTH / element.radius
            a = element(element.theta1)  # arrow head
            b = element(element.theta1 + sign * arrow_angle)  # arrow tail
            d = b - a
            p = 1j * d / abs(d)  # unit perpendicular
            pts = [b + p * (_ARROW_WIDTH * 0.5), a, b - p * (_ARROW_WIDTH * 0.5)]
            pts_xy = [(w.real, w.imag) for w in pts]

            if style == "open":
                x, y = zip(*pts_xy)
                ax.add_line(
                    Line2D(
                        x[:2],
                        y[:2],
                        color=_DEFAULT_ARROW_COLOR,
                        linewidth=_DEFAULT_ARC_WIDTH,
                        zorder=_Z_ARROW,
                        solid_capstyle="round",
                    )
                )
                ax.add_line(
                    Line2D(
                        x[1:],
                        y[1:],
                        color=_DEFAULT_ARROW_COLOR,
                        linewidth=_DEFAULT_ARC_WIDTH,
                        zorder=_Z_ARROW,
                        solid_capstyle="round",
                    )
                )
            elif style == "closed":
                ax.add_patch(
                    Polygon(
                        pts_xy,
                        closed=True,
                        edgecolor="none",
                        facecolor=_DEFAULT_ARROW_COLOR,
                        linewidth=0,
                    )
                )
            else:
                raise ValueError(f"Unsupported arrow style: {style}")


def draw_node_labels(
    k: Diagram,
    layout: dict,
    nodes_to_draw: list | None = None,
    font_size: int = _DEFAULT_FONT_SIZE,
    font_color: str = _DEFAULT_TEXT_COLOR,
    verticalalignment: str = "bottom",
    horizontalalignment: str = "left",
    ax=None,
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
            fontsize=font_size,
            color=font_color,
            verticalalignment=verticalalignment,
            horizontalalignment=horizontalalignment,
            zorder=_Z_TEXT,
        )


def draw_endpoint_labels(
    k: Diagram,
    layout: dict,
    endpoints_to_draw: list | None = None,
    font_size: int = _DEFAULT_FONT_SIZE,
    font_color: str = _DEFAULT_TEXT_COLOR,
    verticalalignment: str = "bottom",
    horizontalalignment: str = "left",
    ax=None,
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
            fontsize=font_size,
            color=font_color,
            verticalalignment=verticalalignment,
            horizontalalignment=horizontalalignment,
            zorder=_Z_TEXT,
        )


def draw_arc_labels(
    k: Diagram,
    layout: dict,
    arcs_to_draw: list | None = None,
    font_size: int = _DEFAULT_FONT_SIZE,
    font_color: str = _DEFAULT_TEXT_COLOR,
    verticalalignment: str = "bottom",
    horizontalalignment: str = "left",
    ax=None,
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
            fontsize=font_size,
            color=font_color,
            verticalalignment=verticalalignment,
            horizontalalignment=horizontalalignment,
        )


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


def draw_from_layout(k: Diagram, layout: dict, ax, with_labels: bool):
    """Render a diagram from a precomputed layout onto given axes.

    Args:
        k (Diagram): Diagram to draw.
        layout (dict): Mapping of arcs/endpoints/nodes to geometric elements or positions.
        ax: Matplotlib axes to draw on.
        with_labels (bool): If True, draw node/endpoint/arc labels.
    """
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


def draw(k: Diagram, **kwds):
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
    plt = _mpl_axes()

    # 1) Add support arcs (bridges/cut-vertices handling for reliable plotting).
    supported_k = _add_support_arcs(k)

    # 2) Decompose into disjoint components.
    components = disjoint_union_decomposition(supported_k)

    # 3) Compute layout per component (and keep the circle packing for alignment).
    layout_circles_pairs = [layout_circle_packing(comp, return_circles=True) for comp in components]

    # 4) Align components horizontally.
    align_layouts(layout_circles_pairs)

    with_labels = kwds.get("with_labels", False)
    show = kwds.get("show", False)

    # Merge per-component layouts into a joint layout.
    joint_layout, joint_circles = {}, {}
    for layout, circles in layout_circles_pairs:
        joint_layout.update(layout)
        joint_circles.update(circles)

    # Prepare axes.
    ax = kwds.get("ax", None)
    if ax is None:
        _, ax = plt.subplots()
        ax = plt.gca()

    # (Optional) visualize circle regions used in packing.
    align_layouts(layout_circles_pairs)  # keeps relative spacing if recomputed upstream
    if _PLOT_CIRCLES:
        _plot_circles(supported_k, joint_circles, ax=ax)

    # 5) Render.
    draw_from_layout(supported_k, joint_layout, ax=ax, with_labels=with_labels)

    if show:
        plt.show()


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
                zorder=_Z_CIRCLES,
            )
        )


if __name__ == "__main__":
    pass