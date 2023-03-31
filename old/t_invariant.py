from knotted import *


def T(knot):

    if not knot.filter_nodes(VQ):
        return [knot.copy()]

    knot1, knot2, knot3 = knot.copy(), knot.copy(), knot.copy()  # assume all are equal

    for i, k in enumerate([knot1, knot2, knot3]):
        vertex = k.filter_nodes(VQ)[0]  # select first vertex

        # arcs (join a and b)
        a, b, c = i, (i+1) % 3, (i+2) % 3

        # reroute arcs
        if vertex.inQ(a):
            biv = Bivalent(vertex[a], vertex[b])
        else:
            biv = Bivalent(vertex[b], vertex[a])

        endp = Endpoint(vertex[c], ingoing=vertex.inQ(c), color=vertex.color[c])

        k.append_node(biv)
        k.append_node(endp)
        k.remove_node(vertex)

        # TODO: take care of colors

        # TODO: fix orientations

    return T(knot1) + T(knot2) + T(knot3)
