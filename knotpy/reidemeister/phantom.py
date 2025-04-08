# """Dealing with phantom objects, e.g.:
# - phantom bivalent vertices that are used to simplify modifications
# - phantom arcs that are used for plotting algorithm to work
#
# TODO: remove this, since it is not needed anymore, plotting still needs it - fix!!
# """
#
# __all__ = ["insert_phantom_node", "is_node_phantom", "insert_phantom_nodes_on_internal_arcs"]
# __version__ = '0.1'
# __author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'
#
# import random
# import string
#
# from knotpy.classes.node import Crossing
# from knotpy.classes.endpoint import Endpoint, IngoingEndpoint
# from knotpy.classes.planardiagram import PlanarDiagram
# from knotpy.classes.node.vertex import Vertex
#
#
# def _random_string(N):
#     return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
#
#
# # def is_node_phantom(k: PlanarDiagram, node):
# #     return "_phantom" in k.nodes[node].attr and k.nodes[node].attr["_phantom"]
#
#
# def insert_phantom_node(k: PlanarDiagram, arc, node_name=None):
#     """Put a "phantom" bivalent vertex on the arc."""
#     if node_name is None:
#         node_name = "_phantom_" + _random_string(8)  # random node name, e.g. "_phantom_jWSu
#     ep1, ep2 = arc
#     k.add_node(node_for_adding=node_name, create_using=Vertex, degree=2, _phantom=True)
#     k.set_endpoint(endpoint_for_setting=(node_name, 0), adjacent_endpoint=ep1, create_using=ep1, **ep1.attr)
#     k.set_endpoint(endpoint_for_setting=ep1, adjacent_endpoint=(node_name, 0), create_using=ep2, _phantom=True)
#     k.set_endpoint(endpoint_for_setting=(node_name, 1), adjacent_endpoint=ep2, create_using=ep2, **ep2.attr)
#     k.set_endpoint(endpoint_for_setting=ep2, adjacent_endpoint=(node_name, 1), create_using=ep1, _phantom=True)
#     return node_name
#
#
# def insert_phantom_nodes_on_internal_arcs(k: PlanarDiagram, nodes, exclude_arcs=None):
#     """ insert phantom bivalent vertices on edges that connect two nodes from the nodes set. Except the excluded arcs.
#     :param k:
#     :param nodes:
#     :param exclude_arcs:
#     :return: list of newly created phantom nodes
#     """
#
#     # get all arcs from nodes
#     arcs = set()
#     for node in nodes:
#         arcs = arcs.union(k.arcs[node])
#     arcs = arcs.difference(exclude_arcs)
#
#     phantom_nodes = []  # keep track of phantom nodes
#     for arc in arcs:
#         ep1, ep2 = arc
#         if ep1.node in nodes and ep2.node in nodes:
#             phantom_nodes.append(insert_phantom_node(k, arc))
#
#     return phantom_nodes
