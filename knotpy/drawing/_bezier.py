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
