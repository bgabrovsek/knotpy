"""Draw a planar graph from a PlanarGraph object.
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

__all__ = ['draw', 'export_pdf', "circlepack_layout"]
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


def circlepack_layout(k):
    """Return a layout for knot k. A layout is"""

    _debug = False
    external_node_radius = 1.0  # radius of external circles corresponding to nodes
    external_arc_radius = 0.5  # radius of external circles corresponding to arcs

    if _debug: print("Graph is", k)

    regions = list(kp.regions(k))
    if _debug: print("Regions are", regions)

    external_region = min(regions, key=lambda r: (-len(r), r))  # sort by longest, then by lexicographical order
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
    internal_circles |= {arc: [ep_to_reg_dict[arc[1]], arc[0].node, ep_to_reg_dict[arc[0]], arc[1].node] for arc in arcs}

    internal_circles = {key: internal_circles[key] for key in internal_circles if key not in external_circles}

    return CirclePack(internal=internal_circles,
                      external=external_circles)


def draw(g, node_size=0.25, line_width=3.5, draw_circles=True):
    #print()
    #print("Drawing graph", g)

    default_node_color = "black"
    default_arc_color = "steelblue"
    default_circle_alpha = 0.15
    default_circle_color = "cadetblue"

    circles = circlepack_layout(g)

    # plot
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.axis('off')

    arcs = g.arcs.keys()
    #print("Arcs are", arcs)

    # plot circles
    if draw_circles:
        for center, radius in circles.values():
            circle_patch = plt.Circle((center.real, center.imag), radius,
                                      alpha=default_circle_alpha,
                                      facecolor=default_circle_color,
                                      ls="none")
            ax.add_patch(circle_patch)

    # plot arcs
    for arc in arcs:
        z0 = circles[arc[0].node][0]
        z1 = circles[arc][0]
        z2 = circles[arc[1].node][0]
        path = bezier(z0, z1, z2)
        ax.add_patch(patches.PathPatch(path,
                                       facecolor='none',
                                       lw=line_width,
                                       edgecolor=default_arc_color))

    # plot nodes
    for node in g.nodes:
        center, radius = circles[node]
        circle_patch = plt.Circle((center.real, center.imag), node_size / 2,
                                  color=g.nodes[node].attr.get("color", default_node_color))
        ax.add_patch(circle_patch)

    if len(str(g.name)) > 0:
        ax.set_title(str(g.name))

    plt.autoscale()
    #plt.show()
    #plt.savefig("/Users/bostjan/Dropbox/Code/knotpy/knotpy/drawing/figs/x.png")

    return None


def export_pdf(graphs, filename, author=None):
    # TODO: detect if one or more grpahs
    # TODO: autodetect extension
    pdf = PdfPages(filename)
    for g in [graphs] if isinstance(graphs, PlanarDiagram) else graphs:

        #print(g)
        #print(list(kp.regions(g)))
        draw(g)
        pdf.savefig()  # saves the current figure into a pdf page
        #plt.show()
        plt.close()

    if author is not None:
        pdf.infodict()["Author"] = author

    pdf.close()




if __name__ == '__main__':

    nots =  ["bcdef, afec, abed, ace, adcbf, aeb",]
    # "bcde, aef, afed, ace, adcfb, bec",
    # "bcde, aef, afd, ace, adfb, bec",
    # "bcd, ade, aef, afb, bfc, ced",
    # "bcd, aec, abefd, acf, bfc, ced",
    # "bcde, aef, afd, acfe, adfb, bedc",
    # "bcdef, afc, abfed, ace, adc, acb",
    # "bcde, aef, afd, acf, afb, bedc",
    # "bcde, aefc, abfd, acfe, adfb, bedc"]
    #
    # graphs = kp.loadtxt_multiple("/Users/bostjan/Dropbox/Code/knotpy/knotpy/drawing/data/polyhedra-?-1.txt",
    #                              notation="plantri", prepended_node_count=True)
    #
    # print("Number of graphs:", len(graphs))
    #
    # g1= kp.from_plantri_notation("bcde, aec, abfd, acfg, aghb, chgd, dfhe, egf")
    # g2= kp.from_plantri_notation("bcde, afgc, abhd, ache, adgf, beg, bfeh, cgd")
    #
    # print(g1)
    # print(g2)
    #
    # print()
    # g1.canonical()
    # g2.canonical()
    #
    # print(str(kp.to_adjacency_list(g1)).replace(" ",""))
    # print(str(kp.to_adjacency_list(g2)).replace(" ",""))
    #
    # exit()
    #
    # print("Number of graphs:", len(set(graphs)))
    #
    # exit()
    #
    # for i, g in enumerate(graphs):
    #     g.name = f"Graph {i} ({len(g)} nodes)"
    #     for v in g.nodes:
    #         if g.degree(v) == 3:
    #             g.nodes[v]["color"] = "brown"

    graphs = [kp.from_plantri_notation(n.replace(" ",""), ccw=True) for n in nots]

    #print(graphs)
    export_pdf(graphs,
               "/Users/bostjan/Dropbox/test.pdf")
    #draw(g, draw_circles=True)

    # circle pack
    pass
