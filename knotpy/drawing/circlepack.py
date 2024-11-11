"""CirclePack.py
Compute circle packings according to the Koebe-Thurston-Andreev theory,
Following data numerical algorithm by C. R. Collins and K. Stephenson,
"A Circle Packing Algorithm", Comp. Geom. Theory and Appl. 2003.

AUTHORS: ...
"""

from math import pi, acos, sin, e

tolerance = 1 + 10e-12  # how accurately to approximate things

# ======================================================
#   The main circle packing algorithm
# ======================================================

def CirclePack(internal, external):
    """Find a circle packing for the given data.
    The two arguments should be dictionaries with disjoint keys; the
    keys of the two arguments are identifiers for circles in the packing.
    The internal argument maps each internal circle to its cycle of
    surrounding circles; the external argument maps each external circle
    to its desired radius. The return function is a mapping from circle
    keys to pairs (center,radius) where center is a complex number."""

    # Some sanity checks and preprocessing
    if min(external.values()) <= 0:
        raise ValueError("CirclePack: external radii must be positive")
    radii = dict(external)
    for k in internal:
        if k in external:
            raise ValueError("CirclePack: keys are not disjoint")
        radii[k] = 1   # Initial radii for internal circles are set to 1.

    # The main iteration for finding the correct set of radii
    lastChange = 2
    while lastChange > tolerance:
        lastChange = 1
        for k in internal:
            theta = flower(radii, k, internal[k])
            hat = radii[k] / (1 / sin(theta / (2 * len(internal[k]))) - 1)
            newrad = hat * (1 / (sin(pi / len(internal[k]))) - 1)
            kc = max(newrad / radii[k], radii[k] / newrad)
            lastChange = max(lastChange, kc)
            radii[k] = newrad

    # Recursively place all the circles
    placements = {}
    k1 = next(iter(internal))  # pick one internal circle
    placements[k1] = 0j  # place it at the origin
    k2 = internal[k1][0]  # pick one of its neighbors
    placements[k2] = radii[k1] + radii[k2]  # place it on the real axis
    place(placements, radii, internal, k1)  # recursively place the rest
    place(placements, radii, internal, k2)

    # conjugate the dictionary
    return dict((k, (placements[k], radii[k])) for k in radii)


# ======================================================
#   Invert a collection of circles
# ======================================================

def InvertPacking(packing, center):
    """Invert with specified center"""
    result = {}
    for k in packing:
        z, r = packing[k]
        z -= center
        if z == 0:
            offset = 1j
        else:
            offset = z / abs(z)
        p, q = z - offset * r, z + offset * r
        p, q = 1 / p, 1 / q
        z = (p + q) / 2
        r = abs((p - q) / 2)
        result[k] = z, r
    return result


def NormalizePacking(packing, k=None, target=1.0):
    """Make the given circle have radius one (or the target if given).
    If no circle is given, the minimum radius circle is chosen instead."""
    if k is None:
        r = min(r for z, r in packing.values())
    else:
        z, r = packing[k]
    s = target / r
    #return dict((kk, (zz * s, rr * s)) for kk, (zz, rr) in packing.iteritems())
    return dict((kk, (zz * s, rr * s)) for kk, (zz, rr) in packing.items())     # Correction: AttributeError: 'dict' object has no attribute 'iteritems'


def InvertAround(packing, k, smallCircles=None):
    """Invert so that the specified circle surrounds all the others.
    Searches for the inversion center that maximizes the minimum radius.

    This can be expressed as a quasiconvex program, but in a related
    hyperbolic space, so rather than applying QCP methods it seems
    simpler to use a numerical hill-climbing approach, relying on the
    theory of QCP to tell us there are no local maxima to get stuck in.

    If the smallCircles argument is given, the optimization
    for the minimum radius circle will look only at these circles"""
    z, r = packing[k]
    if smallCircles:
        optpack = {k: packing[k] for k in smallCircles}
    else:
        optpack = packing
    q, g = z, r * 0.4
    oldrad, ratio = None, 2
    while abs(g) > r * (tolerance - 1) or ratio > tolerance:
        rr, ignore1, ignore2, q = max(list(testgrid(optpack, k, z, r, q, g)))
        if oldrad:
            ratio = rr / oldrad
        oldrad = rr
        g *= 0.53 + 0.1j  # rotate so not always axis-aligned
    return InvertPacking(packing, q)


# ======================================================
#   Utility routines, not for outside callers
# ======================================================

def acxyz(x, y, z):
    """Angle at a circle of radius x given by two circles of radii y and z"""
    try:
        return acos(((x + y) ** 2 + (x + z) ** 2 - (y + z) ** 2) / (2.0 * (x + y) * (x + z)))
    except ValueError:
        return pi / 3
    except ZeroDivisionError:
        return pi


def flower(radius, center, cycle):
    """Compute the angle sum around a given internal circle"""
    return sum(acxyz(radius[center], radius[cycle[i - 1]], radius[cycle[i]])
               for i in range(len(cycle)))


def place(placements, radii, internal, center):
    """Recursively find centers of all circles surrounding k"""
    if center not in internal:
        return
    cycle = internal[center]
    for i in range(-len(cycle), len(cycle) - 1):
        if cycle[i] in placements and cycle[i + 1] not in placements:
            s, t = cycle[i], cycle[i + 1]
            theta = acxyz(radii[center], radii[s], radii[t])
            offset = (placements[s] - placements[center]) / (radii[s] + radii[center])
            offset *= e ** (-1j * theta)
            placements[t] = placements[center] + offset * (radii[t] + radii[center])
            place(placements, radii, internal, t)


def testgrid(packing, k, z, r, q, g):
    """Build grid of test points around q with grid size g"""
    for i in (-2, -1, 0, 1, 2):
        for j in (-2, -1, 0, 1, 2):
            center = q + i * g + j * 1j * g
            if abs(center - z) < r:
                newpack = InvertPacking(packing, center)
                newpack = NormalizePacking(newpack, k)
                minrad = min(r for z, r in newpack.values())
                yield minrad, i, j, center


# ======================================================
#   Mobius transformations
# ======================================================
def plot_packing(packing):
    import matplotlib.pyplot as plt
    figure, axes = plt.subplots()
    plt_circles = [plt.Circle((z.real, z.imag), r, alpha=0.2) for z, r in packing.values()]
    plt_points = [plt.plot(z.real, z.imag, 'ro') for z, r in packing.values()]
    #plt_labels = [plt.text(z.real, z.imag, str(k)) for k, (z, r) in packing.items()]
    axes.set_aspect(1)
    for i, circ in enumerate(plt_circles):
        axes.add_artist(circ)
        axes.add_artist(plt_points[i][0])
        #axes.add_artist(plt_labels[i])
    plt.title('Colored Circle')
    axes.relim()
    axes.autoscale_view()

    plt.show()

def plot_layout_packing(packing):
    import matplotlib.pyplot as plt
    figure, axes = plt.subplots()
    #plt_circles = [plt.Circle((z.real, z.imag), r, alpha=0.2) for z, r in packing.values()]
    #plt_points = [plt.plot(z.real, z.imag, 'ro') for z, r in packing.values()]
    #plt_labels = [plt.text(z.real, z.imag, str(k)) for k, (z, r) in packing.items()]
    plt_circles, plt_points, plt_labels = [], [], []
    for k, circle in packing.items():
        z = circle.center
        r = circle.radius
        plt_circles.append(plt.Circle((z.real, z.imag), r, alpha=0.2))
        plt_points.append(plt.plot(z.real, z.imag, 'ro'))
        #plt_labels.append(plt.text(z.real, z.imag, str(k)))

    axes.set_aspect(1)
    for i, circ in enumerate(plt_circles):
        axes.add_artist(circ)
        axes.add_artist(plt_points[i][0])
        #axes.add_artist(plt_labels[i])
    plt.title('Colored Circle')
    axes.relim()
    axes.autoscale_view()

    plt.show()



def mobius_transform(z, a, b, c, d):
    """Apply Möbius transformation to a complex point z."""
    return (a * z + b) / (c * z + d)

def apply_mobius_to_packing(packing, a, b, c, d):
    """Apply Möbius transformation to the circle packing."""
    transformed_packing = {}
    #for k, (z, r) in packing.items():
    for k, circle in packing.items():
        z = circle.center
        r = circle.radius
        new_z = mobius_transform(z, a, b, c, d)
        new_r = abs((a * r) / (c * z + d))  # Scaling the radius under the transformation
        transformed_packing[k] = (new_z, new_r)
    return transformed_packing

def normalize_radii(packing, max_ratio=2.0):
    """Normalize the packing to ensure all circles have radii within a factor of max_ratio."""
    # Find the smallest radius
    min_radius = min(r for _, r in packing.values())
    
    # Adjust all radii to be within [min_radius, min_radius * max_ratio]
    normalized_packing = {}
    #for k, (z, r) in packing.items():
    for k, circle in packing.items():
        z, r = circle.center, circle.radius
        new_r = max(min_radius, min(min_radius * max_ratio, r))
        normalized_packing[k] = (z, new_r)
    
    return normalized_packing

def find_smallest_radius_circle(circle_dict):
    """Find the key of the circle with the smallest radius in the dictionary."""
    smallest_key = None
    smallest_radius = float('inf')  # Start with an infinitely large radius
    smallest_position = None

    for key, circle in circle_dict.items():
        if circle.radius < smallest_radius:
            smallest_radius = circle.radius
            smallest_position = circle.center
            smallest_key = key

    
    return smallest_key, smallest_position, smallest_radius  # Return both the key and the smallest radius for reference



if __name__ == "__main__":

    """
    #external= {"a":1,"b":1,"c":1, "e":1, "g":1, "f":1}
    #internal={"d":["a","b","c", "e", "g","f"],"h":["a","b","c", "e", "g","f"]}
    # Four internal circles surrounded by three external circles
    external = {"a": 1, "b": 1, "c": 1}
    internal = {"d": ["a", "b", "c"], "e": ["a", "b", "c"], "f": ["d", "e", "a"]}
    # calls error KeyError: 'e'

    # Two levels of internal circles, internal circles surround the previous level of internal circles
    external = {"a": 1, "b": 1, "c": 1}
    internal = {
        "d": ["a", "b", "c"],  # First level
        "e": ["d", "a", "b"],  # Second level
        "f": ["d", "e", "c"]   # Second level
    }
    # same problem

    # Six external circles surrounding three internal circles
    external = {"a": 1, "b": 1, "c": 3, "d": 3, "e": 1, "f": 3}
    internal = {"g": ["a", "b", "c", "d", "e", "f"]}
    # already tried this and it works

    # Nested internal circles surrounded by several external circles
    external = {"a": 1, "b": 1, "c": 1, "d": 1, "e": 1}
    internal = {
        "f": ["a", "b", "c"],
        "g": ["b", "c", "d"],
        "h": ["c", "d", "e"],
        "i": ["a", "e", "f", "g", "h"]
    }
    # KeyError: 'd'

    # Mixed sizes for external circles, with internal circles of varying arrangements
    external = {"a": 1, "b": 1.5, "c": 0.75, "d": 1.25, "e": 1}
    internal = {"f": ["a", "b", "c", "d"], "g": ["b", "d", "e"]}
    # KeyError: 'e'

    # Test case with more external circles and two internal circles
    external = {"a": 1, "b": 1, "c": 1, "d": 1, "e": 1, "f": 1, "h": 1, "i": 1, "j": 1}
    internal = {"g": ["a", "b", "c", "d", "e", "f"], "k": ["h", "i", "j", "g"]}
    # KeyError: 'h'
    """

    external= {"a":1,(4,1):1,"c":1}
    internal={"d":["a",(4,1),"c"]}

    external= {"a":1,"b":1,"c":1}
    internal={"d":["a","b","c"]}

    ret = CirclePack(internal=internal, external=external)

    # Define the Möbius transformation parameters
    a, b, c, d = 1, 0, 0, 1  # Identity transformation (no change)
    a, b, c, d = 1, 1, 0, 1  
    # You can change these to adjust the transformation, e.g., try a = 1, b = 1, c = 0, d = 1


    ## Apply the Möbius transformation to the packing
    #transformed_packing = apply_mobius_to_packing(ret, a, b, c, d)
    ## Normalize the radii to avoid overlaps and maintain closeness in size
    #normalized_packing = normalize_radii(transformed_packing, max_ratio=2.0)  # Factor of 2    
    #norm_ret = normalize_radii(ret, max_ratio=2.0)
    #norm_ret = NormalizePacking(ret, k='a', target=1.0)
    ##mob_norm_ret = apply_mobi s_to_packing(norm_ret, a, b, c, d)

    import pprint
    #print(ret)
    pprint.pprint(ret)

    import matplotlib.pyplot as plt
    #plt.ion()

    #plot_packing(ret)
    #plot_packing(transformed_packing)
    #plot_packing(normalized_packing)
    #plot_packing(norm_ret)
    #plot_packing(mob_norm_ret)
    print("pl")


    #print(ret)
    from knotpy.drawing.layout import circlepack_layout
    from knotpy.notation.pd import from_pd_notation

    #s = "X[1, 3, 4, 5], X[2, 4, 3, 6], X[5, 6, 7, 8], X[8, 7, 9, 10], X[9, 11, 12, 13], X[10, 14, 15, 16], X[11, 16, 17, 18], X[12, 18, 19, 20], X[13, 20, 21, 14], X[15, 21, 19, 17], V[1], V[2]"
    s = "V[0,1,2],V[3,1,4],X[5,6,0,7],X[2,3,8,9],X[7,10,11,12],X[12,11,6,5],X[4,13,14,8],X[13,10,9,14]"
    
    s = "X[4,2,5,1],X[2,6,3,5],X[6,4,1,3]"
    #s = "X[1,9,2,8],X[3,10,4,11],X[5,3,6,2],X[7,1,8,12],X[9,4,10,5],X[11,7,12,6]"
    s = "X[0,1,2,3],X[4,5,6,7],X[1,8,9,10],X[11,12,13,9],X[14,15,7,16],X[17,18,19,13],X[10,20,17,12],X[20,19,15,14],V[3,21,22],V[5,23,24],V[6,24,16],V[4,18,23],V[0,22,8],V[2,11,21]"

    print("\n")
    print(s)
    k2 = from_pd_notation(s)
    print(k2)
    ret = circlepack_layout(k2)
    
    pprint.pprint(ret)
    for key, circle in ret.items():
        print(circle)
        print(f"Key: {key}, Transformed Center: {circle}, Transformed Radius: {circle}")


    eps = 1e-10
    #x = ret['d'][0] #+ eps
    smkey, x, smrad = find_smallest_radius_circle(ret)
    #x = ret['a'].center
    x = 1
    A, B = 1.05, 1.0
    a = (A + x)
    b = (B*x - A*x - x*x)
    c = 1
    d = (b - x)

    transformed_packing = apply_mobius_to_packing(ret, a, b, c, d)

    plot_layout_packing(ret)
    plot_packing(transformed_packing)

    import matplotlib.pyplot as plt
    from knotpy import kp
    pd = "X[0,1,2,3],X[4,5,6,7],X[1,8,9,10],X[11,12,13,9],X[14,15,7,16],X[17,18,19,13],X[10,20,17,12],X[20,19,15,14],V[3,21,22],V[5,23,24],V[6,24,16],V[4,18,23],V[0,22,8],V[2,11,21]"
    k = kp.from_pd_notation(pd)
    print(pd)
    kp.draw(k, draw_circles=True)
    plt.show()

