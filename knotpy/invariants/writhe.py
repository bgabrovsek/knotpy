__all__ = ['writhe']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.orientation import all_orientations
from knotpy.algorithms.topology import edges as get_edges
from knotpy.algorithms.orientation import all_orientations, orient
from knotpy.utils.set_utils import powerset
#
# def crossing_signs_dict(k: PlanarDiagram | OrientedPlanarDiagram) -> dict:
#     """ If the knot or link is oriented, compute all crossing signs directly from the crossings.
#     If the k is an unoriented knot, compute the crossing signs from the diagram. In case k is an unoriented link,
#     compute the crossing signs in a way that the writhe is minimized. In case there are several possible link
#     orientations with the same writhe, the crossing signs are determined non-uniquely.
#     Args:
#         k:
#     Returns:
#     """
#
#     if k.is_oriented():
#         return {c: k.sign(c) for c in k.crossings}
#
#     # we have an unoriented knot or link
#     edges = sorted(get_edges(k))
#     edge_direction = {c: [None, None] for c in k.crossings}  # Position 0 is Ingoing, position 1 is Ingoing
#     #print(edges)
#     for edge in edges:
#         for i in range(n := len(edge)):
#             if edge[i].node == edge[(i + 1) % n].node and edge[i].position % 2 == edge[(i + 1) % n].position % 2:  # i is at the beginning of a crossing (i+1) is the other end
#                 edge_direction[edge[i].node][edge[i].position % 2] = edge[i].position % 2 == edge[i].position
#
#     #print("dir", edge_direction)
#
#     signs = {c: -1 if edge_direction[c][0] == edge_direction[c][1] else 1 for c in k.crossings}
#     #print(signs)
#
#     # minimize the signs for links
#     if len(edges) > 1:
#         crossings_edge = {c: set() for c in k.crossings}  # values are edges that contain the crossing
#         for index, edge in enumerate(edges):
#             for ep in edge:
#                 if ep.node in crossings_edge:
#                     crossings_edge[ep.node].add(index)
#
#             all_signs = []
#             for reversed_edges in powerset(range(len(edges))):
#                 all_signs.append(
#                     {
#                         c: signs[c] * (-1) ** len(set(reversed_edges) & set(crossings_edge[c]))
#                         for c in signs
#                     }
#                 )
#             #print(sorted(all_signs, key=lambda s: sum(s.values())))
#             return sorted(all_signs, key=lambda s: sum(s.values()))[0]
#
#     return signs
#
# def crossing_sign(k: PlanarDiagram | OrientedPlanarDiagram, crossing):
#     """
#     If the knot is oriented, compute the crossing sign
#     Args:
#         k:
#
#     Returns:
#
#     """
#     if k.is_oriented():
#         return k.sign(crossing)
#     signs = crossing_signs_dict(k)
#     if crossing not in signs:
#         raise ValueError(f"Cannot compute crossing sign for {crossing}")
#     return signs[crossing]


def writhe(k: PlanarDiagram | OrientedPlanarDiagram) -> int:
    """The writhe is the total number of positive crossings minus the total number of negative crossings.
    :param k:
    :return:
    """
    print(k)
    if type(k) is OrientedPlanarDiagram:
        return sum(k.nodes[c].sign() for c in k.crossings)
    else:
        return min(sum(o.nodes[c].sign() for c in o.crossings) for o in all_orientations(k))  # TODO: make this faster

# def knot_crossing_signs(k: PlanarDiagram):
#     """ works only for knots"""
#     if not k.is_oriented():
#         k = orient(k)
#
#     return {c:k.sign(c) for c in k.crossings}
#
# def writhe(k: PlanarDiagram) -> int:
#
#     # TODO: orient if one component, otherwise raise error
#     if not k.is_oriented():
#         if number_of_disjoint_components(k) != 1:
#             raise ValueError(f"Cannot determine the writhe of a unoriented link with {number_of_disjoint_components(k)} disjoint components")
#         else:
#             k = orient(k)
#
#
#     return sum(k.nodes[node].sign() for node in k.crossings)
#
#
# def forced_writhe(k: PlanarDiagram) -> int:
#     """
#     TODO: optimize for knots, etc.
#     :param k:
#     :return:
#     """
#     if k.is_oriented():
#         return writhe(k)
#     else:
#         try:
#             return writhe(k)
#         except ValueError:
#             return min(writhe(ok) for ok in all_orientations(k))

# if __name__ == "__main__":
#     import knotpy as kp
#
#     k = kp.link("l5a1")
#     print(writhe(k))