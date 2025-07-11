"""Layout functions for drawing a planar graph.
"""

from itertools import chain
from collections import defaultdict
import math

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.classes.node import Vertex, Crossing
from knotpy.utils.circlepack import CirclePack
from knotpy.algorithms.topology import loops, kinks, bridges
from knotpy.algorithms.disjoint_union import number_of_disjoint_components
from knotpy.algorithms.connected_sum import connected_sum
from knotpy.drawing._support import _visible
from knotpy.utils.geometry import (Circle, CircularArc, Line, Segment, perpendicular_arc, is_angle_between, antipode,
                                   tangent_line, middle, bisector, bisect, split,
                                   perpendicular_arc_through_point, BoundingBox, weighted_circle_center_mean, orient_arc, arc_from_circle_and_points, arc_from_diamater)

from knotpy.drawing.alignment import canonically_rotate_circles

__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'
__all__ = ['layout_circle_packing']

"""CirclePack.py
Compute circle packings according to the Koebe-Thurston-Andreev theory,
Following data numerical algorithm by C. R. Collins and K. Stephenson,
"A Circle Packing Algorithm", Comp. Geom. Theory and Appl. 2003.

AUTHORS: ...
"""

# def _choose_closest(elements, point):
#     """Choose the closest element (Segment or Circular arc) based on the proximity of its endpoints to a given point.
#
#     Args:
#         elements (list): A list of geometric elements. Each element is either an instance of the CircularArc or Segment class.
#         point (complex): A complex number representing the point whose proximity to the elements' endpoints needs to be determined.
#
#     Returns:
#         CircularArc or Segment: The element (either CircularArc or Segment) whose endpoint is
#         closest to the given point.
#     """
#     distances = []
#     for i, element in enumerate(elements):
#
#         if isinstance(element, CircularArc):
#             distances.append((min(abs(element(element.theta1) - point), abs(element(element.theta2) - point)), i))
#         elif isinstance(element, Segment):
#             distances.append((min(abs(element.A - point), abs(element(element.B - point))), i))
#         else:
#             raise ValueError("layout_circle_packing: element is neither CircularArc nor Segment")
#
#         distances.sort()
#         return elements[distances[0][1]]


def _sort_geometric_arcs(garc1: CircularArc | Segment, garc2: CircularArc | Segment, point1: Circle | complex, point2: Circle | complex):
    """Sorts two geometric arcs based on their proximity to two given points.

    This function takes two geometric arcs (`garc1` and `garc2`), and two points
    (`point1` and `point2`) and determines which arc is closest to each point.
    The arcs can either be circular arcs or line segments. If the closest arc
    for both points ends up being the same, an exception is raised. The arcs
    are returned in such a way that the first arc corresponds to the arc nearest
    `point1`, and the second arc corresponds to the arc nearest `point2`.

    Args:
        garc1: A geometric arc, either a CircularArc or Segment.
        garc2: Another geometric arc, either a CircularArc or Segment.
        point1: The first point, either a Circle or a complex number, to compare against the arcs.
        point2: The second point, either a Circle or a complex number, to compare against the arcs.

    Returns:
        Tuple[Union[CircularArc, Segment], Union[CircularArc, Segment]]: A tuple
        containing two geometric arcs where the first arc is the closest to `point1`
        and the second arc is closest to `point2`.

    Raises:
        ValueError: If both points are determined to be closest to the same arc,
            making it impossible to sort the arcs uniquely.
    """

    point1 = point1.center if isinstance(point1, Circle) else point1
    point2 = point2.center if isinstance(point2, Circle) else point2

    dist_arc1_point1 = min(abs(garc1.A - point1), abs(garc1.B - point1))
    dist_arc1_point2 = min(abs(garc1.A - point2), abs(garc1.B - point2))
    dist_arc2_point1 = min(abs(garc2.A - point1), abs(garc2.B - point1))
    dist_arc2_point2 = min(abs(garc2.A - point2), abs(garc2.B - point2))

    point1_arc = garc1 if dist_arc1_point1 < dist_arc2_point1 else garc2
    point2_arc = garc1 if dist_arc1_point2 < dist_arc2_point2 else garc2

    if point1_arc == point2_arc:
        raise ValueError("layout_circle_packing: cannot sort the arcs")

    return point1_arc, point2_arc


def circle_packing(k: PlanarDiagram | OrientedPlanarDiagram):
    """
    Return the layout for a planar diagram obtained by circle packing. See: https://katlas.org/wiki/Drawing_Planar_Diagrams

    This function calculates a circle packing representation for a given planar
    diagram. Each component (nodes, edges, or faces) of the diagram is represented
    by a circle in the output layout.

    Args:
        k (PlanarDiagram | OrientedPlanarDiagram): The planar diagram for which
            the circle packing layout needs to be computed.

    Raises:
        ValueError: If the planar diagram contains kinks, loops, bridges, or
            disjoint components.

    Returns:
        dict: Mapping of elements (nodes, edges, regions) of the diagram to Circle
            objects, which encode the position and radius of the circles in the
            layout.
    """

    if kinks(k):
        raise ValueError("Circle packing layout failed: the knotted diagram contains kinks")
    if loops(k):
        raise ValueError("Circle packing layout failed: the knotted diagram contains loops")
    if bridges(k):
        raise ValueError("Circle packing layout failed: the knotted diagram contains bridges")
    if number_of_disjoint_components(k) > 1:
        raise ValueError("Circle packing layout failed: the knotted diagram contains disjoint components")

    _debug = False
    external_node_radius = 1.0  # radius of external circles corresponding to nodes
    external_arc_radius = 0.5  # radius of external circles corresponding to arcs

    # get external endpoints if they exists
    external_endpoints = [ep for ep in k.endpoints if "outer" in ep.attr and ep.attr["outer"] == True]
    external_endpoints.extend([ep for ep in k.endpoints if "external" in ep.attr and ep.attr["external"] == True])

    faces = list(k.faces)

    if external_endpoints:
        external_face = [face for face in faces if set(face).issuperset(external_endpoints)]

        if len(external_face) != 1:
            raise ValueError("Circle packing layout failed: the knotted diagram contains multiple external faces/regions")
        external_face = external_face[0]
    else:
        external_face = min(faces, key=lambda r: (-len(r), r))  # sort by longest, then by lexicographical order
    print("External face:", external_face)
    arcs = list(k.arcs)

    # Create dictionaries that map all endpoints to faces, arcs,...

    ep_to_arc_dict = {ep: arc for arc in arcs for ep in arc}
    ep_to_face_dict = {ep: face for face in faces for ep in face}

    faces.remove(external_face)  # the circle packing does not need the external face

    # add external nodes and arcs to the set of external circles
    external_circles = {ep.node: external_node_radius for ep in external_face} \
                       | {ep_to_arc_dict[ep]: external_arc_radius for ep in external_face}  # nodes & arcs

    # face -> arc / node
    internal_circles = {face: list(chain(*((ep_to_arc_dict[ep], ep.node) for ep in face))) for face in faces}

    # node -> face / arc
    internal_circles |= {v: list(chain(*((ep_to_arc_dict[ep], ep_to_face_dict[ep]) for ep in k.nodes[v]))) for v in k.nodes}

    # arc -> face / node
    internal_circles |= {frozenset({ep0, ep1}): [ep_to_face_dict[ep1], ep0.node, ep_to_face_dict[ep0], ep1.node] for ep0, ep1 in arcs}
    internal_circles = {key: internal_circles[key] for key in internal_circles if key not in external_circles}

    # Pack it!
    circles = CirclePack(internal=internal_circles, external=external_circles)

    # we need to conjugate, for knotoids the diagram is in CW order
    return {key: Circle(value[0].conjugate(), value[1]) for key, value in circles.items()}  # return Circle objects


def _point_on_circle(center: complex, alpha: float, radius: float = 1.0) -> complex:
    """
    Returns a complex point on a circle at a given angle, centered at a specified  point, with an optional radius.

    Args:
        center (complex): Center of the circle.
        alpha (float): Angle in radians where the point is located on the circle.
        radius (float, optional): Radius of the circle. Defaults to 1.0.

    Returns:
        complex: The computed point on the circle.
    """
    return center + radius * complex(math.cos(alpha), math.sin(alpha))


def _layout_arcs(k: PlanarDiagram | OrientedPlanarDiagram, circles: dict, layout: dict):
    """
    By an arc we mean the path through the arc circle and starts and ends on the intersection of the arc
    circle and the adjacent tangent node circles.
    TODO: if endpoints are different color, split arcs in half using the bisect() method
    TODO: do not layout arcs, just the two endpoints.
    """
    for arc in k.arcs:
        ep1, ep2 = arc
        if not _visible(ep1) or not _visible(ep2):
            continue
        # Compute the arc that is perpendicular to the arc circle.
        g_arc = perpendicular_arc(circles[arc], circles[ep1.node], circles[ep2.node])
        layout[arc] = g_arc




def _layout_endpoints(k: PlanarDiagram | OrientedPlanarDiagram, circles: dict, layout: dict):
    """
    Layout parts of the arcs near the nodes (endpoints). This function generates the circular arcs or segments that
    will represent the endpoints of the arcs for plotting.

    Args:
        k (PlanarDiagram | OrientedPlanarDiagram): The planar or oriented planar diagram
            containing nodes, arcs, and endpoints for layout computation.
        circles (dict): A dictionary containing the geometric information of the nodes and arcs
            (e.g., centers of circles used to define arcs and vertices).
        layout (dict): A dictionary that will be populated with the calculated layout information
            for each node, arc, and endpoint in the diagram.
    """

    for v in k.nodes:
        node_inst = k.nodes[v]
        arcs = k.arcs[v]
        endpoints = k.endpoints[v]


        if isinstance(node_inst, Crossing):
            """Connect crossing endpoints. Plot two circular arcs from the crossing to the endpoint. The over-arc is a single
            circular arc, the under-arc splits into two sub-arcs, the gap represents the arc break emphasizing that the 
            under-arc travels below the over-arc."""

            # get circular arcs
            under_arc = perpendicular_arc(circles[v], circles[arcs[0]], circles[arcs[2]])
            over_arc = perpendicular_arc(circles[v], circles[arcs[1]], circles[arcs[3]])
            point = over_arc * under_arc
            point = point if isinstance(point, complex) else sum(point)/len(point)  # in case there are two intersections, maybe only point[0]?

            layout[endpoints[0]], layout[endpoints[2]] = _sort_geometric_arcs(*split(under_arc, point), circles[arcs[0]], circles[arcs[2]])
            layout[endpoints[1]], layout[endpoints[3]] = _sort_geometric_arcs(*split(over_arc, point), circles[arcs[1]], circles[arcs[3]])

            # modified point
            layout[v] = point


        else:
            """" We have a vertex. First determine if we want to connect two endpoint-arcs by a smooth arc 
            and the others by straight lines, or, do we connect all endpoint-arcs by straight lines. In case at least 
            one arc is smooth, then we need to change the position of the vertex."""

            # get the two arcs that share some properties, so we connect it by an arc
            colors = defaultdict(list)
            [colors[ep.attr.get("color", None)].append(ep) for ep in endpoints]
            same_pair = [val for key, val in colors.items() if key is not None and len(val) == 2] + (colors[None] if len(colors[None]) == 2 else []) + [endpoints if len(endpoints) == 2 else []]
            same_pair = same_pair[0] if same_pair else []

            point = circles[v].center

            if same_pair:
                # connect this pair by an arc
                ep1, ep2 = same_pair[0]
                index1, index2 = endpoints.index(ep1), endpoints.index(ep2)
                arc1, arc2 = arcs[index1], arcs[index2]

                same_arc = perpendicular_arc(circles[v], circles[arc1], circles[arc2])
                point = middle(same_arc)  # move the vertex

                # get arcs
                layout[ep1], layout[ep2] = _sort_geometric_arcs(*bisect(same_arc), circles[arc1], circles[arc2])


            for ep, arc in zip(endpoints, arcs):
                if ep in same_pair:
                    continue

                boundary_b_point = circles[arc] * circles[v]  # intersection point on the circle boundary

                garc = perpendicular_arc_through_point(circles[v], boundary_b_point[0], point)
                layout[ep] = garc



            layout[v] = point  # possible new coordinate


        # set direction so the endpoint arcs point away from the node (crossing/vertex)
        for ep in endpoints:
            layout[ep] = orient_arc(layout[ep], start_point=layout[v])





def _preprocess_knot(k: PlanarDiagram | OrientedPlanarDiagram):
    """
    Processes a given planar diagram or oriented planar diagram by identifying and removing kinks
    present in the diagram, while preserving the structure and connectivity.

    Args:
        k (PlanarDiagram | OrientedPlanarDiagram): The planar diagram or oriented planar diagram
            to be processed.

    Returns:
        PlanarDiagram | OrientedPlanarDiagram: A modified copy of the input diagram, with all kinks
        removed.
    """
    k = k.copy()

    # remove the kinks

    removed_kinks = []
    while _kinks := kinks(k):
        ep = next(iter(_kinks))
        c_inst = k.nodes[ep.node]
        removed_kinks.append((ep, c_inst))
        #v = Vertex(degree=2, _kink=True)
        del k._nodes[ep.node]
        # TODO: if we need a bigger space for kinks, we can insert additional bivertices
        ep1 = c_inst[(ep.position + 1) % 4]
        ep2 = c_inst[(ep.position + 2) % 4]
        k.set_arc((ep1, ep2), _kink=ep.node)

    # split connected sums
    # TODO

    # # remove leafs (knotoids)
    # while _leafs := [v for v in k.vertices if k.degree(v) == 1]:
    #     leaf = _leafs[0]
    #     leaf_ep = leaf[0]
    #     adj_ep = k.twin(leaf_ep)





    return k

def _mean(list_of_points):
    """Return the mean of a list of complex numbers"""
    # TODO: use stats.mean
    return sum(list_of_points)/len(list_of_points)


def _debug(*args):
    print(*args)


def _shorter_arc(arc: CircularArc):
    _arc = - arc
    return _arc if _arc.length() < arc.length() else arc

def _insert_kink(k: PlanarDiagram | OrientedPlanarDiagram,
                 preprocessed_k: PlanarDiagram | OrientedPlanarDiagram,
                 layout: dict,
                 circles: dict,
                 crossing,
                 _circle: Circle,
                 _ep_adj_arc: dict
                 ):
    """

    Args:
        k:
        preprocessed_k:
        layout:
        circles:
        _circle:
        ep_arc: keys are endpoints from the kink crossings, values are the corresponding adjacent arcs in the preprocessed diagram

    Returns:

    """
    print(f"*Adding kink {crossing} to endpoints {_ep_adj_arc.keys()}")

    c_inst = k.nodes[crossing]  # crossing instance

    ep = [ep for ep in c_inst if ep.node == crossing and c_inst[(ep.position - 1 % 4)].node == crossing][0] # the inner endpoint defining the kink face
    twin_ep = k.twin(ep)  # other endpoint in kink loop
    adj_ep_a, adj_ep_b = c_inst[(ep.position + 1) % 4], c_inst[(ep.position + 2) % 4]  # the tail endpoints of the kink
    ep_a, ep_b = k.twin(adj_ep_a), k.twin(adj_ep_b)  # endpoints of the kink crossing

    # the endpoint now follow the ccw order: ep, ep_a, ep_b, twin_ep, all with node property 'crossing'.
    print(f"ep {ep} twin {twin_ep} {ep_a} {ep_b}", "adjacent", adj_ep_a, adj_ep_b)
    ab_arc = perpendicular_arc(_circle, circles[adj_ep_a.node], circles[adj_ep_b.node])  # the full arc through the circle on which the kink should lie on
    ab_arc = orient_arc(ab_arc, start_point=circles[adj_ep_a.node].center)  # orient from a to b
    perpendicular = 1j * (ab_arc.B - ab_arc.A) / abs(ab_arc.B - ab_arc.A)
    rad_vec =  middle(ab_arc) - ab_arc.center  # vector from center to the ab arc
    if (rad_vec / perpendicular).real > 0:
        factor = 0.4
    else:
        factor = 0.25

    # TODO: choose this point so it make sense for small/large inner/external kinks
    # resize the parpendicular vector so the crossing is nice
    perpendicular *= _circle.radius * factor  # perpendicular vector in the direction of the kink crossing, 1/2 size of the arc circle

    crossing_position = middle(ab_arc) + perpendicular


    # TODO: shorten the arc if its too long

    arc_a = perpendicular_arc_through_point(_circle, ab_arc.A, crossing_position)
    arc_b = perpendicular_arc_through_point(_circle, ab_arc.B, crossing_position)
    arc_a = orient_arc(arc_a, start_point=crossing_position)
    arc_b = orient_arc(arc_b, start_point=crossing_position)

    # enlenghten the arcs so that they can be closed by a semi-circle

    circle_a = Circle(arc_a.center, arc_a.radius)
    circle_b = Circle(arc_b.center, arc_b.radius)
    ab = Line(arc_a.center, arc_b.center)
    intersection_a = sorted(circle_a * ab, key=lambda _: abs(crossing_position - _))[0]  # choose the crossing that is closer to the crossing
    intersection_b = sorted(circle_b * ab, key=lambda _: abs(crossing_position - _))[0]

    # create the arcs from ep and twin ep
    arc_ep = _shorter_arc(arc_from_circle_and_points(circle_b, arc_b.A, intersection_b))
    arc_twin_ep = _shorter_arc(arc_from_circle_and_points(circle_a, arc_a.A, intersection_a))
    arc_ep = orient_arc(arc_ep, start_point=crossing_position)
    arc_twin_ep = orient_arc(arc_twin_ep, start_point=crossing_position)

    # shorten the arcs if they are too long.
    # TODO: 0.75 should be a global parameter
    if (diff := (arc_ep.length() - arc_a.length()*0.75)) > 0:
        arc_ep = arc_ep.shorten(diff, side="B")
        arc_twin_ep = arc_twin_ep.shorten(diff, side="B")

    # cap them by a semi-circle or a circlular arc
    center = Segment(arc_ep.center, arc_ep.B) * Segment(arc_twin_ep.center, arc_twin_ep.B)  # center of the cap
    arc_arc = - arc_from_circle_and_points(Circle(center=center , radius=abs(arc_ep.B - center)), arc_ep.B, arc_twin_ep.B)


    layout[ep_a] = arc_a
    layout[ep_b] = arc_b
    layout[ep] = arc_ep
    layout[twin_ep] = arc_twin_ep

    layout[k.arcs[ep]] = arc_arc


def _post_process_layout(k: PlanarDiagram | OrientedPlanarDiagram, preprocessed_k : PlanarDiagram | OrientedPlanarDiagram, layout:dict, circles:dict):
    """
    Post-processes the layout of a knot diagram by restoring removed kinks and adjusting arcs according to circle packing.

    Args:
        k: The original diagram containing the information about knots or links used for restoring kinks and arcs.
        ppk: The processed planar diagram where some elements may have been omitted during layout generation.
        layout: A dictionary where keys are diagram arcs or endpoints and values are the corresponding geometric segments or positions.
        circles: A dictionary containing the mapping between arcs in the diagram and their corresponding circle packing representations.
    """
    print("Post processing layout")


    """
    Add kinks that were removed in the layout due to the circle packing.
    Elements form the preprocessed diagram start with '_',
    elements from the original/post-processed diagram do not start with '_'.
    """
    # loop over the arcs of the preprocessed knot
    for _arc in preprocessed_k.arcs:
        _ep_a, _ep_b = _arc
        # Find an arc that was removed in the preprocessing. The arc '_arc' should contain a kink, so we must add it.
        if "_kink" in _ep_a.attr:
            crossing = _ep_a.attr["_kink"]  # the endpoint defining the kink and the node instance was saved as an attribute
            _arc_a = layout[_ep_a]
            _arc_b = layout[_ep_b]

            _insert_kink(k=k, preprocessed_k=preprocessed_k, layout=layout, circles=circles,
                         crossing=crossing, _circle=circles[_arc], _ep_adj_arc={_ep_a: _arc_a, _ep_b: _arc_b})


            continue

            c_inst = k.nodes[crossing]  # the removed crossing instance


            _circle = circles[_arc]  # the arc circle that was placed instead of the crossing
            #_garc = layout[_arc]  # the arc that was placed instead of a crossing

            # get the first index of the non-looped endpoints of the crossing, and get all other ccw endpoints
            index_0 = [i for i in range(4) if c_inst[i].node != crossing and c_inst[(i + 1) % 4].node != crossing][0]
            index_1, index_2, index_3 = (index_0 + 1) % 4, (index_0 + 2) % 4, (index_0 + 3) % 4  # index_1 is the next non-kink endpoint, 2 and 4 are kinks
            ep0, ep1, ep2, ep3 = c_inst[index_0], c_inst[index_1], c_inst[index_2], c_inst[index_3]   # get the endpoints of the original knot
            arc0, arc1, arc2, arc3 = k.arcs[ep0], k.arcs[ep1], k.arcs[ep2], k.arcs[ep3]  # get the arcs involved in the kink
            assert arc2 == arc3
            _ep_a_garc, _ep_b_garc = layout[_ep_a], layout[_ep_b]  # the arcs of the pre-processed endpoints

            return

            # We which side does the kink lie on?
            _a_face = [face for face in ppk.faces if _ep_a in face][0]
            _b_face = [face for face in ppk.faces if _ep_b in face][0]
            _a_face_circle = circles[_a_face] if _a_face in circles else None
            _b_face_circle = circles[_b_face] if _b_face in circles else None
            # at least one circle should not be outer/external
            if _a_face_circle is None and _b_face_circle is None:
                raise ValueError("Circle packing layout failed: cannot find a kink circle face")
            if _a_face_circle is not None:
                print(_ep_a == ep1, "(1)")
                print(_a_face_circle * _gcircle, _a_face_circle, _gcircle)
                _kink_point = _a_face_circle * _gcircle if _ep_a == ep1 else antipode(_gcircle, _a_face_circle * _gcircle)  # a point on _gcircle in the kink direction
            else:
                print(_ep_b == ep1, "(2)")
                print(_b_face_circle * _gcircle, _a_face_circle, _gcircle)
                _kink_point = _b_face_circle * _gcircle if _ep_b == ep1 else antipode(_gcircle, _b_face_circle * _gcircle)  # a point on _gcircle in the kink direction


            if not isinstance(_kink_point, list):
                raise RuntimeError("Circle packing layout failed: kink point is expected to be a list", _kink_point)

            if len(_kink_point) != 1:
                raise RuntimeError("Circle packing layout failed: kink point is expected contain a single intersection", _kink_point)

            return

            _kink_point = _kink_point[0]

            # the three points defining the kink position are p0, _kink_point, p1, all on _gcircle
            # Define points p0 and p1 on the arc-circle of the missing kink (where non-loops strands will start)
            if min(abs(_ep_a_garc.A - _garc.A), abs(_ep_a_garc.B - _garc.A)) < min(abs(_ep_b_garc.A - _garc.A), abs(_ep_b_garc.B - _garc.A)):
                p0, p1 = _garc.A, _garc.B  # points outside of kink
                print("garc", _garc, "kink pt", _kink_point)
                if _kink_point in _garc:
                    q0 = _garc[(_garc.B + 2 * _garc.A) / 3]
                    q1 = _garc[(2 * _garc.B + _garc.A) / 3]
                else:
                    q0 = _garc[(_garc.B + 2 * _garc.A) / 3]
                    q1 = _garc[(2 * _garc.B + _garc.A) / 3]


            else:
                p1, p0 = _garc.A, _garc.B

            #print("ARC", arc_circle, garc, "p0", p0, "p1", p1, p0 in garc, p1 in garc)
            p2 = antipode(_gcircle, p0)
            p3 = antipode(_gcircle, p1)
            #print("ARC", arc_circle, garc, "p0", p0, "p1", p1, p0 in garc, p1 in garc)

            # p0 is now the point on the crossing/arc circle at index 0, and p1 is the one at index 1
            layout[k.twin(c_inst[index_0])] = Segment(p0, _gcircle.center)
            layout[k.twin(c_inst[index_1])] = Segment(p1, _gcircle.center)
            layout[k.twin(c_inst[index_2])] = Segment(p2, _gcircle.center)
            layout[k.twin(c_inst[index_3])] = Segment(p3, _gcircle.center)

            # add the main kink arc
            kink_garc = - perpendicular_arc_through_point(_gcircle, p2, p3)
            layout[frozenset({k.twin(c_inst[index_3]), k.twin(c_inst[index_2])})] = kink_garc


def layout_circle_packing(k: PlanarDiagram | OrientedPlanarDiagram, return_circles: bool = False):
    """
    Computes the layout using circle packing for a given planar or oriented planar diagram. A layout is a dictionary,
    where keys are diagram elements (nodes, arcs, endpoints, faces) and values are the corresponding geometric objects
    (e.g., points, segments, circle arcs) which, upon plotting, will represent the diagram.

    Args:
        k (PlanarDiagram | OrientedPlanarDiagram): The input planar or oriented planar diagram representing the knot or link for which the layout is calculated.
        return_circles (bool): If True, the function also returns the computed circles for the circle packing. Defaults to False.

    Returns:
        dict or tuple: If `return_circles` is False, the function returns a dictionary
        mapping nodes, endpoints, arcs, and faces to their corresponding layout positions.
        If `return_circles` is True, it returns a tuple containing the layout dictionary
        and the computed circles.
    """

    print(k)
    k_ = _preprocess_knot(k)
    print(k_)

    circles = circle_packing(k_)
    circles = canonically_rotate_circles(circles)

    print("Circles packed")
    layout = {node: None for node in k.nodes}
    layout |= {ep: None for ep in k.endpoints}
    layout |= {arc: None for arc in k.arcs}
    layout |= {face: None for face in k.faces}


    _layout_arcs(k_, circles, layout)
    _layout_endpoints(k_, circles, layout)

    _post_process_layout(k, k_, layout, circles)

    return (layout, circles) if return_circles else layout




if __name__ == "__main__":
    import knotpy as kp
    k = kp.knot("4_1")
    l = layout_circle_packing(k)
