# knotpy/algorithms/join.py

"""
Join diagrams by a bridge or by introducing a crossing.
"""

__all__ = ["bridge_join", "crossing_join"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"


from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint, Arc
from knotpy.classes.node import Vertex, Crossing
from knotpy.classes.planardiagram import Diagram, PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.disjoint_union import disjoint_union
from knotpy.algorithms.naming import unique_new_node_name



def _unpack_arc(arc: Arc) -> tuple[Endpoint, Endpoint]:
    """Return the two endpoints from a frozenset arc."""
    ep1, ep2 = tuple(arc)
    return ep1, ep2


def bridge_join(a: Diagram, b: Diagram, arcs: tuple | None) -> Diagram:
    """
    Join two diagrams by inserting a length-1 bridge (a degree-3 vertex on each side, linked together).

    Args:
        a, b: Two diagrams of the same type.
        arcs: A pair of arcs (one from `a`, one from `b`) as frozensets of two endpoints.
              If None, the first available arc from each diagram is used.

    Returns:
        A new diagram of the same type that is the bridged join of `a` and `b`.

    Raises:
        TypeError: If `a` and `b` are not of the same diagram type.
    """
    if type(a) is not type(b):
        raise TypeError("The two diagrams must be of the same type.")

    # pick arcs
    if arcs is None:
        arc_a, arc_b = next(iter(a.arcs)), next(iter(b.arcs))
    else:
        arc_a, arc_b = arcs

    ep_a_1, ep_a_2 = _unpack_arc(arc_a)
    ep_b_1, ep_b_2 = _unpack_arc(arc_b)

    ab, relabel_dicts = disjoint_union(a, b, return_relabel_dicts=True)
    map_a, map_b = relabel_dicts

    def relabel_from_a(ep: Endpoint) -> tuple:
        return map_a[ep.node], ep.position

    def relabel_from_b(ep: Endpoint) -> tuple:
        return map_b[ep.node], ep.position

    # internal bridge vertices
    va = unique_new_node_name(ab)
    vb = unique_new_node_name(ab)
    ab.add_node(node_for_adding=va, create_using=Vertex, degree=3)
    ab.add_node(node_for_adding=vb, create_using=Vertex, degree=3)

    # connect A's arc to va
    ab.set_endpoint((va, 0), relabel_from_a(ep_a_1), create_using=type(ep_a_1), **ep_a_1.attr)
    ab.set_endpoint(relabel_from_a(ep_a_1), (va, 0), create_using=type(ep_a_2), **ep_a_2.attr)
    ab.set_endpoint((va, 1), relabel_from_a(ep_a_2), create_using=type(ep_a_2), **ep_a_2.attr)
    ab.set_endpoint(relabel_from_a(ep_a_2), (va, 1), create_using=type(ep_a_1), **ep_a_1.attr)

    # connect B's arc to vb
    ab.set_endpoint((vb, 0), relabel_from_b(ep_b_1), create_using=type(ep_b_1), **ep_b_1.attr)
    ab.set_endpoint(relabel_from_b(ep_b_1), (vb, 0), create_using=type(ep_b_2), **ep_b_2.attr)
    ab.set_endpoint((vb, 1), relabel_from_b(ep_b_2), create_using=type(ep_b_2), **ep_b_2.attr)
    ab.set_endpoint(relabel_from_b(ep_b_2), (vb, 1), create_using=type(ep_b_1), **ep_b_1.attr)

    # bridge between va and vb (respect orientation if present)
    is_oriented = ab.is_oriented()
    typ_in = IngoingEndpoint if is_oriented else Endpoint
    typ_out = OutgoingEndpoint if is_oriented else Endpoint

    ab.set_endpoint((va, 2), (vb, 2), create_using=typ_in)
    ab.set_endpoint((vb, 2), (va, 2), create_using=typ_out)

    # framing
    if a.framing is not None or b.framing is not None:
        ab.framing = (a.framing or 0) + (b.framing or 0)

    return ab


def crossing_join(a: Diagram, b: Diagram, arcs: tuple | None) -> Diagram:
    """
    Join two diagrams by a *cut crossing* (twisted connected sum).

    Args:
        a:
        b:
        arcs: A pair of arcs (one from `a`, one from `b`) as frozensets of two endpoints.
              If None, the first available arc from each diagram is used.

    Returns:
        A new diagram with a new crossing that joins the two inputs along the chosen arcs.

    Raises:
        TypeError: If `a` and `b` are not of the same diagram type.
    """
    if type(a) is not type(b):
        raise TypeError("The two diagrams must be of the same type.")

    # pick arcs
    if arcs is None:
        arc_a, arc_b = next(iter(a.arcs)), next(iter(b.arcs))
    else:
        arc_a, arc_b = arcs

    ep_a_1, ep_a_2 = _unpack_arc(arc_a)
    ep_b_1, ep_b_2 = _unpack_arc(arc_b)

    ab, relabel_dicts = disjoint_union(a, b, return_relabel_dicts=True)
    map_a, map_b = relabel_dicts

    def relabel_from_a(ep: Endpoint) -> tuple:
        return map_a[ep.node], ep.position

    def relabel_from_b(ep: Endpoint) -> tuple:
        return map_b[ep.node], ep.position

    # add the crossing
    c = unique_new_node_name(ab)
    ab.add_crossing(crossing_for_adding=c)

    # For oriented diagrams, ensure we connect opposite directions from the two arcs.
    if ab.is_oriented() and (type(ep_a_1) == type(ep_b_1)):  # both ingoing or both outgoing → flip B
        ep_b_1, ep_b_2 = ep_b_2, ep_b_1

    # connect crossing half-edges: (0,1) for arc_a; (2,3) for arc_b
    ab.set_endpoint((c, 0), relabel_from_a(ep_a_1), create_using=type(ep_a_1), **ep_a_1.attr)
    ab.set_endpoint(relabel_from_a(ep_a_1), (c, 0), create_using=type(ep_a_2), **ep_a_2.attr)

    ab.set_endpoint((c, 1), relabel_from_a(ep_a_2), create_using=type(ep_a_2), **ep_a_2.attr)
    ab.set_endpoint(relabel_from_a(ep_a_2), (c, 1), create_using=type(ep_a_1), **ep_a_1.attr)

    ab.set_endpoint((c, 2), relabel_from_b(ep_b_1), create_using=type(ep_b_1), **ep_b_1.attr)
    ab.set_endpoint(relabel_from_b(ep_b_1), (c, 2), create_using=type(ep_b_2), **ep_b_2.attr)

    ab.set_endpoint((c, 3), relabel_from_b(ep_b_2), create_using=type(ep_b_2), **ep_b_2.attr)
    ab.set_endpoint(relabel_from_b(ep_b_2), (c, 3), create_using=type(ep_b_1), **ep_b_1.attr)

    return ab