"""
Definitions and helpers for generating plane graphs and knot diagrams.

The mirror image of a plane graph is obtained by reversing the cyclic order at
each vertex; this corresponds to reflecting the plane about a line.

A separating cycle in a plane graph is a cycle that contains at least one
vertex in its interior and at least one vertex in its exterior.

The length of the smallest separating cycle in a triangulation is the same as
the (vertex) connectivity, and equals the cyclic connectivity of the cubic
dual graph.

An orientation-preserving isomorphism (OP-isomorphism) and an
orientation-reversing isomorphism (OR-isomorphism) are standard notions for
plane graphs. The automorphism group Aut(G) of a plane graph is the group of
all isomorphisms from G to itself; the OP-automorphism group consists of the
orientation-preserving automorphisms.
"""

from __future__ import annotations

import string
from typing import Iterable, Iterator, List, Sequence, Tuple

from knotpy import PlanarDiagram, OrientedPlanarDiagram
# from knotpy import export_pdf, sanity_check, from_knotpy_notation, insert_loop, number_of_link_components
from knotpy.algorithms.degree_sequence import degree_sequence
from knotpy.utils.set_utils import LeveledSet
from knotpy.algorithms.canonical import canonical
from knotpy.tables.graphs import path_graph, cycle_graph
from knotpy.algorithms.insert import insert_arc
from knotpy.classes.freezing import freeze
from knotpy.algorithms.insert import parallelize_arc
from knotpy.algorithms.topology import loops as get_loops
from knotpy.algorithms.sanity import sanity_check

from knotpy.algorithms.insert import insert_loop
from knotpy.algorithms.topology import number_of_link_components
from knotpy.algorithms.naming import unique_new_node_name
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint

from knotpy.classes.planardiagram import PlanarDiagram  # kept duplicate import to preserve environment assumptions
from knotpy.classes.node.crossing import Crossing
from knotpy.utils.set_utils import powerset
from knotpy.algorithms.symmetry import mirror


vertex_names = string.ascii_letters


def vertices_to_crossings(
    g: PlanarDiagram,
    vertices: Sequence | None = None,
    all_crossing_signs: bool = False,
):
    """
    Convert selected 4-valent vertices of a plane graph to crossings.

    Args:
        g: The input planar diagram (treated as an undirected plane graph).
        vertices: Vertices to convert. If ``None``, all degree-4 vertices are converted.
        all_crossing_signs: If ``False``, convert using the default (CCW) crossing
            convention. If ``True``, return all combinations of crossing sign flips
            (via mirroring those converted vertices).

    Returns:
        If ``all_crossing_signs`` is ``False``, a single converted diagram.
        Otherwise, a list of converted diagrams, covering all sign combinations.

    Raises:
        ValueError: If any requested vertex is not 4-valent, or does not exist.
    """
    if vertices is None:
        vertices = [v for v in g.vertices if g.degree(v) == 4]

    if not all(g.degree(v) == 4 for v in vertices):
        raise ValueError("Cannot convert a vertex to a crossing if it is not of degree 4")

    # Accept a variety of container types; if a single item, wrap into a list.
    if not isinstance(vertices, (list, tuple, dict, set)):
        vertices = [vertices]

    for v in g.vertices:
        if v not in g.vertices:
            raise ValueError(f"Cannot convert vertex {vertices} to a crossing")

    if not all_crossing_signs:
        # Single conversion using the default crossing orientation.
        g_copy = g.copy()
        g_copy.convert_nodes(list(vertices), Crossing)
        return g_copy
    else:
        # Convert to default crossings, then enumerate all sign-change combinations by mirroring.
        g_copies = []
        g_copy = g.copy()
        g_copy.convert_nodes(vertices, Crossing)

        g_copies.extend(
            mirror(g_copy, crossings=crossings_to_change_sign, inplace=False)
            for crossings_to_change_sign in powerset(vertices)
        )
        return g_copies


def unknot(oriented: bool = False):
    """
    Construct the trivial knot diagram (unknot) as a single 2-valent vertex with a loop.

    Args:
        oriented: If ``True``, create an oriented planar diagram (with ingoing/outgoing endpoints).

    Returns:
        A planar diagram representing the unknot.
    """
    k = PlanarDiagram() if not oriented else OrientedPlanarDiagram()
    node = "a"
    k.add_vertex(node, degree=2)
    k.set_endpoint((node, 0), (node, 1), IngoingEndpoint if oriented else Endpoint)
    k.set_endpoint((node, 1), (node, 0), OutgoingEndpoint if oriented else Endpoint)
    return k


def unlink(number_of_components: int, oriented: bool = False):
    """
    Construct the unlink with the given number of components (disjoint 2-valent loops).

    Args:
        number_of_components: Number of unlinked components.
        oriented: Oriented version is not implemented.

    Returns:
        A planar diagram representing the unlink.

    Raises:
        NotImplementedError: If ``oriented`` is ``True``.
    """
    if oriented:
        raise NotImplementedError()
    k = PlanarDiagram()
    for _ in range(number_of_components):
        node = unique_new_node_name(k)
        k.add_vertex(node, degree=2)
        k.set_endpoint((node, 0), (node, 1), IngoingEndpoint if oriented else Endpoint)
        k.set_endpoint((node, 1), (node, 0), OutgoingEndpoint if oriented else Endpoint)
    return k


def non_adjacent_combinations(elements: tuple):
    """
    Yield cyclically non-adjacent endpoint pairs from a face boundary.

    Pairs are at least two steps apart around the cycle; pairs on the same node
    are skipped.

    Args:
        elements: A tuple of endpoints (assumed in cyclic order around a face).

    Yields:
        Pairs ``(a, b)`` of endpoints that are non-adjacent in the cyclic order and
        lie on different nodes.
    """
    n = len(elements)
    for i in range(n):
        for j in range(i + 2, i + n - 1):  # ensure at least two apart (cyclic)
            a = elements[i]
            b = elements[j % n]
            if a.node != b.node:
                yield a, b


def generate_simple_graphs(
    n: int,
    degrees: int | list,
    parallel_edges: bool = True,
    loops: bool = True,
):
    """
    Generate connected plane graphs up to ``n`` vertices with degrees constrained to ``degrees``.

    The construction proceeds level-by-level from small seed graphs, adding either
    a new vertex, a new arc within a face (avoiding adjacent endpoints), parallel
    arcs, and optionally loops, while maintaining planarity and a degree cap.

    Args:
        n: Maximum number of vertices.
        degrees: Allowed vertex degrees (single int or list of ints).
        parallel_edges: If ``True``, allow parallel arcs.
        loops: If ``True``, allow loop insertion.

    Returns:
        A list of canonicalized graphs satisfying the degree constraints, sorted by:
        ``(number of vertices, number of endpoints, -number of loops)``.
    """
    d = set(degrees) if isinstance(degrees, list) else {degrees}

    P1 = path_graph(1)
    P2 = path_graph(2)
    C1 = cycle_graph(1)

    # Remove names to avoid polluting canonicalization.
    del P1.attr["name"]
    del P2.attr["name"]
    del C1.attr["name"]

    ls = LeveledSet(canonical(P1))
    ls.new_level(canonical(P2))
    if loops:
        ls.add(C1)

    max_degree = max(degrees)

    # Expand current frontier until no new graphs appear.
    while ls[-1]:
        ls.new_level()

        for graph in ls[-2]:
            l = len(graph)

            # 1) Add a new vertex incident to a face edge (respect degree cap).
            if l < n:
                for face in graph.faces:
                    for ep in face:
                        if graph.degree(ep.node) >= max_degree:
                            continue

                        g = graph.copy()
                        v = vertex_names[l + 1]
                        g.add_vertex(vertex_for_adding=v)
                        insert_arc(g, (ep, (v, 0)))
                        assert sanity_check(g)
                        ls.add(freeze(canonical(g)))

            # 2) Add a new arc inside a face between non-adjacent endpoints.
            for face in graph.faces:
                for arc in non_adjacent_combinations(face):
                    if any(graph.degree(ep.node) >= max_degree for ep in arc):
                        continue

                    g = graph.copy()
                    insert_arc(g, arc)
                    assert sanity_check(g)
                    ls.add(freeze(canonical(g)))

            # 3) Optionally add parallel arcs.
            if parallel_edges:
                for arc in graph.arcs:
                    ep1, ep2 = arc
                    if graph.degree(ep1.node) >= max_degree or graph.degree(ep2.node) >= max_degree:
                        continue
                    if ep1.node == ep2.node:
                        continue

                    g = graph.copy()
                    parallelize_arc(g, arc)
                    assert sanity_check(g)
                    ls.add(freeze(canonical(g)))

            # 4) Optionally add loops (respecting degree cap).
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
    graphs = sorted(
        graphs,
        key=lambda g: (len(g.vertices), len(g.endpoints), -len(get_loops(g))),
    )
    return graphs


def generate_knot_diagrams(n: int, kinks: bool = False):
    """
    Enumerate knot diagrams derived from simple 4-regular plane graphs up to ``n`` vertices.

    Each 4-valent plane graph is converted to crossings in all crossing-sign
    configurations; only one-component links (knots) are retained.

    Args:
        n: Maximum number of vertices in the underlying 4-regular graph.
        kinks: If ``True``, allow loops in the base graph (possible kink configurations).

    Returns:
        A list of canonical knot diagrams.
    """
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
    # Example: generate knots up to 4 vertices (allow kinks)
    knots = generate_knot_diagrams(4, kinks=True)