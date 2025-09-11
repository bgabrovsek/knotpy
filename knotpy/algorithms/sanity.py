"""
Check if the diagram makes sense (is planar, consistent, etc.).
"""
__all__ = ["sanity_check"]
__version__ = "0.2"
__author__ = "Boštjan Gabrovšek"

from collections import Counter

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram, Diagram, DiagramCollection


def sanity_check_raise_exception(k: Diagram | DiagramCollection) -> bool:
    """
    Run structural sanity checks on a planar (or oriented) diagram.

    Validates node/endpoint consistency, arc–endpoint counts, twin relationships,
    Euler characteristic (per component), face coherence, and (for oriented
    diagrams) endpoint orientations.

    Args:
        k: A single diagram or a collection of diagrams.

    Returns:
        True if all checks pass; raises on failure.
    """
    # Allow collections
    if isinstance(k, (list, set, tuple)):
        return all(sanity_check(di) for di in k)

    # Lazy imports to keep import time low
    from knotpy.algorithms.disjoint_union import number_of_disjoint_components
    from knotpy.algorithms.cut_set import cut_nodes
    from knotpy.classes.endpoint import Endpoint, OutgoingEndpoint, IngoingEndpoint

    if not isinstance(k, (PlanarDiagram, OrientedPlanarDiagram)):
        raise TypeError(f"Expected a PlanarDiagram/OrientedPlanarDiagram, got {type(k)}")

    # 1) Endpoint node membership
    for ep in k.endpoints:
        if ep.node not in k.nodes:
            raise ValueError(f"Endpoint {ep} references missing node {ep.node}; available: {set(k.nodes)}")

    # 2) Endpoint positions within node degree
    for ep in k.endpoints:
        deg = k.degree(ep.node)
        if not (0 <= ep.position < deg):
            raise ValueError(f"Endpoint {ep} has position {ep.position} outside node degree {deg}")

    faces = list(k.faces)
    endpoints = list(k.endpoints)
    arcs = list(k.arcs)
    nodes = list(k.nodes)

    # 3) No None endpoints in node incidence lists
    for n in nodes:
        for i in range(len(k.nodes[n])):
            if k.nodes[n][i] is None:
                raise ValueError(f"None endpoint found in node {n} at position {i}")

    # 4) Endpoints are unique
    if len(endpoints) != len(set(endpoints)):
        dup = [e for e, c in Counter(endpoints).items() if c > 1]
        raise ValueError(f"Duplicate endpoints detected: {dup}")

    # 5) Endpoints count matches twice the arcs
    if len(endpoints) != 2 * len(arcs):
        raise ValueError(
            "Endpoints count must equal 2×|arcs|.\n"
            f"Diagram: {k}\n"
            f"#endpoints={len(endpoints)}, #arcs={len(arcs)}\n"
            f"Endpoints: {endpoints}\nArcs: {arcs}"
        )

    # 6) All twins valid and involutive
    for ep in endpoints:
        if ep.node not in k.nodes or not (0 <= ep.position < k.degree(ep.node)):
            raise ValueError(f"Endpoint {ep} does not match a node (invalid node or degree)")
        twin = k.twin(ep)
        if k.twin(twin) != ep:
            raise ValueError(f"twin(twin({ep})) != {ep}; got {k.twin(twin)}")

    # 7) Euler characteristic per component
    euler_characteristic = len(nodes) - len(arcs) + len(faces)
    expected = 2 * number_of_disjoint_components(k)
    if euler_characteristic != expected:
        raise ValueError(f"Euler characteristic {euler_characteristic} != {expected} (2×components). Diagram: {k}")

    # 8) Oriented diagrams: endpoint/crossing orientation consistency
    if k.is_oriented():
        for ep in k.endpoints:
            if not isinstance(ep, (OutgoingEndpoint, IngoingEndpoint)):
                raise ValueError("Oriented diagram has non-oriented endpoints")

        for ep1, ep2 in k.arcs:
            pair = (type(ep1), type(ep2))
            if pair not in {(OutgoingEndpoint, IngoingEndpoint), (IngoingEndpoint, OutgoingEndpoint)}:
                raise ValueError(f"Arc {ep1, ep2} is not oppositely oriented")

        for crossing in k.crossings:
            ep0, ep1, ep2, ep3 = k.nodes[crossing]
            if type(ep0) is type(ep2):
                raise ValueError(f"Crossing {crossing}: opposite endpoints (0,2) must have opposite orientation")
            if type(ep1) is type(ep3):
                raise ValueError(f"Crossing {crossing}: opposite endpoints (1,3) must have opposite orientation")
            # One of (0,1)/(0,3) must match, symmetrically for ep2
            if not (type(ep0) is type(ep1) or type(ep0) is type(ep3)):
                raise ValueError(f"Crossing {crossing}: ep0 must match one of ep1/ep3")
            if not (type(ep2) is type(ep1) or type(ep2) is type(ep3)):
                raise ValueError(f"Crossing {crossing}: ep2 must match one of ep1/ep3")

    # 9) Faces consistency
    #    - Non-cut nodes appear at most once per face
    #    - Face endpoints unique and cover all endpoints
    #    - Node degree equals its appearances across faces
    cut = cut_nodes(k)

    for face in faces:
        counts = Counter(ep.node for ep in face)
        for node, count in counts.items():
            if node not in cut and count != 1:
                raise ValueError(f"Non-cut node {node} appears {count} times in face {face}")

    face_endpoints = [ep for face in faces for ep in face]
    if len(face_endpoints) != len(set(face_endpoints)):
        raise ValueError("Some endpoints appear multiple times across faces")
    if len(face_endpoints) != len(endpoints):
        raise ValueError("Not all endpoints are represented in faces")

    per_node_face_count = Counter(ep.node for ep in face_endpoints)
    for node, count in per_node_face_count.items():
        if k.degree(node) != count:
            raise ValueError(f"Face incidence count {count} for node {node} != degree {k.degree(node)}")

    return True



def sanity_check(k: Diagram | DiagramCollection) -> bool:
    """
    Run structural sanity checks on a planar (or oriented) diagram.

    Validates node/endpoint consistency, arc–endpoint counts, twin relationships,
    Euler characteristic (per component), face coherence, and (for oriented
    diagrams) endpoint orientations.

    Args:
        k: A single diagram or a collection of diagrams.

    Returns:
        True if all checks pass, false otherwise.
    """
    # Allow collections
    try:
       sanity_check_raise_exception(k)
    except ValueError:
       return False
    return True

if __name__ == "__main__":
    pass
