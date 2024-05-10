"""Generators for some simple planar diagrams."""

#__all__ = [""]




__all__ = ['parallel_edge']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'



def parallel_edge(multiplicity):
    """Returns a graph with two vertices and multiplicity edges between the two nodes."""
    # TODO: Implement this
    raise NotImplementedError()
    # pg = PlanarGraph()
    # pg._add_node(0, multiplicity)
    # pg._add_node(1, multiplicity)
    # if multiplicity > 0:
    #     for i in range(multiplicity):
    #         pg._set_arc(((0, i), (1, multiplicity - i - 1)))
    #     return pg
    pass

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