# Closure of a knotoid

__all__ = ["closure"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.duality import dual_planar_diagram
from knotpy.algorithms.paths import bfs_shortest_path
from knotpy.manipulation.remove import remove_bivalent_vertices, remove_bivalent_vertex
from knotpy.algorithms.naming import unique_new_node_name


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


def _underpass_closure(k: PlanarDiagram, A, B, arcs):
    """
    Make an "underpass closure" of the diagram k, where A and B are degree-1 vertices (leafs) that will be closed and
    arcs is the set of arcs (list od tuples) through which the closure will pass.
    Each arc is oriented: the first endpoint is CCW with respect to the face of the path starting at A.
    """
    k = k.copy()
    # loop through all neighbouring faces and get the common arc that we must pass
    previous_open_endpoint = (A, 1)
    for ep_f, ep_g in arcs:
        crossing = unique_new_node_name(k)
        # insert the crossing and attach endpoints
        k.add_crossing(crossing_for_adding=crossing)
        k.set_arc((previous_open_endpoint, (crossing, 0)))
        k.set_arc((ep_f, (crossing, 3)))
        k.set_arc((ep_g, (crossing, 1)))
        previous_open_endpoint = (crossing, 2)
    #attach the final endpoints from the last node
    k.set_arc((previous_open_endpoint, (B, 1)))

    if k.degree(A) != 2 or k.degree(B) != 2:
        raise ValueError("The leafs should have degree 2 after closure")
    remove_bivalent_vertex(k, A)
    remove_bivalent_vertex(k, B)
    return k


def _overpass_closure(k: PlanarDiagram, A, B, arcs):
    """
    Make an "overpass closure" of the diagram k, where A and B are degree-1 vertices (leafs) that will be closed and
    arcs is the set of arcs (list od tuples) through which the closure will pass.
    Each arc is oriented: the first endpoint is CCW with respect to the face of the path starting at A.
    """
    k = k.copy()
    # loop through all neighbouring faces and get the common arc that we must pass
    previous_open_endpoint = (A, 1)
    for ep_f, ep_g in arcs:
        crossing = unique_new_node_name(k)
        # insert the crossing and attach endpoints
        k.add_crossing(crossing_for_adding=crossing)
        k.set_arc((previous_open_endpoint, (crossing, 1)))
        k.set_arc((ep_f, (crossing, 0)))
        k.set_arc((ep_g, (crossing, 2)))
        previous_open_endpoint = (crossing, 3)
    # attach the final endpoints from the last node
    k.set_arc((previous_open_endpoint, (B, 1)))

    if k.degree(A) != 2 or k.degree(B) != 2:
        raise ValueError("The leafs should have degree 2 after closure")
    remove_bivalent_vertex(k, A)
    remove_bivalent_vertex(k, B)
    return k

def _over_and_under_closure(k: PlanarDiagram, A, B, arcs):
    """
    Make an "double-sided over and under closure" of the diagram k, where A and B are degree-1 vertices (leafs) that will be closed and
    arcs is the set of arcs (list od tuples) through which the closure will pass.
    Each arc is oriented: the first endpoint is CCW with respect to the face of the path starting at A.
    """


    k = k.copy()
    # loop through all neighbouring faces and get the common arc that we must pass
    previous_open_endpoint_over = (A, 1)
    previous_open_endpoint_under = (A, 2)
    for ep_f, ep_g in arcs:
        crossing_over = unique_new_node_name(k)
        k.add_crossing(crossing_for_adding=crossing_over)
        crossing_under = unique_new_node_name(k)
        k.add_crossing(crossing_for_adding=crossing_under)
        # insert the crossing and attach endpoints
        #k.add_crossings_from([crossing_over, crossing_under])

        k.set_arc((previous_open_endpoint_over, (crossing_over, 1)))
        k.set_arc((previous_open_endpoint_under, (crossing_under, 0)))

        k.set_arc((ep_g, (crossing_over, 2)))
        k.set_arc((ep_f, (crossing_under, 3)))
        k.set_arc(((crossing_over, 0), (crossing_under, 1)))

        previous_open_endpoint_over = (crossing_over, 3)
        previous_open_endpoint_under = (crossing_under, 2)
    #attach the final endpoints from the last node

    k.set_arc((previous_open_endpoint_over, (B, 2)))
    k.set_arc((previous_open_endpoint_under, (B, 1)))

    if k.degree(A) != 3 or k.degree(B) != 3:
        raise ValueError("The leafs should have degree 3 after double-closure")

    return k

def closure(k: PlanarDiagram, over=False, under=False):
    """

    :param k:
    :param over:
    :param under:
    :return:
    """

    _DEBUG = False

    if not under and not over:
        raise ValueError("Cannot have both underpass and overpass closure to False")

    leafs = list(v for v in k.vertices if k.degree(v) == 1)
    if len(leafs) != 2:
        raise ValueError("Can only close a diagram with two leafs")

    # get the two connected nodes
    A, B = leafs
    # dual planar graph
    dual = dual_planar_diagram(k)

    if _DEBUG: print("DUAL", dual)

    # get faces of the two leafs
    A_ep = k.endpoint_from_pair((A, 0))
    B_ep = k.endpoint_from_pair((B, 0))
    A_face = next(f for f in dual.vertices if A_ep in f)
    B_face = next(f for f in dual.vertices if B_ep in f)

    # the shortest path from the two endpoint faces will yield the arcs we must add to the structure
    path = bfs_shortest_path(dual, A_face, B_face)
    if _DEBUG: print("path:", " -> ".join(str(f) for f in path))

    if _DEBUG: print("start endpoint", A_ep, "end endpoint", B_ep)

    previous_endpoint = (A_ep.node, A_ep.position + 1)

    # loop through all neighbouring faces and get the common arc that we must pass
    # previous_open_endpoint = (A, 1)
    # for f, g in zip(path, path[1:]):
    #     arc = _face_intersection_arc(k, f, g)  # find the arcs we must pass
    #     ep_f, ep_g = arc
    #
    #     crossing = unique_new_node_name(k)
    #     # insert the crossing and attach endpoints
    #     k.add_crossing(crossing_for_adding=crossing)
    #     # TODO: orientation
    #     # TODO: attributes
    #     if underpass_closure:
    #         k.set_arc((previous_open_endpoint, (crossing, 0)))
    #         k.set_arc((ep_f, (crossing, 3)))
    #         k.set_arc((ep_g, (crossing, 1)))
    #         previous_open_endpoint = (crossing, 2)
    #     else:
    #         k.set_arc((previous_open_endpoint, (crossing, 1)))
    #         k.set_arc((ep_f, (crossing, 0)))
    #         k.set_arc((ep_g, (crossing, 2)))
    #         previous_open_endpoint = (crossing, 3)


    # attach the final endpoints from the last node
    #     k.set_arc((previous_open_endpoint, (B, 1)))

    arcs = [_face_intersection_arc(k, f, g) for f, g in zip(path, path[1:])]
    if over and under:
        closed_k = _over_and_under_closure(k, A, B, arcs)
    elif over:
        closed_k = _overpass_closure(k, A, B, arcs)
    else:
        closed_k = _underpass_closure(k, A, B, arcs)

    return closed_k

if __name__ == "__main__":

   import knotpy as kp

   k = kp.from_knotpy_notation("a=V(b0) b=X(a0 c0 c3 d3) c=X(b1 d2 e0 b2) d=X(f0 e1 c1 b3) e=X(c2 d1 g3 f1) f=X(d0 e3 g2 h0) g=X(h3 h1 f2 e2) h=X(f3 g1 i0 g0) i=V(h2)")
   print(k)
   c = closure(k)
   print(c)
   print(kp.sanity_check(c))



