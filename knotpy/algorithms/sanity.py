from collections import Counter

def sanity_check(k):
    """
    Perform a series of sanity checks on a given knot object `k` to validate its structure and properties.

    This function performs consistency checks on the structural elements of a knot object,
    including nodes, endpoints, arcs, faces, and certain mathematical properties like the Euler characteristic.
    It ensures that the topology of the knot is well-defined and satisfies required constraints.

    Parameters:
        k: An instance of a knot object. This object is expected to have the properties and methods
           required for the checks, such as nodes, endpoints, arcs, faces, degree, and twin.

    Returns:
        bool: True if all consistency checks pass.

    Raises:
        ValueError: If any of the checks fail, such as when:
            - Endpoint nodes are not in the set of nodes.
            - Endpoint positions are not valid for the given node degrees.
            - Nodes have unassigned (None) endpoints.
            - Duplicate endpoints are found.
            - The number of endpoints does not match twice the number of arcs.
            - Endpoints do not have valid twins.
            - Euler characteristic is not satisfied.
            - Faces are inconsistent, such as when nodes or endpoints are improperly represented in faces.
    """
    from knotpy.algorithms.disjoint_sum import number_of_disjoint_components
    from knotpy.algorithms.cut_set import cut_nodes
    from knotpy.classes.endpoint import Endpoint, OutgoingEndpoint, IngoingEndpoint

    if isinstance(k, (list, set, tuple)):
        return all(sanity_check(_) for _ in k)

    # TODO: empty graph without edges deos not work
    # TODO: also check directed graphs

    # Check if all endpoint nodes are in the set of global nodes.
    for ep in k.endpoints:
        if ep.node not in k.nodes:
            raise ValueError(f"Endpoint {ep} node {ep.node} is not in the expected nodes: {set(k.nodes)}")

    # Check if endpoint positions are in the node's degrees.
    for ep in k.endpoints:
        if k.degree(ep.node) <= ep.position:
            raise ValueError(f"Endpoint {ep} has bigger index than the node {ep.node} with degree {k.degree(ep.node)}")

    faces = list(k.faces)
    endpoints = list(k.endpoints)
    arcs = list(k.arcs)
    nodes = list(k.nodes)

    # Check if all endpoints are assigned.
    for n in nodes:
        for i in range(len(k.nodes[n])):
            if k.nodes[n][i] is None:
                raise ValueError(f"None endpoint found in node {n} at position {i}")

    # Check if all endpoints are different.
    if len(endpoints) != len(set(endpoints)):
        repeated_elements = [element for element, count in Counter(endpoints).items() if count > 1]
        raise ValueError(f"Endpoints {repeated_elements} repeat")

    # Check if number of endpoints match the number of arcs
    if len(endpoints) != len(arcs)*2:
        raise ValueError(f"There are more endpoints than twice the arcs. \nKnot: {k} \n endpoints: {endpoints}\n arcs {arcs}."
                         f"\n num. endpoints {len(endpoints)}, num. arcs: {len(arcs)}")

    # Check that all endpoints are assigned valid nodes and that twins match.
    for ep in endpoints:
        if ep.node not in k.nodes or not (0 <= ep.position < k.degree(ep.node)):
            ValueError(f"Endpoint {ep} does not match a node (invalid node or degree)")
        twin = k.twin(ep)
        twin_twin = k.twin(twin)
        if twin_twin != ep:
            raise ValueError(f"Twin {twin_twin} of twin {twin} is not the original endpoint {ep}")

    # Check the Euler characteristic.
    if (euler_characteristic := len(nodes) - len(arcs) + len(faces)) != 2:

        if euler_characteristic != number_of_disjoint_components(k) * 2:

           raise ValueError(f"Euler characteristic is not satisfied: {euler_characteristic} (expected 2). {k}")

    # Check if oriented diagrams have a consistent orientation
    if k.is_oriented():
        for ep in k.endpoints:
            assert type(ep) is OutgoingEndpoint or type(ep) is IngoingEndpoint, "Oriented diagram has non-oriented endpoints"

        for arc in k.arcs:
            ep1, ep2 = arc
            assert (type(ep1) is OutgoingEndpoint and type(ep2) is IngoingEndpoint) or (type(ep1) is IngoingEndpoint and type(ep2) is OutgoingEndpoint)
        for crossing in k.crossings:
            ep0, ep1, ep2, ep3 = k.nodes[crossing]
            assert type(ep0) is not type(ep2)
            assert type(ep1) is not type(ep3)
            assert type(ep0) is type(ep1) or type(ep0) is type(ep3)
            assert type(ep2) is type(ep1) or type(ep2) is type(ep3)


    """
    Check faces consistency. A bridge must appear twice in a face. A cut-vertex must appear degree-times in a one face.
    Every other node appears once in each face for degree-faces.
    """

    # Check that each node appears only once in a region, except if it is a cut-vertex.
    cut = cut_nodes(k)
    for face in faces:
        for node, count in Counter([ep.node for ep in face]).items():
            if node not in cut and count != 1:
                raise ValueError(f"The non-cut node {node} appears more then once in the face {face}")

    # Check that endpoints in faces are unique and that all endpoints are in the faces.
    face_endpoints = [ep for face in faces for ep in face]
    if len(face_endpoints) != len(set(face_endpoints)):
        raise ValueError("Same endpoints appear multiple times in a face")
    if len(face_endpoints) != len(endpoints):
        raise ValueError("Not all endpoints are in the faces")

    # Check that the number of nodes in face endpoints match the nodes degrees.
    face_nodes = [ep.node for ep in face_endpoints]
    for node, count in Counter(face_nodes).items():
        if k.degree(node) != count:
            raise ValueError(f"Faces of the node {node} does not match the degree")

    # TODO: this face checking is not 100% fail-safe. Additional checks must be made.

    return True

if __name__ == "__main__":
    from knotpy import PlanarDiagram

    graph_tree = PlanarDiagram()
    graph_tree.set_arcs_from("a0b0,a1c0,a2d0")
    sanity_check(graph_tree)

    # graph_nice = PlanarDiagram()
    # graph_nice.set_arcs_from("a0b0,a1c2,a2d1,b1c0,c1d0")
    # print(graph_nice)
    # sanity_check(graph_nice)

    # graph_funky = PlanarDiagram()
    # graph_funky.set_arcs_from("a0b0,b1b3,b2c0,c1d0,c2e0,d1d2,d3e1,e2e3,e4e5")
    # sanity_check(graph_funky)


    graph_non_planar = PlanarDiagram()
    graph_non_planar.set_arcs_from("a0b0,a1b1,a2b2")
    print(*graph_non_planar.faces)
    sanity_check(graph_non_planar)