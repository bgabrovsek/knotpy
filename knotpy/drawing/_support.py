from knotpy import from_knotpy_notation
from knotpy.algorithms.sanity import sanity_check
from knotpy.manipulation.insert import insert_endpoint
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.topology import bridges, leafs
from knotpy.algorithms.cut_set import cut_nodes
from knotpy.manipulation.insert import insert_arc
from knotpy.manipulation.subdivide import subdivide_endpoint
from knotpy.notation.native import to_knotpy_notation


def _subdivide_two_adjacent_arcs(k:PlanarDiagram, endpoint):
    """
        Subdivide the two adjacent arcs in a planar diagram at a given endpoint.

        If the specified endpoint is oriented upwards, this function subdivides the
        adjacent left and right endpoints (CCW and CW respectively),
        creating new nodes and marking them with a "__support__" attribute.

        Args:
            k (PlanarDiagram): The planar diagram in which the subdivision occurs.
            endpoint (tuple): A tuple representing the target endpoint.

        Returns:
            tuple: A tuple containing the newly created left and right nodes, and the
            corresponding new endpoints (endpoints of the left and right nodes, respectively).

    """

    node, pos = endpoint
    degree = k.degree(node)
    left_endpoint = k.endpoint_from_pair((node, (pos - 1) % degree))
    right_endpoint = k.endpoint_from_pair((node, (pos + 1) % degree))

    # # Check whether the arc from left_endpoint loops directly to right_endpoint
    # if k.twin(left_endpoint) == right_endpoint:
    #     # We have a loop.
    #     node_left = subdivide_endpoint(k, left_endpoint)
    #     node_right = subdivide_endpoint(k, right_endpoint)
    # else:
    #     # We do not have a loop.
    #     node_left = subdivide_endpoint(k, left_endpoint)
    #     node_right = subdivide_endpoint(k, right_endpoint)
    #
    node_left = subdivide_endpoint(k, left_endpoint)
    node_right = subdivide_endpoint(k, right_endpoint)
    k.nodes[node_left].attr["__support__"] = True
    k.nodes[node_right].attr["__support__"] = True

    return node_left, node_right, k.endpoint_from_pair((node_left, 0)), k.endpoint_from_pair((node_right, 0))


def _add_support_arcs_for_cut_vertices(k:PlanarDiagram):

    def _cut_nodes_not_leaf_adjacent():
        # return cut nodes that are not adjacent to a leaf
        cn = cut_nodes(k)
        leaf_adj = [k.twin((l, 0)).node for l in leafs(k)]
        return set(cn) - set(leaf_adj)

    while nodes := _cut_nodes_not_leaf_adjacent():

        # print("CUT VERT", k, "NODE", nodes)

        node = nodes.pop()
        # print("NODE", node)
        degree = k.degree(node)
        #bivertices = [subdivide_endpoint(k, ep) for ep in k.nodes[node]]
        #print("BS", to_knotpy_notation(k))
        bivertices = [subdivide_endpoint(k, (node, pos)) for pos in range(degree)]

        #print("adding support around", node, "with", degree, "bivertices", bivertices)
        #print("AV", to_knotpy_notation(k))

        for v in bivertices:
            k.nodes[v].attr["__support__"] = True

        for i in range(degree):
            adj_vert_a, adj_vert_b = bivertices[i], bivertices[(i + 1) % degree]
            adj_pos_a = k.degree(adj_vert_a)
            adj_pos_b = 1

            # k.set_endpoint((adj_vert_a, adj_pos_a), (adj_vert_b, adj_pos_b), __support__=True)
            # k.set_endpoint((adj_vert_b, adj_pos_b), (adj_vert_a, adj_pos_a), __support__=True)
            insert_endpoint(k, target_endpoint=(adj_vert_a, adj_pos_a), adjacent_endpoint=(adj_vert_b, adj_pos_b), __support__=True)
            insert_endpoint(k, target_endpoint=(adj_vert_b, adj_pos_b), adjacent_endpoint=(adj_vert_a, adj_pos_a), __support__=True)
            # insert_arc(k, ((adj_vert_a, adj_pos_a), (adj_vert_b, adj_pos_b)), __support__=True)
        # print("END", k)
        assert sanity_check(k)
        #print("AS", to_knotpy_notation(k))

    # print("FINISH")

def _add_support_arcs_for_bridges(k:PlanarDiagram):
    """
    Adds support arcs for bridges in the given diagram.


    Raises:
        NotImplementedError: If an unsupported configuration involving degree-2
            vertices is encountered.

    Args:
        k (PlanarDiagram): The planar diagram object for which support arcs need to be added.

    Returns:
        PlanarDiagram: The processed planar diagram without bridges.
    """

    # Support for bridges
    while all_bridges := bridges(k):
        bridge = all_bridges.pop()
        # the bridge from node a to node b
        endpoint_a, endpoint_b = bridge
        node_a, pos_a = endpoint_a
        node_b, pos_b = endpoint_b
        deg_a = k.degree(node_a)
        deg_b = k.degree(node_b)
        if deg_a == 2 or deg_b == 2:
            raise NotImplementedError("Support arcs for degree-2 vertices not supported")

        # Are we plotting just a segment (path graph on two vertices)?
        if deg_a == 1 and deg_b == 1:
            # just a segment
            k.set_endpoint((node_a, 1), (node_b, 2), __support__=True)
            k.set_endpoint((node_a, 2), (node_b, 1), __support__=True)
            k.set_endpoint((node_b, 1), (node_a, 2), __support__=True)
            k.set_endpoint((node_b, 2), (node_a, 1), __support__=True)
            continue

        # Looking from node a, one parallel arc if considered "right" and the other one "left.

        if k.degree(node_a) == 1:
            # we have a leaf/knotoid terminal at node a, do not create a parallel arc to the bridge, but two adjacent arcs
            node_a_right = node_a_left = node_a
            pos_a_right, pos_a_left = 1, 2
        else:
            # add two parallel endpoints (right and left)
            node_a_right = subdivide_endpoint(k, (node_a, (pos_a + 1) % deg_a))
            node_a_left = subdivide_endpoint(k, (node_a, (pos_a - 1) % deg_a))
            pos_a_right = 1 if k.nodes[node_a_right][0].node == node_a else 2
            pos_a_left = 2 if k.nodes[node_a_right][0].node == node_a else 1

            k.nodes[node_a_right].attr["__support__"] = True
            k.nodes[node_a_left].attr["__support__"] = True

        if k.degree(node_b) == 1:
            # we have a leaf/knotoid terminal at node a
            node_b_right = node_b_left = node_b
            pos_b_right, pos_b_left = 2, 1
        else:
            node_b_right = subdivide_endpoint(k, (node_b, (pos_b - 1) % deg_b))
            node_b_left = subdivide_endpoint(k, (node_b, (pos_b + 1) % deg_b))
            pos_b_right = 2 if k.nodes[node_b_right][0].node == node_b else 1
            pos_b_left = 1 if k.nodes[node_b_right][0].node == node_b else 2

            k.nodes[node_b_right].attr["__support__"] = True
            k.nodes[node_b_left].attr["__support__"] = True

        if k.degree(node_a) == 1:
            # if pos_a_right <  pos_a_left, first insert the smaller one, otherwise indices will not make sense
            insert_arc(k, ((node_a_right, pos_a_right), (node_b_right, pos_b_right)), __support__=True)
            insert_arc(k, ((node_a_left, pos_a_left), (node_b_left, pos_b_left)), __support__=True)
        else:
            insert_arc(k, ((node_a_left, pos_a_left), (node_b_left, pos_b_left)), __support__=True)
            insert_arc(k, ((node_a_right, pos_a_right), (node_b_right, pos_b_right)), __support__=True)

def _add_support_arcs(k: PlanarDiagram):
    """ Ads support arcs so there are no bridges in the diagram. For every bridge, add two parallel arcs. In the case
    the bridge is a leaf, add two adjacent arcs to the leaf.

    :param k:
    :return:
    """

    #print("\n SUPPORT \n")


    k = k.copy()
    if k.name:
        name = k.name
        del k.attr["name"]
    else:
        name = None
    is_oriented = k.is_oriented()

    if not sanity_check(k):
        raise ValueError(f"The diagram is not planar: {to_knotpy_notation(k)} (before support)")

    #print("BB", to_knotpy_notation(k))

    _add_support_arcs_for_bridges (k)

    #print("AB", to_knotpy_notation(k))

    if bridges(k):
        raise ValueError(f"HAS BRIDGES!!!")

    if not sanity_check(k):
        raise ValueError(f"The diagram is not planar: {to_knotpy_notation(k)} (after bridges)")

    #print("BC", to_knotpy_notation(k))

    _add_support_arcs_for_cut_vertices(k)

    #print("AC", to_knotpy_notation(k))

    if not sanity_check(k):
        raise ValueError(f"The diagram is not planar: {to_knotpy_notation(k)} (after cut vertices)")

    if name:
        k.name = name
    return k


if __name__ == "__main__":
    pass
    # k = from_knotpy_notation("BS a=V(b0 i2 j1) b=X(a0 j0 k1 i0) c=X(l0 d0 k0 e0) d=X(c1 f0 g3 i1) e=V(c3 k2 l1) f=X(d1 g2 h3 h2) g=X(h1 h0 f1 d2) h=X(g1 g0 f3 f2) i=V(b3 d3 a1) j=V(b1 a2 l2) k=V(c2 b2 e1) l=V(c0 e2 j2) [; i:{'__support__'=True} j:{'__support__'=True} k:{'__support__'=True} l:{'__support__'=True}; a1:{'__support__'=True} a2:{'__support__'=True} e1:{'__support__'=True} e2:{'__support__'=True} i2:{'__support__'=True} j1:{'__support__'=True} k2:{'__support__'=True} l1:{'__support__'=True}]")
    # print(k)
    # print(sanity_check(k))
    # _add_support_arcs_for_cut_vertices(k)
    # print(sanity_check(k))
