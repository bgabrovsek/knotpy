"""Disjoint components are the diagram components that do not share a common node (crossing, vertex, ...).
"""

__all__ = ["closure"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.duality import dual_planar_diagram
from knotpy.algorithms.graph import bfs_shortest_path


def _face_intersection_arc(k:PlanarDiagram, f, g):
    """Find a intersection arc of F and G. If F contains arc (A,B), G should contain (B,A)
    :param f:
    :param g:
    :return:
    """

    for i in range(len(f)):
        f_pair = (f[i], f[(i + 1) % len(f)])
        for j in range(len(g)):
            g_pair = (g[j], g[(j + 1) % len(g)])
            if f_pair[0].node == g_pair[1].node and f_pair[1].node == g_pair[0].node and (f_pair[1].position + 1) % k.degree(f_pair[1].node) == g_pair[0].position:
                return f_pair[1], g_pair[1]
    return None



def closure(k: PlanarDiagram, underpass_closure=True):
    """

    :param k:
    :param underpass_closure:
    :return:
    """

    k = k.copy()

    leafs = list(v for v in k.vertices if k.degree(v) == 1)
    if len(leafs) != 2:
        raise ValueError("Can only close a diagram with two leafs")

    # get the two connected nodes
    A, B = leafs
    # dual planar graph
    dual = dual_planar_diagram(k)

    # get faces of the two leafs
    A_ep = k.endpoint_from_pair((A, 0))
    B_ep = k.endpoint_from_pair((B, 0))
    A_face = next(f for f in dual.vertices if A_ep in f)
    B_face = next(f for f in dual.vertices if B_ep in f)

    # the shortest path from the two endpoint faces will yield the arcs we must add to the structure
    path = bfs_shortest_path(dual, A_face, B_face)
    print("path:", " -> ".join(str(f) for f in path))

    print("start endpoint", A_ep, "end endpoint", B_ep)

    previous_endpoint = (A_ep.node, A_ep.position + 1)

    # loop through all neighbouring faces
    for f, g in zip(path, path[1:]):
        arc = _face_intersection_arc(k, f, g)  # find the arcs we must pass

        k


        print(f, "and", g, "int", arc)

    print(dual)

if __name__ == "__main__":

    import knotpy as kp

    k = kp.from_condensed_em_notation("b0,a0c3c1c0,b3b2d0b1,c2")
    k.name = "2_1"
    print(k)
    c=  closure(k)

    print()

    k = kp.from_condensed_em_notation("b1,c1a0c0d3,b2b0e1e0,f1f0g0b3,c3c2g3h0,d1d0h3h2,d2i0h1e2,e3g2f3f2,g1 & 7_45:b0,a0c0d0c1,b1b3e1e0,b2f3g1g0,c3c2g3h0,h3h2i0d1,d3d2h1e2,e3g2f1f0,f2")
    k.name = "7_44"
    print(k)
    c = closure(k)

    kp.draw(k)
    kp.plt.show()