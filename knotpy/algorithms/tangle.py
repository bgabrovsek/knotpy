__all__ = ["tangle_decompositions", "is_integer_tangle", "compose_tangles"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek"

from knotpy.classes.planardiagram import Diagram
from knotpy.algorithms.cut_set import arc_cut_sets, cut_decomposition
from knotpy.algorithms.disjoint_union import number_of_disjoint_components, disjoint_union


def tangle_decompositions(k: Diagram, minimal_component_nodes: int = 2) -> list:
    """Return all possible tangle decompositions of a knot diagram.

    Each component in the decomposition must have at least
    `minimal_component_nodes` nodes.

    Args:
        k: Input diagram (planar or oriented).
        minimal_component_nodes: Minimum number of nodes per component.

    Raises:
        ValueError: If the diagram already has `tangle_endpoints` in any node,
            or if the diagram has more than one disjoint component.

    Returns:
        A list of decomposed tangle diagrams.
    """
    # Avoid decomposing a diagram that already has tangle endpoints marked
    if any("tangle_endpoints" in node.attr for node in k.nodes.values()):
        raise ValueError("The diagram already has tangle endpoints")

    # Ensure the diagram is connected (single component)
    if number_of_disjoint_components(k) != 1:
        raise ValueError(
            "Cannot compute tangle decomposition of a diagram "
            "with more than one disjoint component"
        )

    # Compute all valid decompositions from arc cut sets
    return [
        cut_decomposition(k, ccw_endpoints[0], vertex_maker="tangle_endpoint")
        for arc_cut, ccw_endpoints in arc_cut_sets(
            k,
            order=4,
            minimum_partition_nodes=minimal_component_nodes,
            return_partition=False,
            return_ccw_ordered_endpoints=True
        )
    ]


def compose_tangles(tangle1: Diagram, tangle2: Diagram) -> Diagram:
    """Compose two tangles by connecting matching tangle endpoints.

    Both tangles must have endpoints labeled with `tangle_endpoint` values
    0–3. Each label must appear exactly twice across the combined diagram.

    Args:
        tangle1: First tangle diagram.
        tangle2: Second tangle diagram.

    Raises:
        ValueError: If endpoint labels are missing or not paired correctly.

    Returns:
        The composed tangle diagram.
    """
    k = disjoint_union(tangle1, tangle2)

    # Connect endpoints by matching their "tangle_endpoint" labels
    for i in range(4):
        # Collect nodes with the given endpoint label
        leafs = [
            node for node in k.nodes
            if k.nodes[node].attr.get("tangle_endpoint") == i
        ]
        if len(leafs) != 2:
            raise ValueError(
                "Cannot compose tangles: endpoint labels are missing or incorrect"
            )

        # Identify the endpoints to connect
        endpoints = [
            k.twin(k.endpoints[leafs[0]][0]),
            k.twin(k.endpoints[leafs[1]][0])
        ]

        # Create the connecting arc and remove the leaf nodes
        k.set_arc(endpoints)
        k.remove_nodes_from(leafs, remove_incident_endpoints=False)

    return k


def rotate(tangle: Diagram, angle: int, inplace: bool = True) -> Diagram:
    """Rotate a tangle diagram by a multiple of 90 degrees.

    Rotation changes the `tangle_endpoint` labels modulo 4.

    Args:
        tangle: The tangle diagram to rotate.
        angle: Rotation angle in degrees (must be 0, 90, 180, or 270).
        inplace: If True, modifies the tangle in place. If False, returns a copy.

    Raises:
        ValueError: If angle is not a multiple of 90.

    Returns:
        The rotated tangle diagram.
    """
    angle = angle % 360
    if angle not in [0, 90, 180, 270]:
        raise ValueError("Angle must be a multiple of 90 degrees")

    if not inplace:
        tangle = tangle.copy()

    # Adjust tangle_endpoint labels by the rotation step
    for node in tangle.nodes("tangle_endpoint"):
        tangle.nodes[node].attr["tangle_endpoint"] = (
            tangle.nodes[node].attr["tangle_endpoint"] + (angle // 90)
        ) % 4

    return tangle


def is_integer_tangle(tangle: Diagram) -> bool:
    """Check if a tangle is an integer tangle.

    An integer tangle can be "horizontal" or "vertical".
    Conditions checked:
      - Diagram has exactly `n - 4` crossings (where `n` is the number of nodes).
      - All but one of its faces are bigons (2-gons).

    Args:
        tangle: The tangle diagram to check.

    Returns:
        True if the tangle is an integer tangle, False otherwise.
    """
    # Number of crossings should be exactly nodes - 4
    number_of_crossings = tangle.number_of_crossings
    if number_of_crossings != len(tangle) - 4:
        return False

    # All faces except one must be bigons
    faces = tangle.faces()
    if sum(len(face) == 2 for face in faces) != number_of_crossings - 1:
        return False

    return True