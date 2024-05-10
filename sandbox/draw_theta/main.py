from matplotlib.path import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages

import knotpy as kp
from knotpy.drawing.circlepack import CirclePack


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




def draw_diagram_from_layout(k, layout, node_size=0.25, line_width=3.5, draw_circles=True):

    default_node_color = "black"
    default_arc_color = "steelblue"
    default_circle_alpha = 0.15
    default_circle_color = "cadetblue"

    circles = layout  # run circle-packing


    # plot
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.axis('off')

    arcs = k.arcs.keys()

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
    for node in k.nodes:
        center, radius = circles[node]
        circle_patch = plt.Circle((center.real, center.imag), node_size / 2,
                                  color=k.nodes[node].attr.get("color", default_node_color))
        ax.add_patch(circle_patch)

    if len(str(k.name)) > 0:
        ax.set_title(str(k.name))

    plt.autoscale()
    #plt.show()
    #plt.savefig("/Users/bostjan/Dropbox/Code/knotpy/knotpy/drawing/figs/x.png")

    return None

if __name__ == '__main__':
    # PD code
    pd_code = "V[3,18,17],V[9,2,14],X[13,14,17,16],X[16,18,22,20],X[22,23,24,21],X[23,3,2,24],X[20,8,11,13],X[9,11,8,21]"

    # create knot
    knot = kp.from_pd_notation(pd_code)

    # a knot is given in EM notation
    print(knot)

    # create layout, that is, a system of circles associated to each vertex/edge/region in form of a dictionary
    layout = kp.circlepack_layout(knot)

    for circle in layout:
        center, radius = layout[circle]
        print("circle", circle, "center", center, "radius", radius)


    # draw diagram from layout
    draw_diagram_from_layout(knot, layout)

    # show diagram
    plt.show()
    # plt.savefig("slika.png")
    plt.close()



