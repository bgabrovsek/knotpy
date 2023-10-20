"""Generators for some simple planar diagrams."""

#__all__ = [""]


from knotpy.classes.knot import Knot
from knotpy.classes.planardiagram import PlanarDiagram

__all__ = ['empty_knot']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


def empty_knot(create_using=None):
    """Return the empty graph/knot with zero nodes and zero arcs.
    :param create_using: planar diagram instance, Constructor or None.
    :return: empty graph
    """

    if create_using is None:
        g = Knot()
    elif isinstance(create_using, type):
        g = create_using()
    elif isinstance(create_using, PlanarDiagram):
        g = type(create_using)()
    else:
        raise TypeError("create_using is not a valid KnotPy type or instance")
    return g
#
#
# def trivial_theta_curve():
#     pg = PlanarGraph()
#     pg._add_node(0, (0, 2, 1))
#     pg._add_node(1, (0, 1, 2))
#     return pg
#
#
# def parallel_edge(multiplicity):
#     """Returns a graph with two vertices and multiplicity edges between the two nodes."""
#     pg = PlanarGraph()
#     pg._add_node(0, multiplicity)
#     pg._add_node(1, multiplicity)
#     if multiplicity > 0:
#         for i in range(multiplicity):
#             pg._set_arc(((0, i), (1, multiplicity - i - 1)))
#         return pg
#
# def house_graph():
#     """
#     4--3-\
#     |  |  2
#     0--1-/
#     """
#
#     g = PlanarGraph()
#     g._add_node(0, degree=2)
#     g._add_node(1, degree=3)
#     g._add_node(2, degree=2)
#     g._add_node(3, degree=3)
#     g._add_node(4, degree=2)
#     g._set_arc(((0, 0), (1, 0)))
#     g._set_arc(((1, 1), (2, 0)))
#     g._set_arc(((2, 1), (3, 1)))
#     g._set_arc(((3, 2), (4, 0)))
#     g._set_arc(((4, 1), (0, 1)))
#     g._set_arc(((1, 2), (3, 0)))
#
#
#     return g
#
#
#
# def vertex_graph():
#     pg = PlanarGraph()
#     pg._add_node(0, degree=0)
#     return pg
#
# if __name__ == '__main__':
#     print(empty_graph())
#     print(vertex_graph())
#     #print(to_em_notation(empty_graph()))
#     #print(to_em_notation(vertex_graph()))


"""
for m in range(4, 6):
    g = parallel_edge(m)
    print(g)
    em = to_em_notation(g)
    print(from_notation(em))
    data = to_pd_notation(g)
    print(from_notation(data))
"""