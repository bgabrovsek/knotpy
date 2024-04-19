from knotpy.classes.knot import Knot, OrientedKnot
from knotpy.classes.spatialgraph import SpatialGraph

from knotpy.classes.planardiagram import PlanarDiagram


__all__ = ['planar_diagram_from_data', "orientations"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@gmail.si>'

#
# def planar_diagram_from_data(incoming_data, create_using) -> PlanarDiagram:
#     """ Generate a planar diagram, from (incoming) data.
#     :param incoming_data: notation or other PlanarDiagram instance
#     :param create_using: type or instance
#     :return: planar diagram with data
#     """
#
#     # initiate the diagram with create_using
#     if type(create_using) is type:
#         k = create_using()
#     elif isinstance(create_using, PlanarDiagram):
#         k = create_using
#     else:
#         raise TypeError("create_using is not a valid KnotPy planar diagram type or instance")
#
#     k.clear()
#
#     if isinstance(incoming_data, PlanarDiagram):
#         # copy data from incoming_data instance
#
#         k.attr.update(incoming_data.attr)
#
#         # copy nodes
#         for node in incoming_data.nodes:
#             node_instance = incoming_data.nodes[node]
#             k.add_node(node_for_adding=node, create_using=type(node_instance),
#                        degree=len(node_instance), **node_instance.attr)
#
#         # copy endpoints
#         for ep in incoming_data.endpoints:
#             adj_ep = incoming_data.twin(ep)
#             k.set_endpoint(endpoint_for_setting=ep, adjacent_endpoint=(adj_ep.node, adj_ep.position),
#                            create_using=type(adj_ep), **adj_ep.attr)
#
#     elif incoming_data is None:
#         # create empty diagram
#         pass
#
#     else:
#         raise NotImplementedError("constructing planar diagrams from non-planar diagrams not implemented")
#
#     return k


def orientations(k: PlanarDiagram) -> tuple:
    """Return all possible orientations of planar diagram k.

    :param k: input planar diagram
    :return: oriented tuples
    """

    # if isinstance(k, )

    pass


