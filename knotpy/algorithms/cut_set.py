"""
This module provides tools for identifying and analyzing (arc) cut sets in planar diagrams.

Ana arc cut set in a graph or diagram is a set of edges (arcs) that, when removed,
disconnects the graph into two or more disjoint components.
These functions are designed to work with planar diagram representations,
allowing the detection of such critical subsets of arcs and vertices.



We need arc cut sets for these operations:
- detecting connected sus
- detecting 3-sums
- tangle decomposition & flyping
"""

__all__ = ["arc_cut_sets", "cut_nodes", "find_arc_cut_set"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

from collections import Counter
from itertools import combinations
import warnings

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.classes.node import Vertex, Crossing
from knotpy.algorithms.naming import multiple_unique_new_node_names
from knotpy.utils.disjoint_union_set import DisjointSetUnion
from knotpy.algorithms.disjoint_union import disjoint_union_decomposition



def _is_arc_cut_set(k: PlanarDiagram, arcs, minimum_partition_nodes=1, return_partition=False) -> bool | tuple[bool, list]:
    """
    Determines whether removing a given set of arcs disconnects the planar diagram.

    Args:
        k (PlanarDiagram): The planar diagram being analyzed.
        arcs: A collection of arcs that are being tested as a potential arc-cut-set.
        minimum_partition_nodes (int): The minimum number of nodes required in each
            partition for the cut-set to be valid.
        return_partition (bool, optional): Whether to return the partitions resulting
            after removing the arcs if the arcs form a valid arc-cut-set. Defaults to False.

    Returns:
        bool | tuple[bool, Any]: If `return_partition` is False, returns a boolean indicating
        whether the given arcs form a valid arc-cut-set. If `return_partition` is True, returns
        a tuple where the first element is the boolean result, and the second element represents
        the partition (list of sets of nodes) resulting after removing the arcs.
    """

    # Get partition before cutting out arcs.
    dsu = DisjointSetUnion(k.nodes)  # before cutting out arcs
    dsu_ = DisjointSetUnion(k.nodes)  # after cutting out arcs
    for arc in k.arcs:
        ep1, ep2 = arc
        dsu[ep1.node] = ep2.node
        if arc not in arcs:
            dsu_[ep1.node] = ep2.node

    partition = dsu.classes()
    partition_ = dsu_.classes()

    # Get partition after cutting out arcs.
    cut_set_ok = sum(len(p) >= minimum_partition_nodes for p in partition_) == sum(len(p) >= minimum_partition_nodes for p in partition) + 1

    return cut_set_ok if not return_partition else (cut_set_ok, partition_)


def _arc_cut_set_iterator(k: PlanarDiagram | OrientedPlanarDiagram, order: int, minimum_partition_nodes=1, return_partition=False, return_ccw_ordered_endpoints=False):
    """
    Computes the arc cut sets for a given planar diagram or oriented planar
    diagram. An arc cut sets is a set of arcs that, when removed, disconnects the diagram.

    Args:
        k: A PlanarDiagram or OrientedPlanarDiagram instance of the diagram for which the arc cut sets are to be computed.
        order: An integer representing the order of the cut. The order defines the number of arcs of the arc cut sets.
        minimum_partition_nodes: An integer specifying the minimum number of
            nodes required in each partition generated by the cuts. Default is 1.
        return_partition: If True, also returns the partitions resulting after removing the arcs. Default is False.
        return_ccw_ordered_endpoints: If True, the arcs are put in CCW order of the cut (slower), otherwise they are unordered (faster). Default is False.

    Returns:
        List: A list of arc cut sets computed based on the input parameters.
    """

    # Loop through all possible combinations of edges and select those which are cut the diagram.
    for arcs in combinations(k.arcs, order):

        is_cut_set_good, partition = _is_arc_cut_set(k, arcs, minimum_partition_nodes=minimum_partition_nodes, return_partition=True)

        if not is_cut_set_good:
            continue

        if return_partition and len(partition) != 2:
            warnings.warn("Arc cut-set yielded more than two partitions, which is not yet supported.")
            continue

        # Return the ccw order of the cuts, i.e. a list of endpoints from the 0the partition and the 1st partition, respectively.
        if return_ccw_ordered_endpoints:

            # Two dicts, where keys are endpoints in the corresponding partition, values are endpoints other partition.
            twins = [dict((ep1, ep2) if ep1.node in p else (ep2, ep1) for ep1, ep2 in arcs) for p in partition]
            partition_endpoints = [set(twins[0].keys()), set(twins[1].keys())]

            # shows which endpoint is ccw next to which endpoint in every partition
            ccw_next = [dict(), dict()]

            """For each face in the cut set, find if there are any endpoint from our arcs. If there are,
            there should be two - one from each partition. And these two endpoints are "next" to each other. 
            If there are not, then we can just skip this face."""
            for face in k.faces:
                face_set = set(face)
                ep0_in_face = partition_endpoints[0] & face_set
                ep1_in_face = partition_endpoints[1] & face_set

                if not ep0_in_face and not ep1_in_face:
                    continue

                if len(ep0_in_face) != 1 or len(ep1_in_face) != 1:
                    raise ValueError("Face does not contains exactly one endpoint")

                ep0, = ep0_in_face
                ep1, = ep1_in_face
                ccw_next[0][ep0] = twins[1][ep1]
                ccw_next[1][ep1] = twins[0][ep0]

            # start generating the path (we knot what elements are ccw next to each other)
            paths = [[next(iter(ccw_next[0]))], [next(iter(ccw_next[1]))]]

            while len(paths[0]) < len(ccw_next[0]):
                paths[0].append(ccw_next[0][paths[0][-1]])
                paths[1].append(ccw_next[1][paths[1][-1]])

            yield (arcs, partition, paths) if return_partition else (arcs, paths)

        else:
            yield (arcs, partition) if return_partition else arcs



def arc_cut_sets(k: PlanarDiagram | OrientedPlanarDiagram, order: int, minimum_partition_nodes=1, return_partition=False, return_ccw_ordered_endpoints=False):
    """
    Computes the arc cut sets for a given planar diagram or oriented planar
    diagram. An arc cut sets is a set of arcs that, when removed, disconnects the diagram.

    Args:
        k: A PlanarDiagram or OrientedPlanarDiagram instance of the diagram for which the arc cut sets are to be computed.
        order: An integer representing the order of the cut. The order defines the number of arcs of the arc cut sets.
        minimum_partition_nodes: An integer specifying the minimum number of
            nodes required in each partition generated by the cuts. Default is 1.
        return_partition: If True, also returns the partitions resulting after removing the arcs. Default is False.
        return_ccw_ordered_endpoints: If True, the arcs are put in CCW order of the cut (slower), otherwise they are unordered (faster). Default is False.

    Returns:
        List: A list of arc cut sets computed based on the input parameters.
    """

    return list(_arc_cut_set_iterator(k, order, minimum_partition_nodes=minimum_partition_nodes, return_partition=return_partition, return_ccw_ordered_endpoints=return_ccw_ordered_endpoints))


def find_arc_cut_set(k: PlanarDiagram | OrientedPlanarDiagram, order: int, minimum_partition_nodes=1):
    """
    Find one arc cut set of size `order` in a planar diagram.

    Args:
        k: The planar diagram or oriented planar diagram to analyze.
        order: The number of arcs in the desired cut set.
        minimum_partition_nodes: The minimum required number of nodes in each resulting partition.
            Defaults to 1.

    Returns:
        A tuple containing the selected arcs if an arc cut set satisfying the criteria is found,
        or None if no such set exists.
    """

    try:
        return next(_arc_cut_set_iterator(k=k, order=order, minimum_partition_nodes=minimum_partition_nodes, return_partition=False, return_ccw_ordered_endpoints=False))
    except StopIteration:
        return None


def cut_decomposition(k: PlanarDiagram | OrientedPlanarDiagram, cut_path: tuple | list, vertex_maker="cut") -> list:

    """Cuts the diagram into two parts by cutting each arc with an endpoint in the cut path. The first component of
    the cut contains the nodes from the cut path.

    """

    k = k.copy()

    # Create 2*n new nodes (leafs of the endpoints created by the cut path)
    cut_nodes = multiple_unique_new_node_names(k, len(cut_path) * 2)
    k.add_vertices_from(cut_nodes, degree=1)

    # split arcs to the new vertices
    for i, endpoint in enumerate(cut_path):
        twin = k.twin(endpoint)

        k.set_endpoint(endpoint, (cut_nodes[2 * i], 0), create_using=type(twin), **twin.attr)
        k.set_endpoint((cut_nodes[2 * i], 0), endpoint, create_using=type(endpoint), **endpoint.attr)
        k.nodes[cut_nodes[2 * i]].attr[vertex_maker] = i
        k.set_endpoint(twin, (cut_nodes[2 * i + 1], 0), create_using=type(endpoint), **endpoint.attr)
        k.set_endpoint((cut_nodes[2 * i + 1], 0), twin, create_using=type(twin), **twin.attr)
        k.nodes[cut_nodes[2 * i + 1]].attr[vertex_maker] = i

    decomposition = disjoint_union_decomposition(k)
    decomposition.sort(key=lambda _: cut_path[0].node not in _.nodes)

    return decomposition





def cut_nodes(k: PlanarDiagram) -> set:
    """
    Identify the cut vertices (articulation nodes) in a planar diagram.
    
    A cut vertex is a node whose removal increases the number of connected components in the diagram. 
    In the context of this function, it detects nodes that belong to multiple faces in the planar diagram.
    
    Args:
        k (PlanarDiagram): The planar diagram to analyze.
    
    Returns:
        set: A set of nodes that are cut vertices (articulation points) in the diagram.
    """
    nodes = set()
    for f in k.faces:
        # keep nodes that repeat twice or more in a face
        counts = Counter(ep.node for ep in f)
        nodes |= {node for node, count in counts.items() if count >= 2}

    return nodes




if __name__ == "__main__":
    pass