from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.topology import bridges
from knotpy.manipulation.insert import insert_arc
from knotpy.manipulation.subdivide import subdivide_endpoint

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


def _add_support_arcs(k: PlanarDiagram):
    """ Ads support arcs so there are no bridges in the diagram. For every bridge, add two parallel arcs. In the case
    the bridge is a leaf, add two adjacent arcs to the leaf.

    :param k:
    :return:
    """

    k = k.copy()
    is_oriented = k.is_oriented()

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

    return k