import warnings

#from knotpy.algorithms.sanity import sanity_check
from knotpy.manipulation.insert import insert_endpoint, parallelize_arc
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.topology import bridges, leafs, kinks, loops
from knotpy.algorithms.cut_set import cut_nodes
from knotpy.manipulation.insert import insert_arc
from knotpy.manipulation.subdivide import subdivide_endpoint
from knotpy.notation.native import to_knotpy_notation

_DEBUG_SUPPORT = False

def non_leaf_bridges(k:PlanarDiagram):
    """Returns a list of bridges that are not leafs."""
    return [b for b in bridges(k) if all(k.degree(ep.node) > 1 for ep in b)]

def _visible(__obj):
    """Should object (node, endpoint, ...) be shown in diagram?
    :param __obj:
    :return:
    """
    if not hasattr(__obj, "attr"):
        return True
    if "_support" in __obj.attr and __obj.attr["_support"]:
        return False
    return True

def _subdivide_two_adjacent_arcs(k:PlanarDiagram, endpoint):
    """
        Subdivide the two adjacent arcs in a planar diagram at a given endpoint.

        If the specified endpoint is oriented upwards, this function subdivides the
        adjacent left and right endpoints (CCW and CW respectively),
        creating new nodes and marking them with a "_support" attribute.

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

    node_left = subdivide_endpoint(k, left_endpoint)
    node_right = subdivide_endpoint(k, right_endpoint)
    k.nodes[node_left].attr["_support"] = True
    k.nodes[node_right].attr["_support"] = True

    return node_left, node_right, k.endpoint_from_pair((node_left, 0)), k.endpoint_from_pair((node_right, 0))


def _add_support_arcs_for_cut_vertices(k:PlanarDiagram):

    # TODO: do not include kinks as cut-vertices

    def _cut_nodes_not_leaf_adjacent_or_kink():
        # return cut nodes that are not adjacent to a leaf
        cn = cut_nodes(k)
        leaf_adj = [k.twin((l, 0)).node for l in leafs(k)]
        kink_crossings = [ep.node for ep in kinks(k)]
        return set(cn) - set(leaf_adj) - set(kink_crossings)

    while nodes := _cut_nodes_not_leaf_adjacent_or_kink():

        node = nodes.pop()
        degree = k.degree(node)
        bivertices = [subdivide_endpoint(k, (node, pos)) for pos in range(degree)]

        for v in bivertices:

            if _DEBUG_SUPPORT:
                print("Adding support for cut vertices {}".format(v))

            k.nodes[v].attr["_support"] = True

        for i in range(degree):
            adj_vert_a, adj_vert_b = bivertices[i], bivertices[(i + 1) % degree]
            adj_pos_a = k.degree(adj_vert_a)
            adj_pos_b = 1

            insert_endpoint(k, target_endpoint=(adj_vert_a, adj_pos_a), adjacent_endpoint=(adj_vert_b, adj_pos_b), _support=True)
            insert_endpoint(k, target_endpoint=(adj_vert_b, adj_pos_b), adjacent_endpoint=(adj_vert_a, adj_pos_a), _support=True)

        #assert sanity_check(k)

# def _add_support_for_bivalent_vertices(k:PlanarDiagram):
#
#     while bivertices := [v for v in k.vertices if k.degree(v) == 2]:
#         v = bivertices[0]
#         assert sanity_check(k)
#         #parallelize_arc(k, ((v ,0), k.twin((v, 0))), _support=True)
#         parallelize_arc(k, ((v ,0), k.twin((v, 0))), color="green")
#         assert sanity_check(k)

def _long_bridges(k:PlanarDiagram):
    """If multiple bridges are connected via a 2-valent node, we call this a long bridge and treat it as one."""

    #_bridges = bridges(k)
    _bridges = non_leaf_bridges(k)

    if not _bridges:
        return []


    while bivertices := [v for ep1, ep2 in _bridges for v in [ep1.node, ep2.node] if k.degree(v) == 2]:
        # join bi-vertices
        v = bivertices[0]
        endpoints = []

        for b in _bridges:
            ep1, ep2 = b
            if ep1.node == v or ep2.node == v:
                endpoints.append([ep1, ep2, b] if ep2.node == v else [ep2, ep1, b])

        if len(endpoints) != 2:
            raise ValueError(f"bivalent bridges error, endpoints: {endpoints}")

        _bridges.remove(endpoints[0][2])
        _bridges.remove(endpoints[1][2])
        _bridges.add(frozenset( [endpoints[0][0], endpoints[1][0] ] ))

    return _bridges



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
    while all_bridges := _long_bridges(k):#bridges(k):
        bridge = all_bridges.pop()

        if _DEBUG_SUPPORT:
            print("Adding support for (long) bridges {}".format(bridge))


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

            if _DEBUG_SUPPORT:
                print("degs: 1 & 1")

            # just a segment
            k.set_endpoint((node_a, 1), (node_b, 2), _support=True)
            k.set_endpoint((node_a, 2), (node_b, 1), _support=True)
            k.set_endpoint((node_b, 1), (node_a, 2), _support=True)
            k.set_endpoint((node_b, 2), (node_a, 1), _support=True)
            continue

        # Looking from node a, one parallel arc if considered "right" and the other one "left.

        if k.degree(node_a) == 1:

            if _DEBUG_SUPPORT:
                print("degs: a=1")

            # we have a leaf/knotoid terminal at node a, do not create a parallel arc to the bridge, but two adjacent arcs
            node_a_right = node_a_left = node_a
            pos_a_right, pos_a_left = 1, 2
        else:


            if _DEBUG_SUPPORT:
                print("degs: a!1")


            # add two parallel endpoints (right and left)
            node_a_right = subdivide_endpoint(k, (node_a, (pos_a + 1) % deg_a))  # HERE ADD SUPPORT
            node_a_left = subdivide_endpoint(k, (node_a, (pos_a - 1) % deg_a))
            pos_a_right = 1 if k.nodes[node_a_right][0].node == node_a else 2
            pos_a_left = 2 if k.nodes[node_a_right][0].node == node_a else 1

            k.nodes[node_a_right].attr["_support"] = True
            k.nodes[node_a_left].attr["_support"] = True

        if k.degree(node_b) == 1:

            if _DEBUG_SUPPORT:
                print("degs: b=1")


            # we have a leaf/knotoid terminal at node a
            node_b_right = node_b_left = node_b
            pos_b_right, pos_b_left = 2, 1
        else:

            if _DEBUG_SUPPORT:
                print("degs: b!1")


            node_b_right = subdivide_endpoint(k, (node_b, (pos_b - 1) % deg_b))  # HERE ADD SUPPORT
            node_b_left = subdivide_endpoint(k, (node_b, (pos_b + 1) % deg_b))
            pos_b_right = 2 if k.nodes[node_b_right][0].node == node_b else 1
            pos_b_left = 1 if k.nodes[node_b_right][0].node == node_b else 2

            k.nodes[node_b_right].attr["_support"] = True
            k.nodes[node_b_left].attr["_support"] = True

        if k.degree(node_a) == 1:
            if _DEBUG_SUPPORT:
                print("degs: a1")

            # if pos_a_right <  pos_a_left, first insert the smaller one, otherwise indices will not make sense
            insert_arc(k, ((node_a_right, pos_a_right), (node_b_right, pos_b_right)), _support=True)
            insert_arc(k, ((node_a_left, pos_a_left), (node_b_left, pos_b_left)), _support=True)
        else:

            if _DEBUG_SUPPORT:
                print("degs: a1!")

            insert_arc(k, ((node_a_left, pos_a_left), (node_b_left, pos_b_left)), _support=True)
            insert_arc(k, ((node_a_right, pos_a_right), (node_b_right, pos_b_right)), _support=True)


def _add_support_arcs(k: PlanarDiagram):
    """Add support arcs so there are no bridges/loops/,,, in the diagram. For every bridge, add two parallel arcs. In the case
    the bridge is a leaf, add two adjacent arcs to the leaf.

    :param k:
    :return:
    """

    k = k.copy()
    if k.name:
        name = k.name
        del k.attr["name"]
    else:
        name = None
    #
    # if not sanity_check(k):
    #     raise ValueError(f"The diagram is not planar: {to_knotpy_notation(k)} (before support)")

    _add_support_arcs_for_bridges(k)

    #if bridges(k):
    if non_leaf_bridges(k):
        raise ValueError(f"Diagram has bridges after adding bridge-support arcs.")

    # if not sanity_check(k):
    #     raise ValueError(f"The diagram is not planar: {to_knotpy_notation(k)} (after bridges)")

    _add_support_arcs_for_cut_vertices(k)

    # if not sanity_check(k):
    #     raise ValueError(f"The diagram is not planar: {to_knotpy_notation(k)} (after cut vertices)")

    if name:
        k.name = name

    return k


def drawable(k:PlanarDiagram):

    diagram_drawable = True
    error_text = []

    #if bridges(k):
    if non_leaf_bridges(k):
        warnings.warn(f"Diagram {to_knotpy_notation(k)} contains bridges (skipping)", UserWarning)
        error_text.append("bridge")
        diagram_drawable = False

    if loops(k):
        warnings.warn(f"Diagram {to_knotpy_notation(k)} contains loops (skipping)", UserWarning)
        error_text.append("loop")
        diagram_drawable = False

    # if kinks(k):
    #     warnings.warn(f"Diagram {to_knotpy_notation(k)} contains kinks (skipping)", UserWarning)
    #     error_text.append("kink")
    #     diagram_drawable = False

    # if leafs(k):
    #     warnings.warn(f"Diagram {to_knotpy_notation(k)} contains leafs (skipping)", UserWarning)
    #     error_text.append("leaf")
    #     diagram_drawable = False

    if cut_nodes(k):
        warnings.warn(f"Diagram {to_knotpy_notation(k)} contains cut-nodes (skipping)", UserWarning)
        error_text.append("cut-node")
        diagram_drawable = False

    return diagram_drawable, error_text

# def drawable(k):
#     if bridges(k):
#         print("bridges:", bridges(k))
#         return False
#
#     return True


if __name__ == "__main__":
    pass
