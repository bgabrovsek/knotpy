from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.manipulation.subdivide import subdivide_endpoint
from knotpy.manipulation.insert import insert_new_leaf
from knotpy.manipulation.remove import remove_bivalent_vertex



def rewire_endpoint(k: PlanarDiagram, source_endpoint, destination_endpoint):
    """Pull out one endpoint and stick it somewhere else."""
    # TODO: we should distinguish between rewire (overwrites) and pull_and_plug (remove and inserts)

    adjacent_endpoint = k.twin(source_endpoint)
    src_node, src_pos = source_endpoint
    dst_node, dst_pos = destination_endpoint


    # get attributes
    src_attr = k.endpoint_from_pair(source_endpoint).attr
    adj_attr = adjacent_endpoint.attr


    bi_node = subdivide_endpoint(k, source_endpoint)  # split the initial arc
    leaf_node = insert_new_leaf(k, destination_endpoint)  # insert new leaf node at destination, TODO: orientation

    # set leaf attributes
    k.endpoint_from_pair((leaf_node, 0)).attr.update(adj_attr)
    k.endpoint_from_pair((dst_node, dst_pos)).attr.update(src_attr)

    endpoint_to_remove = k.twin((bi_node, 0))

    #k.set_arc(((bi_node, 0), (leaf_node, 1)))
    k.set_endpoint(endpoint_for_setting=(bi_node, 0), adjacent_endpoint=(leaf_node, 1), **adj_attr)
    k.set_endpoint(endpoint_for_setting=(leaf_node, 1), adjacent_endpoint=(bi_node, 0), **src_attr)

    # TODO: attributes from here on not tested
    k.remove_endpoint(endpoint_to_remove)
    remove_bivalent_vertex(k, bi_node)
    remove_bivalent_vertex(k, leaf_node)



# def rewire_endpoint(k: PlanarDiagram, source_endpoint, destination_endpoint):
#     """Pull out one endpoint and stick it somewhere else."""
#
#     # TODO: simplify that k.node[ep] points to k.node[ep.node][ep.position]
#     # TODO: we can maybe simplify everything by adding a temporary vertex at the destination
#
#     if not isinstance(source_endpoint, Endpoint):
#         source_endpoint = k.endpoint_from_pair(source_endpoint)
#
#     src_node, src_pos = source_endpoint
#     dst_node, dst_pos = destination_endpoint
#
#     src_node_inst = k._nodes[src_node]
#     dst_node_inst = k._nodes[dst_node]
#
#     if not isinstance(k.nodes[src_node], Vertex) or not isinstance(k.nodes[src_node], Vertex):
#         raise TypeError("Can rewire arcs only from a vertex to a vertex.")
#
#     adjacent_endpoint = k.twin(source_endpoint)
#     adj_node, adj_pos = adjacent_endpoint
#
#     # rewire
#     # print("rewire")
#     # print(k)
#     # print("+1")
#     # shift twin position of destination endpoint (+1), since we are inserting a new endpoint
#     for pos, adj_dest_ep in enumerate(dst_node_inst[dst_pos:], start=dst_pos):
#         ep = k.endpoint_from_pair((dst_node, pos))
#         k._nodes[adj_dest_ep.node][adj_dest_ep.position] = type(ep)(node=dst_node, position=pos + 1, **ep.attr)
#         # print(k)
#
#     # print("-1")
#     # shift twin positions of source endpoint (-1), since we are removing an old endpoint
#     for pos, adj_source_ep in enumerate(src_node_inst[src_pos + 1:], start=src_pos + 1):
#         ep = k.endpoint_from_pair((src_node, pos))
#         # we cannot use position = pos - 1, since the position can change in the previous loop
#         k._nodes[adj_source_ep.node][adj_source_ep.position] = type(ep)(node=src_node, position=ep.position - 1, **ep.attr)
#         # print(k)
#     # If the source endpoint on a loop, then also reduce the position by 1.
#     if adj_node == src_node and adj_pos > src_pos:
#         if not (src_node == dst_node and adj_pos > dst_pos):
#             adjacent_endpoint = type(adjacent_endpoint)(node=adj_node, position=adj_pos - 1, **adjacent_endpoint.attr)
#
#     # insert new endpoint
#     k._nodes[dst_node]._inc.insert(dst_pos, adjacent_endpoint)
#
#     # print("insert")
#     # print(k)
#
#     # If the destination endpoint is on the same node as the source endpoint, reduce position by 1.
#     # The following piece of code is after inserting the endpoint, since we did not yet remove the old endpoint.
#     if src_node == dst_node and dst_pos > src_pos:
#         dst_pos -= 1
#
#     # if destination is the same as adjacent, we should adjust the adjacent position, since we are inserting a new endpoint
#     if adj_node == dst_node and dst_pos <= adj_pos:
#         adj_pos += 1
#
#     # correct the adjacent endpoint of the new one
#     k._nodes[adj_node][adj_pos] = type(source_endpoint)(node=dst_node, position=dst_pos, **source_endpoint.attr)
#
#     # delete old source endpoint
#     del k._nodes[src_node][src_pos]







if __name__ == "__main__":
    # test rewire (normal)
    from knotpy import sanity_check, PlanarDiagram, Crossing

    k = PlanarDiagram()
    k.set_arcs_from("x0a0,x1y2,x2d0,y0e0,y1f0,y3g0,y4h0,f1d1")
    print(k)
    sanity_check(k)
    print(k)
    rewire_endpoint(k, source_endpoint=("x",1), destination_endpoint=("y",2))
    print(k)
    sanity_check(k)

    exit()


def replug_endpoint(k: PlanarDiagram, source_endpoint, destination_endpoint):
    """Unplugs the endpoint endpoint_source and plugs it into endpoint_destination. Takes care of removing the source
    endpoint (shifting bigger indices). Does not insert the destination endpoint, but overwrites it.

    :param k: planar diagram
    :param source_endpoint:
    :param destination_endpoint:
    :return:
    """
    src_node, src_pos = source_endpoint
    dst_node, dst_pos = destination_endpoint

    src_ep = k.endpoints[(src_node, src_pos)]
    adj_ep = k.nodes[src_node][src_pos]

    if isinstance(k.nodes[src_node], Crossing):
        raise ValueError("Cannot unplug endpoint from crossing (this would yield a 3-valent crossing).")

    k.set_endpoint(endpoint_for_setting=(dst_node, dst_pos),
                   adjacent_endpoint=adj_ep,
                   create_using=type(src_ep),
                   **src_ep.attr)
    k.set_endpoint(endpoint_for_setting=adj_ep,
                   adjacent_endpoint=(dst_node, dst_pos),
                   create_using=type(adj_ep),
                   **adj_ep.attr)

    k.remove_endpoint(src_ep)
