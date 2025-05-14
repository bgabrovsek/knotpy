from collections import Counter

def sanity_check(k):
    from knotpy.algorithms.disjoint_sum import number_of_disjoint_components
    """
    Perform a consistency check on the planar diagram `k`.

    This function verifies the structural integrity of the planar diagram by
    checking for issues such as `None` endpoints, repeated endpoints, mismatched
    endpoint counts, and incorrect twin assignments (twins are pairs of endpoints of the same arc connecting two nodes).

    :param k: The planar diagram to check.
    :type k: PlanarDiagram
    :raises ValueError: If any of the following conditions are met:
        - A node has an endpoint set to `None`.
        - An endpoint appears more than once.
        - The number of endpoints does not match twice the number of arcs.
        - Not all nodes have associated endpoints.
        - An endpoint's twin does not correctly reference back to the original.
    :return: True if all checks pass.
    :rtype: bool
    """

    _print_details = False

    for ep in k.endpoints:
        if ep.node not in k.nodes:
            raise ValueError(f"Endpoint {ep} node {ep.node} is not in the expected nodes: {set(k.nodes)}")

    for ep in k.endpoints:
        if k.degree(ep.node) <= ep.position:
            raise ValueError(f"Endpoint {ep} has bigger index than the node {ep.node} with degree {k.degree(ep.node)}")

    faces = list(k.faces)  # TODO: empty graph without edges deos not work
    endpoints = list(k.endpoints)
    arcs = list(k.arcs)
    nodes = list(k.nodes)

    if _print_details:
        print(f"Nodes: {nodes}")
        print(f"Endpoints: {endpoints}")
        print(f"Arcs: {arcs}")
        print(f"Faces: {faces}")

    # TODO: also check directed graphs
        
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


    # if set(ep.node for ep in endpoints) != set(nodes):
    #     raise ValueError("Not all nodes have endpoints")

    # Check that all endpoints are assigned valid nodes and that twins match.
    for ep in endpoints:
        if ep.node not in k.nodes or not (0 <= ep.position < k.degree(ep.node)):
            ValueError(f"Endpoint {ep} does not match a node (invalid node or degree)")
        twin = k.twin(ep)
        twin_twin = k.twin(twin)
        if twin_twin != ep:
            raise ValueError(f"Twin {twin_twin} of twin {twin} is not the original endpoint {ep}")

    if _print_details:
        print(f"Nodes ({len(nodes)}) + Arcs ({len(arcs)}) + Faces ({len(faces)}) = {len(nodes) - len(arcs) + len(faces)}")
    # Check Euler characteristic
    if (euler_characteristic := len(nodes) - len(arcs) + len(faces)) != 2:

        if euler_characteristic != number_of_disjoint_components(k) * 2:

           raise ValueError(f"Euler characteristic is not satisfied: {euler_characteristic} (expected 2). {k}")


    """
    Check faces consistency. A bridge must appear twice in a face. A cut-vertex must appear degree-times in a one face.
    Every other node appears once in each face for degree-faces.
    """

    from knotpy.algorithms.cut_set import cut_nodes

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