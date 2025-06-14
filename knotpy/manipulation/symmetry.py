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
        for c in crossings:
            permute_node(k, c, (1, 2, 3, 0))
    else:
        for c in crossings:
            permute_node(k, c, (1, 2, 3, 0))

    return k
    # a → X(d0 b1 c1 c0), b → X(e0 a1 c3 c2), c → X(a3 a2 b3 b2), d → V(a0), e → V(b0) with framing 0


def flip(k:PlanarDiagram, nodes=None, inplace=False):
    """Flip the diagram by 180 degrees. This should not change the knot type or planar diagram type in S^3 and R^3.
        :param k:
        :return:
        """
    if not inplace:
        k = k.copy()

    if nodes is None:
        nodes = list(k.nodes)

    for node in nodes:
        permute_node(k, node, list(range(k.degree(node) - 1, -1, -1)))


    # reverse crossing order
    # for c in list(k.crossings):
    #     permute_node(k, c, {0:3,1:2,2:1,3:0})

    return k
