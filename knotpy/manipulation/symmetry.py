from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.manipulation.permute import permute_node


def mirror(k: PlanarDiagram, crossings=None, inplace=False):
    """Mirror a planar diagram in-place. If no crosssings are given, mirror the whole diagram
    :param k:
    :param crossings:
    :return:
    """

    if not inplace:
        k = k.copy()

    #print(crossings)
    if crossings is None:
        crossings = set(k.crossings)


    if k.is_oriented():
        raise NotImplementedError("Mirroring not implemented on oriented knots")
    else:
        for c in crossings:
            permute_node(k, c, (1, 2, 3, 0))

    return k
    # a → X(d0 b1 c1 c0), b → X(e0 a1 c3 c2), c → X(a3 a2 b3 b2), d → V(a0), e → V(b0) with framing 0


def flip(k:PlanarDiagram, inplace=False):
    """Flip the diagram by 180 degrees
        :param k:
        :param crossings:
        :return:
        """
    if not inplace:
        k = k.copy()

    for c in list(k.crossings):
        permute_node(k, c, {0:3,1:2,2:1,3:0})
    return k
