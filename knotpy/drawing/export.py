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

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.drawing.draw import draw
from knotpy.notation.native import to_knotpy_notation
from knotpy.utils.progressbar import bar

__all__ = ["export_pdf", "export_pdf_groups"]
__version__ = "0.2"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

_IGNORE_DRAWING_ERRORS = True


def _draw_error_diagram(k: PlanarDiagram, error_text, ax=None) -> None:
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
    draw_circles: bool = False,
    with_labels: bool = False,
    with_title: bool = False,
    show_progress: bool = True,
) -> None:
    """Render planar diagram(s) to a multi-page PDF (one diagram per page).

    If any diagram cannot be drawn (e.g., contains unsupported features),
    a placeholder page with an “X” and a brief error message is written instead.

    Args:
        diagrams: A `PlanarDiagram` or an iterable of `PlanarDiagram` objects.
        filename: Output PDF path.
        draw_circles: If True, also draws auxiliary packing circles (debugging).
        with_labels: If True, draw node/endpoint/arc labels.
        with_title: If True, add a title: uses `k.name` if present, otherwise
            uses the diagram’s KnotPy notation.
        show_progress: If True and 10+ diagrams, shows a progress bar.

    Returns:
        None
    """
    # Local imports to keep import time small.
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    diagrams = [diagrams] if isinstance(diagrams, PlanarDiagram) else list(diagrams or [])
    show_progress = show_progress and len(diagrams) >= 10

    if with_title:
        for k in diagrams:
            if k.name is None or len(str(k.name)) == 0:
                k.attr["_title"] = to_knotpy_notation(k)
            else:
                k.attr["_title"] = str(k.name)

    if plt.get_fignums():  # close any open figures to avoid mixing content
        plt.close()

    pdf = PdfPages(filename)

    try:
        iterator = bar(diagrams, comment="exporting to PDF") if show_progress else diagrams
        for k in iterator:
            if _IGNORE_DRAWING_ERRORS:
                try:
                    draw(k, draw_circles=draw_circles, with_labels=with_labels, with_title=with_title)
                except Exception as e:
                    _draw_error_diagram(k, str(e))
            else:
                draw(k, draw_circles=draw_circles, with_labels=with_labels, with_title=with_title)

            # Save current figure to the PDF and close it to free memory.
            #pdf.savefig(bbox_inches="tight", pad_inches=0)
            pdf.savefig(pad_inches=0)
            plt.close()
    finally:
        pdf.close()

    if with_title:
        for k in diagrams:
            k.attr.pop("_title", None)


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
    draw_circles: bool = False,
    with_labels: bool = False,
    with_title: bool = False,
    show_progress: bool = True,
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
                try:
                    draw(k, draw_circles=draw_circles, with_labels=with_labels, with_title=with_title, ax=ax)
                except Exception as e:
                    _draw_error_diagram(k, str(e), ax=ax)

            # Hide any leftover axes if grid larger than group size.
            for ax in axes_list[len(group):]:
                ax.axis("off")

            plt.tight_layout()
            pdf.savefig(bbox_inches="tight", pad_inches=0.05, dpi=plt.gcf().dpi)
            plt.close()
    finally:
        pdf.close()