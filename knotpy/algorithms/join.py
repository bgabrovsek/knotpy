from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.classes.endpoint import IngoingEndpoint, OutgoingEndpoint, Endpoint
from knotpy.classes.node import Vertex, Crossing
from knotpy.algorithms.disjoint_union import disjoint_union
from knotpy.algorithms.naming import unique_new_node_name

def bridge_join(a: PlanarDiagram | OrientedPlanarDiagram, b: PlanarDiagram | OrientedPlanarDiagram, arcs):
    """Join two planar diagrams by bridging the arcs in arcs."""


    if type(a) != type(b):
        raise TypeError("The two diagrams must be of the same type.")


    # get the two arcs or take first available ones if they are not given
    arc_a, arc_b = arcs if arcs is not None else (next(iter(a.arcs)), next(iter(b.arcs)))

    ep_a_1, ep_a_2 = arc_a
    ep_b_1, ep_b_2 = arc_b

    ab, node_relabel_dicts = disjoint_union(a, b, return_relabel_dictionaries=True)

    def r(ep):
        return node_relabel_dicts[ep.node], ep.position

    ab.add_node(len(ab.nodes))
    ab.add_node(node_for_adding=(va := unique_new_node_name(ab)), create_using=Vertex, degree=3)
    ab.add_node(node_for_adding=(vb := unique_new_node_name(ab)), create_using=Vertex, degree=3)

    ab.set_endpoint((va, 0), r(ep_a_1), create_using=type(ep_a_1), **ep_a_1.attr)
    ab.set_endpoint(r(ep_a_1), (va, 0), create_using=type(ep_a_2), **ep_a_2.attr)
    ab.set_endpoint((va, 1), r(ep_a_2), create_using=type(ep_a_2), **ep_a_2.attr)
    ab.set_endpoint(r(ep_a_2), (va, 1), create_using=type(ep_a_1), **ep_a_1.attr)

    ab.set_endpoint((vb, 0), r(ep_b_1), create_using=type(ep_b_1), **ep_b_1.attr)
    ab.set_endpoint(r(ep_b_1), (vb, 0), create_using=type(ep_b_2), **ep_b_2.attr)
    ab.set_endpoint((vb, 1), r(ep_b_2), create_using=type(ep_b_2), **ep_b_2.attr)
    ab.set_endpoint(r(ep_b_2), (vb, 1), create_using=type(ep_b_1), **ep_b_1.attr)

    type_b = IngoingEndpoint if ab.is_oriented else Endpoint
    type_a = OutgoingEndpoint if ab.is_oriented else Endpoint

    ab.set_endpoint((va, 2), (vb, 2), create_using=type_b)
    ab.set_endpoint((vb, 2), (va, 2), create_using=type_a)

    if a.framing is not None or b.framing is not None:
        ab.framing = (a.framing or 0) + (b.framing or 0)

    return ab



def crossing_join(a: PlanarDiagram | OrientedPlanarDiagram, b: PlanarDiagram | OrientedPlanarDiagram, arcs):
    """Join two planar diagrams by a cut-crossing (twisted connected sum)."""

    if type(a) != type(b):
        raise TypeError("The two diagrams must be of the same type.")


    # get the two arcs or take first available ones if they are not given
    arc_a, arc_b = arcs if arcs is not None else (next(iter(a.arcs)), next(iter(b.arcs)))

    ep_a_1, ep_a_2 = arc_a
    ep_b_1, ep_b_2 = arc_b

    ab, node_relabel_dicts = disjoint_union(a, b, return_relabel_dictionaries=True)

    def r(ep):
        return node_relabel_dicts[ep.node], ep.position

    ab.add_node(len(ab.nodes))
    ab.add_crossing(crossing_for_adding=(c := unique_new_node_name(ab)))

    # Switch endpoints if orientation does not match
    if type(ep_a_1) is not Endpoint and type(ep_a_1) != type(ep_b_1):
        ep_b_1, ep_b_2 = ep_b_2, ep_b_1

    ab.set_endpoint((c, 0), r(ep_a_1), create_using=type(ep_a_1), **ep_a_1.attr)
    ab.set_endpoint(r(ep_a_1), (c, 0), create_using=type(ep_a_2), **ep_a_2.attr)

    ab.set_endpoint((c, 1), r(ep_a_2), create_using=type(ep_a_2), **ep_a_2.attr)
    ab.set_endpoint(r(ep_a_2), (c, 1), create_using=type(ep_a_1), **ep_a_1.attr)

    ab.set_endpoint((c, 2), r(ep_b_1), create_using=type(ep_b_1), **ep_b_1.attr)
    ab.set_endpoint(r(ep_b_1), (c, 2), create_using=type(ep_b_2), **ep_b_2.attr)

    ab.set_endpoint((c, 3), r(ep_b_2), create_using=type(ep_b_2), **ep_b_2.attr)
    ab.set_endpoint(r(ep_b_2), (c, 3), create_using=type(ep_b_1), **ep_b_1.attr)


    return ab