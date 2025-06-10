
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.cut_set import arc_cut_sets, cut_decomposition
from knotpy.algorithms.disjoint_union import number_of_disjoint_components, disjoint_union



def tangle_decompositions(k: PlanarDiagram | OrientedPlanarDiagram, minimal_component_nodes: int = 2) -> list:
    """
    Return all tangle decompositions of a diagram. Each component of the decomposition must have at least minimal_nodes_in_component
    nodes in every component.
    """

    if k.nodes("tangle_endpoints"):
        raise ValueError("The diagram already has tangle endpoints")

    if number_of_disjoint_components(k) != 1:
        raise ValueError("Cannot compute tangle decomposition of a diagram with more than one disjoint component")

    return [
        cut_decomposition(k, ccw_endpoints[0], vertex_maker="tangle_endpoint")
        for arc_cut, ccw_endpoints in arc_cut_sets(k, order=4, minimum_partition_nodes=minimal_component_nodes, return_partition=False, return_ccw_ordered_endpoints=True)
    ]



def compose_tangles(tangle1 : PlanarDiagram | OrientedPlanarDiagram, tangle2: PlanarDiagram | OrientedPlanarDiagram):
    """ Compose two tangles by connecting all their endpoints."""

    k = disjoint_union(tangle1, tangle2)

    for i in range(4):
        leafs = k.nodes(tangle_endpoint=i)
        if len(leafs) != 2:
            raise ValueError("Cannot compose tangles: endpoint labels are missing or incorrect")
        endpoints = [k.twin(k.endpoints[leafs[0]][0]), k.twin(k.endpoints[leafs[1]][0])]
        k.set_arc(endpoints)
        k.remove_nodes_from(leafs, remove_incident_endpoints=False)

    return k


def rotate(tangle: PlanarDiagram | OrientedPlanarDiagram, angle: int, inplace=True) -> PlanarDiagram | OrientedPlanarDiagram:
    """Rotate a tangle by angle degrees."""
    angle = angle % 360
    if angle not in [0, 90, 180, 270]:
        raise ValueError("Angle must be a multiple of 90 degrees")

    if not inplace:
        tangle = tangle.copy()

    for node in tangle.nodes("tangle_endpoint"):
        tangle.nodes[node].attr["tangle_endpoint"] = (tangle.nodes[node].attr["tangle_endpoint"] + (angle // 90)) % 4

    return tangle



def is_integer_tangle(tangle: PlanarDiagram | OrientedPlanarDiagram) -> bool:
    """Check if a tangle is an integer tangle. Can be a "horizontal" or a "vertical" integer tangle."""

    # TODO: check if conditions are ok (there are n-1 number of 2-faces)

    # all nodes must be crossings
    if (number_of_crossings := tangle.number_of_crossings) != len(tangle) - 4:
        return False

    # all faces but one must be bigons
    faces = tangle.faces()
    if sum(len(face) == 2 for face in faces) != number_of_crossings - 1:
        return False

    return True
