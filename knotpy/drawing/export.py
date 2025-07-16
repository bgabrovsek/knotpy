import matplotlib.pyplot as plt
import math
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.drawing.draw import draw
from knotpy.notation.native import to_knotpy_notation
from knotpy.utils.progressbar import bar

_IGNORE_DRAWING_ERRORS = True

def _draw_error_diagram(k, error_text, ax=None):
    # Draw an "X".
    ax = ax or plt.gca()
    x_values_1, y_values_1, x_values_2, y_values_2 = [0, 1], [0, 1], [0, 1], [1, 0]

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

    for k in (bar(diagrams, comment="exporting to PDF") if show_progress else diagrams):

        if _IGNORE_DRAWING_ERRORS:
            try:
                draw(k,
                     draw_circles=draw_circles,
                     with_labels=with_labels,
                     with_title=with_title)
            except Exception as e:
                _draw_error_diagram(k, str(e))
        else:
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

    for group in (bar(groups, comment="exporting to PDF") if show_progress else groups):
        n = len(group)
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
        fig, axes = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows))  # Adjust size per diagram
        # TODO: do not use numpy
        axes = axes.flatten() if isinstance(axes, (list, np.ndarray)) else [axes]

        for k, ax in zip(group, axes):
            pass
            try:
                draw(k,
                     draw_circles=draw_circles,
                     with_labels=with_labels,
                     with_title=with_title,
                     ax=ax)
            except Exception as e:
                _draw_error_diagram(k, str(e), ax=ax)
            # draw(k,
            #      draw_circles=draw_circles,
            #      with_labels=with_labels,
            #      with_title=with_title,
            #      ax=ax)

        plt.tight_layout(pad=0)
        pdf.savefig(bbox_inches="tight", pad_inches=0)  # saves the current figure into a pdf page
        plt.close()

    # if author is not None:
    #     pdf.infodict()["Author"] = author

    pdf.close()


if __name__ == "__main__":
    import knotpy as kp
    s = """
    a=V(b0) b=X(a0 c3 d3 c0) c=X(b3 d2 d1 b1) d=X(e0 c2 c1 b2) e=X(d0 f0 f3 g3) f=X(e1 g2 g0 e2) g=X(f2 h0 f1 e3) h=V(g1)
    a=V(b0) b=X(a0 c0 c3 d3) c=X(b1 e3 e1 b2) d=X(f3 g0 e0 b3) e=X(d2 c2 h0 c1) f=X(i3 i2 g1 d0) g=X(d1 f2 i1 i0) h=V(e2) i=X(g3 g2 f1 f0)
    a=V(b0) b=X(a0 c3 d3 c0) c=X(b3 e0 e3 b1) d=X(f0 g3 h0 b2) e=X(c1 f2 f1 c2) f=X(d0 e2 e1 i0) g=X(j3 j2 h1 d1) h=X(d2 g2 j1 j0) i=V(f3) j=X(h3 h2 g1 g0)
    a=V(b3) b=X(c0 d0 d3 a0) c=X(b0 e3 f0 g3) d=X(b1 e2 e0 b2) e=X(d2 h0 d1 c1) f=X(c2 g2 i3 i2) g=X(i1 i0 f1 c3) h=V(e1) i=X(g1 g0 f3 f2)
    a=V(b0) b=X(a0 c3 d3 c0) c=X(b3 e0 e3 b1) d=X(f0 g0 h3 b2) e=X(c1 f2 f1 c2) f=X(d0 e2 e1 i0) g=X(d1 h2 j3 j2) h=X(j1 j0 g1 d2) i=V(f3) j=X(h1 h0 g3 g2)
    a=V(b0) b=X(a0 c3 d3 c0) c=X(b3 e0 e3 b1) d=X(f3 g3 h0 b2) e=X(c1 i0 i3 c2) f=X(i2 h3 g0 d0) g=X(f2 h2 h1 d1) h=X(d2 g2 g1 f1) i=X(e1 j0 f0 e2) j=V(i1)
    a=V(b0) b=X(a0 c0 c3 d0) c=X(b1 e3 e1 b2) d=X(b3 e0 f0 g3) e=X(d1 c2 h0 c1) f=X(d2 g2 i3 i2) g=X(i1 i0 f1 d3) h=V(e2) i=X(g1 g0 f3 f2)
    a=V(b0) b=X(a0 c3 d0 c0) c=X(b3 e0 e3 b1) d=X(b2 f3 g0 h0) e=X(c1 i0 i3 c2) f=X(h2 g2 g1 d1) g=X(d2 f2 f1 h1) h=X(d3 g3 f0 i2) i=X(e1 j0 h3 e2) j=V(i1)
    a=V(b3) b=X(c0 d0 d3 a0) c=X(b0 e3 f3 g0) d=X(b1 e2 e0 b2) e=X(d2 h0 d1 c1) f=X(i3 i2 g1 c2) g=X(c3 f2 i1 i0) h=V(e1) i=X(g3 g2 f1 f0)
    a=V(b0) b=X(a0 c0 c3 d3) c=X(b1 e3 e1 b2) d=X(f0 g3 e0 b3) e=X(d2 c2 h0 c1) f=X(d0 g2 i3 i2) g=X(i1 i0 f1 d1) h=V(e2) i=X(g1 g0 f3 f2)
    a=V(b3) b=X(c3 d0 c0 a0) c=X(b2 e0 e3 b0) d=X(b1 f3 g0 e2) e=X(c1 h0 d3 c2) f=X(i3 i2 g1 d1) g=X(d2 f2 i1 i0) h=V(e1) i=X(g3 g2 f1 f0)
    a=V(b3) b=X(c3 d0 c0 a0) c=X(b2 e0 e3 b0) d=X(b1 f0 g3 e2) e=X(c1 h0 d3 c2) f=X(d1 g2 i3 i2) g=X(i1 i0 f1 d2) h=V(e1) i=X(g1 g0 f3 f2)
    a=V(b0) b=X(a0 c0 c3 d0) c=X(b1 e3 e1 b2) d=X(b3 e0 f3 g0) e=X(d1 c2 h0 c1) f=X(i3 i2 g1 d2) g=X(d3 f2 i1 i0) h=V(e2) i=X(g3 g2 f1 f0)
    a=V(b0) b=X(a0 c3 d0 c0) c=X(b3 e0 e3 b1) d=X(b2 f3 g0 h0) e=X(c1 h2 h1 c2) f=X(i3 i2 g1 d1) g=X(d2 f2 i1 i0) h=X(d3 e2 e1 j0) i=X(g3 g2 f1 f0) j=V(h3)
    a=V(b0) b=X(a0 c3 d0 c0) c=X(b3 e0 e3 b1) d=X(b2 f0 g3 h0) e=X(c1 h2 h1 c2) f=X(d1 g2 i3 i2) g=X(i1 i0 f1 d2) h=X(d3 e2 e1 j0) i=X(g1 g0 f3 f2) j=V(h3)
    a=V(b3) b=X(c3 d0 c0 a0) c=X(b2 e0 e3 b0) d=X(b1 f3 g0 h0) e=X(c1 i0 h3 c2) f=X(h2 g2 g1 d1) g=X(d2 f2 f1 h1) h=X(d3 g3 f0 e2) i=V(e1)
    """
    s = s.strip().splitlines()
    k = [kp.from_knotpy_notation(_) for _ in s]
    for _ in k:
        print(_)
    print(k)
    import matplotlib.pyplot as plt
    export_pdf(k, "test.pdf", draw_circles=True, with_labels=True, with_title=True)
    export_pdf_groups([[k[0],k[1],k[3]], [k[4],k[5],k[6]]], "test_group.pdf", draw_circles=True, with_labels=True, with_title=True)
    plt.show()



