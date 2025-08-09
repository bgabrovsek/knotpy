# knotpy/algorithms/rewire.py

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.subdivide import subdivide_endpoint
from knotpy.algorithms.insert import insert_new_leaf
from knotpy.algorithms.remove import remove_bivalent_vertex
from knotpy.classes.endpoint import Endpoint
from knotpy.classes.node import Crossing


def pull_and_plug_endpoint(
    k: PlanarDiagram | OrientedPlanarDiagram,
    source_endpoint: Endpoint | tuple,
    destination_endpoint: Endpoint | tuple,
) -> None:
    """Pull out one endpoint and plug it somewhere else.

    This splits the source arc, creates a leaf at the destination, connects them,
    and removes temporary bivalent vertices. Operates in place.

    Args:
        k: Diagram to modify.
        source_endpoint: Endpoint or (node, position) to pull out.
        destination_endpoint: Endpoint or (node, position) where it is plugged.
    """
    adjacent_endpoint = k.twin(source_endpoint)
    src_node, src_pos = source_endpoint
    dst_node, dst_pos = destination_endpoint

    # get attributes
    src_attr = k.endpoint_from_pair(source_endpoint).attr
    adj_attr = adjacent_endpoint.attr

    bi_node = subdivide_endpoint(k, source_endpoint)  # split the initial arc
    leaf_node = insert_new_leaf(k, destination_endpoint)  # insert new leaf node at destination

    # set leaf attributes
    k.endpoint_from_pair((leaf_node, 0)).attr.update(adj_attr)
    k.endpoint_from_pair((dst_node, dst_pos)).attr.update(src_attr)

    endpoint_to_remove = k.twin((bi_node, 0))

    # connect the new stubs
    k.set_endpoint(endpoint_for_setting=(bi_node, 0), adjacent_endpoint=(leaf_node, 1), **adj_attr)
    k.set_endpoint(endpoint_for_setting=(leaf_node, 1), adjacent_endpoint=(bi_node, 0), **src_attr)

    # remove old source side and clean up
    k.remove_endpoint(endpoint_to_remove)
    remove_bivalent_vertex(k, bi_node)
    remove_bivalent_vertex(k, leaf_node)


def replug_endpoint(
    k: PlanarDiagram | OrientedPlanarDiagram,
    source_endpoint: Endpoint | tuple,
    destination_endpoint: Endpoint | tuple,
) -> None:
    """Unplug an endpoint and overwrite the destination slot.

    Does not insert at the destination (overwrites). Operates in place.

    Args:
        k: Diagram to modify.
        source_endpoint: Endpoint or (node, position) to unplug.
        destination_endpoint: Endpoint or (node, position) to overwrite.

    Raises:
        ValueError: If unplugging from a crossing (would create 3-valent crossing).
    """
    src_node, src_pos = source_endpoint
    dst_node, dst_pos = destination_endpoint

    src_ep = k.endpoints[(src_node, src_pos)]
    adj_ep = k.nodes[src_node][src_pos]

    if isinstance(k.nodes[src_node], Crossing):
        raise ValueError("Cannot unplug endpoint from crossing (this would yield a 3-valent crossing).")

    k.set_endpoint(
        endpoint_for_setting=(dst_node, dst_pos),
        adjacent_endpoint=adj_ep,
        create_using=type(src_ep),
        **src_ep.attr,
    )
    k.set_endpoint(
        endpoint_for_setting=adj_ep,
        adjacent_endpoint=(dst_node, dst_pos),
        create_using=type(adj_ep),
        **adj_ep.attr,
    )

    k.remove_endpoint(src_ep)


def swap_endpoints(
    k: PlanarDiagram | OrientedPlanarDiagram,
    ep1: Endpoint | tuple,
    ep2: Endpoint | tuple,
) -> None:
    """Swap two endpoints in place (no insertion/removal).

    Args:
        k: Diagram to modify.
        ep1: Endpoint or (node, position).
        ep2: Endpoint or (node, position).
    """
    if not isinstance(ep1, Endpoint):
        ep1 = k.endpoint_from_pair(ep1)
    if not isinstance(ep2, Endpoint):
        ep2 = k.endpoint_from_pair(ep2)

    twin1 = k.twin(ep1)
    twin2 = k.twin(ep2)

    k.set_endpoint(endpoint_for_setting=ep1, adjacent_endpoint=twin2)
    k.set_endpoint(endpoint_for_setting=twin2, adjacent_endpoint=ep1)

    k.set_endpoint(endpoint_for_setting=ep2, adjacent_endpoint=twin1)
    k.set_endpoint(endpoint_for_setting=twin1, adjacent_endpoint=ep2)


def permute_node(
    k: PlanarDiagram | OrientedPlanarDiagram,
    node,
    permutation: dict | list | tuple,
) -> None:
    """Permute the endpoint indices of a node.

    Example:
        permutation = {0: 0, 1: 2, 2: 3, 3: 1} maps [a, b, c, d] -> [a, d, b, c].

    Args:
        k: Diagram to modify.
        node: Node label.
        permutation: Mapping or sequence giving new index for each old index.
    """
    adj_endpoints = [adj_ep for adj_ep in k.nodes[node]]  # snapshot
    node_endpoint_inst = [k.twin(adj_ep) for adj_ep in adj_endpoints]

    for pos, adj_ep in enumerate(adj_endpoints):
        if adj_ep.node != node:  # no loop
            # set adjacent
            k.set_endpoint(
                endpoint_for_setting=(node, permutation[pos]),
                adjacent_endpoint=(adj_ep.node, adj_ep.position),
                create_using=type(adj_ep),
                **adj_ep.attr,
            )
            # set self
            k.set_endpoint(
                endpoint_for_setting=adj_ep,
                adjacent_endpoint=(node, permutation[pos]),
                create_using=type(node_endpoint_inst[pos]),
                **node_endpoint_inst[pos].attr,
            )
        else:
            # loop case
            k.set_endpoint(
                endpoint_for_setting=(node, permutation[pos]),
                adjacent_endpoint=(adj_ep.node, permutation[adj_ep.position]),
                create_using=type(adj_ep),
                **adj_ep.attr,
            )


if __name__ == "__main__":
    pass