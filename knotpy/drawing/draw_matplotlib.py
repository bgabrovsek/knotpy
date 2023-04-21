import knotpy as kp
import matplotlib
from collections import defaultdict
from circlepack import CirclePack
from matplotlib.path import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from itertools import chain
import matplotlib.colors as mcolors


def _bezier_function(z0, z1, z2, derivative=0):
    """Return Bézier curve as a function, or its derivative."""
    if derivative == 0:
        return lambda t: (1 - t) * ((1 - t) * z0 + t * z1) + t * ((1 - t) * z1 + t * z2)
    if derivative == 1:
        return lambda t: 2 * (1 - t) * (z1 - z0) + 2 * t * (z2 - z1)
    if derivative == 2:
        return lambda t: 2 * (z2 - 2 * z1 + z0)
    return None


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

def draw(g, node_size=0.25, line_width=3.5, draw_circles=False):
    _debug = True

    external_node_radius = 1.0  # radius of external circles corresponding to nodes
    external_arc_radius = 0.5  # radius of external circles corresponding to arcs

    default_node_color = "black"
    default_arc_color = "steelblue"
    default_circle_alpha = 0.2
    default_circle_color = "cadetblue"

    #external_circles = dict()  # radii of external circles, keys are circles, values are radii
    #internal_circles = dict()  # neighbourhood circles of internal circles {circle key: list of ordered surrounding circles}
    #ext_nodes, ext_arcs = dict(), dict()
    #int_nodes, int_arcs, int_regs = defaultdict(list), defaultdict(list), defaultdict(list)

    if _debug: print("Graph", g)

    regions = g.regions()
    external_region = min(regions, key=lambda r: (-len(r), r))  # sort by longest, then by lexicographical order

    # sorted(g.regions(), key=lambda r: (-len(r), r)) # sort by longest, then by lexicographical order
    if _debug: print("Internal regions", _repr(regions))
    if _debug: print("External regions", _repr(external_region))

    arcs = g.arcs()
    ep_to_arc_dict = {ep: arc for arc in arcs for ep in arc}
    ep_to_reg_dict = {ep: reg for reg in regions for ep in reg}
    if _debug: print("Arcs", arcs)

    regions.remove(external_region)

    """for ep in external_region:
        ext_nodes[ep[0]] = external_node_radius
        ext_arcs[ep_to_arc_dict[ep]] = external_arc_radius"""

    external_circles = {ep[0]: external_node_radius for ep in external_region} | \
                       {ep_to_arc_dict[ep]: external_arc_radius for ep in external_region}  # nodes & arcs

    # int_regs = {region: list(chain(*zip([(ep[0], ep_to_arc_dict[ep]) for ep in region]))) for region in regions}

    """for region in regions:  # internal regions
        for ep in region:
            int_regs[region].append(ep[0])  # connect region to node
            int_regs[region].append(ep_to_arc_dict[ep])  # connect region to arc"""

    internal_circles = {region: list(chain(*((ep[0], ep_to_arc_dict[ep]) for ep in region))) for region in regions}

    """
    for v in g.nodes:
        for v_pos, ep in enumerate(g.adj[v]):
            int_nodes[v].append(ep_to_arc_dict[(v, v_pos)])
            int_nodes[v].append(ep_to_reg_dict[(v, v_pos)])"""

    internal_circles |= {v: list(chain(
        *((ep_to_arc_dict[(v, v_pos)], ep_to_reg_dict[(v, v_pos)]) for v_pos, ep in enumerate(g.adj[v]))
    )) for v in g.nodes}


    """for arc in arcs:
        int_arcs[arc].append(arc[0][0])
        int_arcs[arc].append(ep_to_reg_dict[arc[1]])
        int_arcs[arc].append(arc[1][0])
        int_arcs[arc].append(ep_to_reg_dict[arc[0]])"""

    internal_circles |= {arc: [arc[0][0], ep_to_reg_dict[arc[1]], arc[1][0], ep_to_reg_dict[arc[0]]] for arc in arcs}

    internal_circles = {key: internal_circles[key] for key in internal_circles if key not in external_circles}

    circles = CirclePack(internal=internal_circles,
                         external=external_circles)

    print(circles)

    # plot
    fig, ax = plt.subplots()
    ax.set_aspect('equal')

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
        z0 = circles[arc[0][0]][0]
        z1 = circles[arc][0]
        z2 = circles[arc[1][0]][0]
        path = bezier(z0, z1, z2)
        ax.add_patch(patches.PathPatch(path,
                                       facecolor='none',
                                       lw=line_width,
                                       edgecolor=default_arc_color))

    # plot nodes
    for node in g.nodes:
        center, radius = circles[node]
        circle_patch = plt.Circle((center.real, center.imag), node_size / 2,
                                  color=g.nodes[node].get("color", default_node_color))
        ax.add_patch(circle_patch)


    plt.autoscale()
    plt.show()

    return None


if __name__ == '__main__':
    g = kp.from_plantri_notation("bcde,aedf,afgh,ahbe,adb,bhgc,cfh,cgfd")
    for v in g.nodes:
        if g.degree(v) == 3:
            g._node_attr[v]["color"] = "brown"

    # g = kp.from_plantri_notation("bed,ac,bde,ca,ac")
    # g = kp.from_plantri_notation("bc,ac,ab")
    draw(g)

    # circle pack
    pass
