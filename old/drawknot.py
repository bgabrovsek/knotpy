from circlepack import CirclePack
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.colors as mpl_color
from matplotlib.backends.backend_pdf import PdfPages
from timer import *

from knotted import *
from math import sqrt

THICK = False

def arcQ(x): return isinstance(x, int)
def crQ(x): return isinstance(x, tuple) and isinstance(x[0], int)
def areaQ(x): return isinstance(x, tuple) and isinstance(x[0], tuple)

def tup(z):
    if isinstance(z, complex):
        return z.real, z.imag
    elif isinstance(z, float):
        return z, 0.0
    else:
        return tuple(z)

def perp_vec(z):
    return (complex(z.imag, -z.real)/ abs(z), complex(-z.imag, z.real)/abs(z))


def node_by_key(K, key):
    for node in K.nodes:
        if node.tuple() == key:
            return node
    return None

def bezier_function(z0,z1,z2,derivative=0):
    # returns bezier function of t, or its derivative
    if derivative == 0:
        # 0th derivative (curve), P(t) = (1-t)((1-t)p0+tp1)+t((1-t)p1+tp2)
        return lambda t: (1 - t) * ((1 - t) * z0 + t * z1) + t * ((1 - t) * z1 + t * z2)
    if derivative == 1:
        # 1st derivative, P'(t) = 2(1-t)(p1-p0) +2t(p2-p1)
        return lambda t: 2 * (1 - t) * (z1 - z0) + 2 * t * (z2 - z1)
    if derivative ==2 :
        # 2nd derivative, P''(t) = 2(p2-2p1+p0)
        return lambda t: 2 * (z2 - 2 * z1 + z0)
    return None



def bezier(*z, straight_lines=False):
    """
    draw bezier curve (deg 1 or deg 2)
    :param z: list of coordinates as complex numbers
    :return: return path
    """
    vertices = [tup(w) for w in z]
    codes = [Path.MOVETO] + [Path.LINETO if straight_lines else Path.CURVE3]*(len(z)-1)
    return Path(vertices, codes)
    #patch = patches.PathPatch(path, facecolor='none', lw=width, edgecolor=arc_colors[0])


def plot_circles(K, circles, width=3, gap=5, arrow_length=1.0, enumerate_arcs = True, text_distance = 2):
    """
    Draw the actual knot
    :param K:
    :param circles:
    :param width:
    :param gap:
    :param arrow_length:
    :param enumerate_arcs:
    :param text_distance:
    :return:
    """
    global THICK
    if THICK:
        width = 3
        gap = 5
        arrow_length = 1.0
    else:
        width = 1.5
        gap = 2.5
        arrow_length = 0.5
        enumerate_arcs = False



    show_circles = False
    arc_colors = ["tab:blue", "black", "tab:red", "tab:purple", "tab:orange"]

    circle_values = [circles[i] for i in circles] # all values of dictionary (center, radius)
    x_min = min(c.real - r for c, r in circle_values)
    x_max = max(c.real + r for c, r in circle_values)
    y_min = min(c.imag - r for c, r in circle_values)
    y_max = max(c.imag + r for c, r in circle_values)

    fig, ax = plt.subplots()
    ax.set(xlim=(x_min, x_max), ylim = (y_min, y_max), aspect=1.0)
    plt.axis('off')
    # DRAW THE CIRCLES
    if show_circles:
        for key in circles:
            c, r = circles[key]
            circ = plt.Circle((c.real, c.imag), r, color="palegreen" if areaQ(key) else ("pink" if arcQ(key) else "lightblue"))
            text = plt.text(c.real, c.imag, str(key), fontsize=r*5/sqrt(len(str(key))), verticalalignment='center', horizontalalignment='center',color="navy")
            ax.add_artist(circ)
            ax.add_artist(text)

    # DRAW KNOT
    for key in circles:

        # DRAW ARCS
        if arcQ(key):

            adj_nodes = tuple(k for k in circles if crQ(k) and (key in (k[:-1] if len(k) == 5 else k)))  # TODO: does not work for vertices of degree 5

            if len(adj_nodes) == 1:
                raise ValueError("Cannot process loops yet.")
            elif len(adj_nodes) == 2:
                key_a, key_b = adj_nodes
            else:
                raise ValueError("Arc does not have two adjacent crossings.")

            # determine correct orientation (out node) -> (arc) -> (in node), to adjust arrows
            node_a, node_b = node_by_key(K, key_a), node_by_key(K, key_b)
            pos_a, pos_b = node_a.index(int(key)), node_b.index(int(key))
            if node_a.outQ(pos_a) and node_b.inQ(pos_b): key_a, key_b = key_b, key_a

            # extract the circles
            (a, ar), (b, br), (c, cr) = circles[key_a], circles[key_b], circles[key]

            # add bezier curve

            z0, z1, z2 = a + (c-a)*ar/(ar+cr), c, b + (c-b)*br/(br+cr)
            path = bezier(z0, z1, z2)

            patch = patches.PathPatch(path, facecolor='none', lw=width, edgecolor=arc_colors[K.color(key)])
            ax.add_artist(patch)

            # add arrows

            P = bezier_function(z0,z1,z2)
            PP = bezier_function(z0,z1,z2, derivative=1)

            pt = P(0.5)
            tang = PP(0.5) / abs(PP(0.5))
            norm1, norm2 = perp_vec(tang)

            # draw arrows
            if arrow_length > 0:
                path = bezier(pt+(norm1+tang)*arrow_length, pt, pt + (norm2 + tang) * arrow_length, straight_lines=True)
                patch = patches.PathPatch(path, facecolor='none', lw=width, edgecolor=arc_colors[K.color(key)], capstyle='round')
                ax.add_artist(patch)

            # draw arc labels
            if enumerate_arcs:
                tpt = pt + (norm1-tang)*text_distance
                plt.text(tpt.real, tpt.imag,
                            str(key),
                            fontsize=10, verticalalignment='center', horizontalalignment='center', color=arc_colors[K.color(key)])

        # nodes

        if crQ(key):
            c, cr = circles[key] # get center and radius

            # crossing

            if len(key) == 5:

                # under arcs
                (a, ar), (b, br) = circles[key[0]], circles[key[2]]
                path = bezier(a + (c - a) * ar / (ar + cr), c, b + (c - b) * br / (br + cr))
                patch = patches.PathPatch(path, facecolor='none', lw=width, edgecolor=arc_colors[K.color(key[0])])
                ax.add_artist(patch)

                # over_arc
                (a, ar), (b, br) = circles[key[1]], circles[key[3]]
                path = bezier(a + (c - a) * ar / (ar + cr), c, b + (c - b) * br / (br + cr))
                patch = patches.PathPatch(path, facecolor='none', edgecolor="white", lw=width+2*gap)
                ax.add_artist(patch)
                patch = patches.PathPatch(path, facecolor='none', lw=width, edgecolor=arc_colors[K.color(key[1])])
                ax.add_artist(patch)

            elif len(key) == 3:
                color = {i:K.color(i) for i in key} # dictionary of arc: color
                #print(key, color.values())
                #if len(set(color.values())) == 2:
                if True:
                    # data & b are of same color, f is different, draw arc accordingly
                    if color[key[0]] == color[key[1]]: (a, ar), (b, br), (f, fr), color2, color1 = circles[key[0]], circles[key[1]], circles[key[2]], color[key[0]], color[key[2]]
                    if color[key[0]] == color[key[2]]: (a, ar), (b, br), (f, fr), color2, color1 = circles[key[0]], circles[key[2]], circles[key[1]], color[key[0]], color[key[1]]
                    if color[key[1]] == color[key[2]]: (a, ar), (b, br), (f, fr), color2, color1 = circles[key[1]], circles[key[2]], circles[key[0]], color[key[1]], color[key[0]]

                    # add data-b arc of crossing
                    path = bezier(a + (c - a) * ar / (ar + cr), c, b + (c - b) * br / (br + cr))
                    patch = patches.PathPatch(path, facecolor='none', lw=width, edgecolor=arc_colors[color2])
                    ax.add_artist(patch)

                    # add single f arc
                    z_mid = bezier_function(a + (c - a) * ar / (ar + cr), c, b + (c - b) * br / (br + cr))(0.5)
                    path = bezier(z_mid, c,  f + (c - f) * fr / (fr + cr))
                    patch = patches.PathPatch(path, facecolor='none', lw=width, edgecolor=arc_colors[color1])
                    ax.add_artist(patch)

                    # take average color for node
                    rgb1, rgb2 = mpl_color.to_rgb(arc_colors[color2]), mpl_color.to_rgb(arc_colors[color1])
                    rgb = ((rgb1[0]+rgb2[0])/2, (rgb1[1]+rgb2[1])/2, (rgb1[2]+rgb2[2])/2)

                    circ = plt.Circle((z_mid.real, z_mid.imag), width*0.2, color=rgb)
                    ax.add_artist(circ)

                #else:
                 #   raise ValueError("Vertex "+str(key)+" does not have two colors.")

                #(data, ar), (b, br) = [circles[key[i]] for i in key if ]


                pass

            elif len(key) == 2:
                pass

            else:
                raise ValueError("Unknown node type:" + str(key)+".")



    #return plt
    #plt.show()



def test_draw_circle_packing():
    inter = {9: [4,5,6,10,11], 5:[4,8,6,9], 8:[3,2,7,6,5,4],7:[8,2,1,6]}
    exter = {i:10.0 for i in (1,2,3,4,6,10,11)}
    ret = CirclePack(inter, exter)
    print(ret)
    plot_circles(ret)



def test_draw_circle_packing_hopf():
    inter = {2: [6,4,7,5], 3:[7,4,8,5], 6:[1,4,2,5],7:[2,4,3,5],8:[0,4,3,5]}
    exter = {0:5.0,1:5.0,4:10.0,5:10.0}
    ret = CirclePack(inter, exter)
    #ret = CirclePack({0:[1,2,3]}, {1:10,2:10,3:10})

    print(ret)
    plot_circles(ret)




def test_draw_circle_packing_tref():

    inter = {2:[11,9,12,7], 6:[8,13,9,11], 4:[8,11,7,10], 11:[8,6,9,2,7,4], 10:[8,4,7,1], 12:[2,9,5,7], 13:[3,9,6,8]}
    exter = {1:20, 7:20, 5:20, 9:20, 3:20, 8:20}

    #ex = {1,5,3,7,9,8}
    #exter = {e:10 for e in ex}


    #inter = {11:[1,7,9,2,3,8],2:[11,9,5,7]}

    ret = CirclePack(inter, exter)

    #ret = CirclePack({0:[1,2,3]}, {1:10,2:10,3:10})

    print(ret)
    plot_circles(ret)


def draw_knot(K):
    """
    Draws data knot
    :param K:
    :return:
    """

    #print("Drawing", K)


    external_radius_crs = 10.0  # radius of external circles corresponding to crossings
    external_radius_arc = 6.0  # radius of external circles corresponding to arcs
    areas = [tuple(a) for a in K.CCW_areas()] # turn areas into tuples (as they will be circle keys)

    # choose the external area as the longest one
    max_area_size = max(len(a) for a in areas)
    max_areas = [a for a in areas if len(a) == max_area_size]
    external_area = min(max_areas) # out of longest area, chose the alphabetically smallest one

    external = dict()  # radii of external circles {circle key: radii}
    internal = dict()  # neighbourhood circles of internal circles {circle key: list of ordered surrounding circles}

    # EXTERNAL CIRCLES

    for arc, ccw_b in external_area[::-1]:
        cr, pos = K.D(arc)[not ccw_b] # TODO: is CCW direction OK? It probably does not matter.
        external[arc] = external_radius_arc
        external[cr.tuple()] = external_radius_crs

    for a in areas: internal[a] = [] # add areas to interior circles
    for a in K.arcs(): internal[a] = []        # add arcs to interior circles
    for node in K.nodes: internal[node.tuple()] = [] # add arcs to interior circles

    # add internal area circles connections
    for a in areas:
        # append all arcs and crossings to it
        for arc, ccw_b in a:
            ccw_cr, ccw_pos = K.D(arc)[ccw_b] # TODO: is CCW direction OK? It probably does not matter.
            internal[a].append(arc)
            internal[a].append(ccw_cr.tuple())

    # add internal arc circles
    for arc in K.arcs():
        if arc in external: continue
        true_area, false_area = None, None
        (cr0, pos0), (cr1, pos1) = K.D(arc)
        for a in areas:
            if (arc, True) in a: true_area = a
            if (arc, False) in a: false_area = a
        internal[arc] += [cr1.tuple(), true_area, cr0.tuple(), false_area]

    # add internal crossings
    for node in K.nodes:
        for pos in node:
            arc = node[pos]
            arc_dir = (arc,True) if node.outQ(pos) else (arc,False)
            area = [a for a in areas if arc_dir in a][0] # get the area
            internal[node.tuple()].append(arc)
            internal[node.tuple()].append(area)



    # remove external keys from internal, since they should be disjoint
    del internal[external_area]
    for key in external:
        if key in internal: del internal[key]

    # reverse everything, since we are having the wrong orientation the whole time
    for key in internal:
        internal[key].reverse()

    #print(K.export())
    #print(K)
    #print("EX", external)
    #print("IN", internal)

    #print(K.bridgeQ(), K.bridge_crossingQ())

    #print(K.areas())
    # pack the circles"

    #print("ex",K)
    ret = CirclePack(internal, external)

    plot_circles(K, ret)


def PDF_export_knots(KNOTS, pdf_filename):

    print("Exporting",len(KNOTS),"knots to", pdf_filename)

    ticker = dot_counter()
    count, prev_perc = 0, None

    with PdfPages(pdf_filename) as pdf:

        for K in KNOTS:

            percent = int(1000 * count / len(KNOTS)) / 10
            if prev_perc != percent:
                print("\r" + str(percent) + "%", end="", flush=True)
                prev_perc = percent

            count += 1

            #print("Drawing",K)
            ticker.tick()

            draw_knot(K)
            if K.name:
                plt.title(str(K.name))
            else:
                plt.title(str(K))
            pdf.savefig()  # saves the current figure into data pdf page
            plt.close()

        d = pdf.infodict()
        d['Author'] = 'Bostjan Gabrovsek'
        print("DONE.")

    ticker.end()



def plot_knot(knot, filename):

    with PdfPages(filename) as pdf:

        draw_knot(knot)
        if knot.name:
            plt.title(str(knot.name))
        else:
            plt.title(str(knot))
        pdf.savefig()  # saves the current figure into data pdf page
        plt.close()

        d = pdf.infodict()
        d['Author'] = 'Bostjan Gabrovsek'
        #print("DONE.")

from test_knots import *


export_knots([K], "slika.pdf")

#for K in TEST[1:]:
#    print(K)
#    draw_knot(K)
#test_draw_circle_packing_tref()


#test_draw_circle_packing()

#print(ret)