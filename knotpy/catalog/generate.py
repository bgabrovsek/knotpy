"""
The
mirror image of a plane graph is obtained by reversing the cyclic order at each vertex;
this corresponds to reflecting the plane about a line.


A separating cycle in a plane graph is a cycle that contains at least one vertex in its
interior and at least one vertex in its exterior.

The length of the smallest separating cycle
in a triangulation is the same as the (vertex) connectivity, and is known to equal the
cyclic connectivity of the cubic dual graph

An orientationpreserving isomorphism (OP-isomorphism)
orientation-reversing isomorphism (OR-isomorphism)
the automorphism group Aut(G) of a plane graph is the group of all isomorphisms
from G to itself, and the OP-automorphism group

"""

import string

#from knotpy import export_pdf, sanity_check, from_knotpy_notation, insert_loop, number_of_link_components
from knotpy.algorithms.degree_sequence import degree_sequence
from knotpy.utils.set_utils import LeveledSet
from knotpy.algorithms.canonical import canonical
from knotpy.catalog.graphs import path_graph, cycle_graph
from knotpy.manipulation.insert import insert_arc, insert_new_leaf
from knotpy.classes.freezing import freeze
from knotpy.manipulation.insert import parallelize_arc
from knotpy.classes.convert import vertices_to_crossings
from knotpy.algorithms.topology import loops as get_loops
from knotpy.algorithms.sanity import sanity_check
from knotpy.drawing.draw_matplotlib import export_pdf
from knotpy.notation.native import from_knotpy_notation
from knotpy.manipulation.insert import insert_loop
from knotpy.algorithms.topology import number_of_link_components

vertex_names = string.ascii_letters

def non_adjacent_combinations(elements: tuple):
    n = len(elements)
    for i in range(n):
        for j in range(i + 2, i + n - 1):  # ensure at least 2 apart, cyclically
            a = elements[i]
            b = elements[j % n]
            if a.node != b.node:
                yield a, b


def generate_simple_graphs(n: int, degrees: int | list, parallel_edges=True, loops=True):
    """Generate connected graph with up to n vertices with degrees degrees.
    """

    d = set(degrees) if isinstance(degrees, list) else {degrees}

    P1 = path_graph(1)
    P2 = path_graph(2)
    C1 = cycle_graph(1)

    del P1.attr["name"]
    del P2.attr["name"]
    del C1.attr["name"]

    ls = LeveledSet(canonical(P1))
    ls.new_level(canonical(P2))
    if loops:
        ls.add(C1)

    max_degree = max(degrees)

    # add an additional edge
    while ls[-1]:

        ls.new_level()

        for graph in ls[-2]:
            l = len(graph)

            # Add a new vertex to the graph.
            if l < n:
                for face in graph.faces:
                    for ep in face:

                        # do not increase degree
                        if graph.degree(ep.node) >= max_degree:
                            continue

                        g = graph.copy()

                        v = vertex_names[l + 1]
                        #print()
                        #print(g, "vertex", v, "arc", (ep, (v, 0)))
                        g.add_vertex(vertex_for_adding=v)
                        insert_arc(g, (ep, (v, 0)))

                        #print(g)
                        assert sanity_check(g)
                        ls.add(freeze(canonical(g)))

            # Add a new arc to the graph
            for face in graph.faces:
                for arc in non_adjacent_combinations(face):

                    # do not increase degree
                    if any(graph.degree(ep.node) >= max_degree for ep in arc):
                        continue

                    g = graph.copy()
                    insert_arc(g, arc)
                    assert sanity_check(g)
                    ls.add(freeze(canonical(g)))

            # Add parallel arcs
            if parallel_edges:
                for arc in graph.arcs:

                    ep1, ep2 = arc
                    if graph.degree(ep1.node) >= max_degree or graph.degree(ep2.node) >= max_degree:
                        continue
                    if ep1.node == ep2.node:
                        continue
                    # do not increase degree

                    g = graph.copy()
                    parallelize_arc(g, arc)
                    assert sanity_check(g)
                    ls.add(freeze(canonical(g)))


            # Add loops
            if loops:
                for ep in graph.endpoints:

                    if graph.degree(ep.node) + 2 > max_degree:
                        continue

                    g = graph.copy()
                    insert_loop(g, ep)
                    assert sanity_check(g)
                    ls.add(freeze(canonical(g)))

    graphs = set(ls)
    graphs = [g for g in graphs if all(d in degrees for d in degree_sequence(g))]
    graphs = sorted(graphs, key=lambda g: (len(g.vertices), len(g.endpoints), -len(get_loops(g))))


    return graphs


def generate_knot_diagrams(n: int, kinks=False):

    graphs = generate_simple_graphs(n, degrees=[4], parallel_edges=True, loops=kinks)

    knots = []

    for g in graphs:

        g_links = vertices_to_crossings(g, all_crossing_signs=True)
        if number_of_link_components(g_links[0]) > 1:
            continue

        g_links = {canonical(k) for k in g_links}

        knots.extend(g_links)

    return knots



if __name__ == "__main__":


    #graphs = generate_simple_graphs(4, degrees=[4])

    knots = generate_knot_diagrams(4, kinks=True)

    export_pdf(knots, "knots.pdf", with_title=True)