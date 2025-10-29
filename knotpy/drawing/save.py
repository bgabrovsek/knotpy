"""
Export utilities for rendering planar diagrams to PDF.

This module provides two helpers:

- `export_pdf`: render one or many diagrams, one per page.
- `export_pdf_groups`: render groups of diagrams in grids, one grid per page.

Both functions rely on `knotpy.drawing.draw.draw` for rendering and add light
error handling so that problematic diagrams still produce a page with a visible
error marker.
"""

import math

from knotpy.classes.planardiagram import Diagram
from knotpy.drawing.draw import draw
from knotpy.notation.native import to_knotpy_notation
from knotpy.utils.progressbar import bar
import knotpy.drawing.drawing_defaults as DEFAULTS

__all__ = ["export_pdf", "export_pdf_groups", "save_drawing"]
__version__ = "0.2"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

DEFAULTS._DEFAULT_IGNORE_DRAWING_ERRORS = False
DEFAULTS._DEFAULT_SHOW_PROGRESS = True

def _draw_error_diagram(k: Diagram, error_text, ax=None) -> None:
    """Draw a simple placeholder (“X”) and a short error note.

    Args:
        k: The diagram that failed to render.
        error_text: A string or list of strings describing the error(s).
        ax: Optional matplotlib Axes to draw into. If omitted, uses `plt.gca()`.
    """
    # Local import to keep module import fast.
    import matplotlib.pyplot as plt

    ax = ax or plt.gca()
    x_values_1, y_values_1 = [0, 1], [0, 1]
    x_values_2, y_values_2 = [0, 1], [1, 0]

    ax.plot(x_values_1, y_values_1, color="blue", linewidth=2)
    ax.plot(x_values_2, y_values_2, color="blue", linewidth=2)

    msg = error_text if isinstance(error_text, str) else ", ".join(error_text)
    ax.text(0.5, 0.5, f"Error ({msg})", ha="center", va="center",
            fontsize=12, color="red", weight="bold")

    title = str(k.name) if (k.name is not None and len(str(k.name)) > 0) else k.__class__.__name__
    ax.set_title(title)

    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.5, 1.5)
    ax.set_aspect("equal")
    ax.axis("off")


def export_pdf(
    diagrams,
    filename: str,
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
    show_progress=DEFAULTS._DEFAULT_SHOW_PROGRESS,
    ignore_errors=DEFAULTS._DEFAULT_IGNORE_DRAWING_ERRORS,
    ) -> None:

    """Render planar diagram(s) to a multi-page PDF (one diagram per page).

    If any diagram cannot be drawn (e.g., contains unsupported features),
    a placeholder page with an “X” and a brief error message is written instead.

    Args:
        diagrams: A `PlanarDiagram` or an iterable of `PlanarDiagram` objects.
        filename: Output PDF path.
        show_progress: If True and 10+ diagrams, shows a progress bar.

    Returns:
        None
    """
    #TODO: minimize the number of arguments by adding **kwargs with non-essential arguments (alpha,...)

    args = dict(locals())

    # Local imports to keep import time small.
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    diagrams = [diagrams] if isinstance(diagrams, Diagram) else list(diagrams or [])
    show_progress = show_progress and len(diagrams) >= 10

    if plt.get_fignums():  # close any open figures to avoid mixing content
        plt.close()

    pdf = PdfPages(filename)

    draw_args = {k:v for k,v in args.items() if k not in ("diagrams", "filename", "show_progress", "ignore_errors")}

    try:
        iterator = bar(diagrams, comment="exporting to PDF") if show_progress else diagrams
        for k in iterator:
            fig, ax = plt.subplots()
            if ignore_errors:
                try:
                    draw(k, **draw_args, show=False, ax=ax)
                except Exception as e:
                    _draw_error_diagram(k, str(e), ax=ax)
            else:
                draw(k, **draw_args, show=False, ax=ax)

            # Save the current figure to the PDF and close it to free memory.
            #pdf.savefig(bbox_inches="tight", pad_inches=0)
            pdf.savefig(fig, pad_inches=0)
            plt.close()
    finally:
        pdf.close()


def _flatten_axes(axes):
    """Flatten a matplotlib axes object into a simple list without NumPy.

    Args:
        axes: A single Axes, a 1D/2D list/tuple of Axes, or a nested structure.

    Returns:
        list: A flat list of Axes.
    """
    if axes is None:
        return []
    if hasattr(axes, "flatten") and not isinstance(axes, (list, tuple)):
        # Matplotlib often returns a numpy-like array with .flatten()
        return list(axes.flatten())
    if isinstance(axes, (list, tuple)):
        flat = []
        for item in axes:
            flat.extend(_flatten_axes(item))
        return flat
    return [axes]


def export_pdf_groups(
    groups,
    filename: str,
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
    show_progress=DEFAULTS._DEFAULT_SHOW_PROGRESS,
    ignore_errors=DEFAULTS._DEFAULT_IGNORE_DRAWING_ERRORS,
) -> None:
    """Render groups of diagrams in grids; one grid per PDF page.

    Each item in `groups` is a sequence (list/tuple/set) of diagrams. For each
    group, a near-square grid (rows × cols) is chosen and the diagrams are drawn
    into that grid on a single page.

    Args:
        groups: Iterable of diagram groups, where each group is an iterable of
            `PlanarDiagram` objects.
        filename: Output PDF path.
        draw_circles: If True, also draws auxiliary packing circles (debugging).
        with_labels: If True, draw node/endpoint/arc labels.
        with_title: If True, add per-diagram titles as in `export_pdf`.
        show_progress: If True and total diagrams across all groups ≥ 10, show a progress bar.

    Returns:
        None

    Raises:
        TypeError: If `groups` is not a sequence of sequences.
    """
    #TODO: minimize the number of arguments by adding **kwargs with non-essential arguments (alpha,...)


    args = dict(locals())

    # Local imports to keep import time small.
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    if not isinstance(groups, (list, set, tuple)):
        raise TypeError("groups must be a list/tuple/set of groups")
    groups = list(groups)
    if not groups:
        return
    if not isinstance(next(iter(groups)), (list, set, tuple)):
        raise TypeError("groups must be a sequence of sequences (each a group of diagrams)")

    total = sum(len(g) for g in groups)
    show_progress = show_progress and total >= 10

    if plt.get_fignums():
        plt.close()

    pdf = PdfPages(filename)
    draw_args = {k:v for k,v in args.items() if k not in ("groups", "filename", "show_progress", "ignore_errors")}

    try:
        iterator = bar(groups, comment="exporting to PDF") if show_progress else groups
        for group in iterator:
            group = list(group)
            n = len(group)
            if n == 0:
                # still generate an empty page for consistency
                fig = plt.figure()
                pdf.savefig(bbox_inches="tight", pad_inches=0.05, dpi=plt.gcf().dpi)
                plt.close()
                continue

            cols = math.ceil(math.sqrt(n))
            rows = math.ceil(n / cols)
            fig, axes = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows))
            axes_list = _flatten_axes(axes)

            # Draw each diagram into its own Axes; extras (if any) are hidden.
            for k, ax in zip(group, axes_list):

                if ignore_errors:
                    try:
                        draw(k, **draw_args, show=False, ax=ax)
                    except Exception as e:
                        _draw_error_diagram(k, str(e), ax=ax)
                else:
                    draw(k, **draw_args, show=False, ax=ax)

                # try:
                #     draw(k, draw_circles=draw_circles, with_labels=with_labels, with_title=with_title, ax=ax)
                # except Exception as e:
                #     _draw_error_diagram(k, str(e), ax=ax)

            # Hide any leftover axes if grid larger than group size.
            for ax in axes_list[len(group):]:
                ax.axis("off")

            #plt.tight_layout()
            pdf.savefig(bbox_inches="tight", pad_inches=0.05, dpi=plt.gcf().dpi)
            plt.close()
    finally:
        pdf.close()


def save_drawing(
        k: Diagram,
        filename: str,
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
        show_axis=DEFAULTS._DEFAULT_SHOW_AXIS
    ):
    args = dict(locals())
    from matplotlib import pyplot as plt
    args = {k: v for k, v in args.items() if k not in ("filename")}
    draw(**args, show=False)
    plt.savefig(filename, bbox_inches="tight", pad_inches=0.05, dpi=plt.gcf().dpi)
    plt.close()
