"""
Generation of graph and knot/link families fo diagrams.
"""

from __future__ import annotations

__all__ = ["bouquet", "cycle_graph", "generate_knot_diagrams", "generate_simple_graphs", "path_graph", "star_graph",
           "unknot", "unlink", "vertices_to_crossings", "project", "wheel_graph"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek"

from string import ascii_letters
from typing import Sequence

from knotpy import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.degree_sequence import degree_sequence
from knotpy.utils.set_utils import LeveledSet
from knotpy.algorithms.canonical import canonical
from knotpy.algorithms.insert import insert_arc
from knotpy.classes.freezing import freeze
from knotpy.algorithms.insert import parallelize_arc
from knotpy.algorithms.topology import loops as get_loops
from knotpy.algorithms.sanity import sanity_check
from knotpy.algorithms.insert import insert_loop
from knotpy.algorithms.topology import number_of_link_components
from knotpy.algorithms.naming import unique_new_node_name
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.node.crossing import Crossing
from knotpy.classes.node.vertex import Vertex
from knotpy.utils.set_utils import powerset
from knotpy.algorithms.symmetry import mirror


# graph generators

def path_graph(number_of_vertices: int) -> PlanarDiagram:
    """
    Build a path graph with ``number_of_vertices`` vertices.
    Vertices are named ``'a', 'b', 'c', ...`` and connected in a single edge.

    Args:
        number_of_vertices: Total number of vertices in the path (≥ 1).

    Returns:
        A planar diagram named ``"P_{n}"`` with a linear chain of arcs.
    """
    n = number_of_vertices
    k = PlanarDiagram(name=f"P_{n}")
    k.add_vertices_from(ascii_letters[:n])
    for i in range(number_of_vertices - 1):
        k.set_arc(
            (
                (ascii_letters[i], 0),
                (ascii_letters[i + 1], 0 if i == number_of_vertices - 2 else 1),
            )
        )
    return k


def cycle_graph(number_of_vertices: int) -> PlanarDiagram:
    """
    Build a cycle graph with ``number_of_vertices`` vertices.
    Vertices are named ``'a', 'b', 'c', ...`` and connected in a single cycle.

    Args:
        number_of_vertices: Size of the cycle (≥ 1).

    Returns:
        A planar diagram named ``"C_{n}"`` whose arcs form a cycle.
    """
    n = number_of_vertices
    k = PlanarDiagram(name=f"C_{n}")
    k.add_vertices_from(ascii_letters[:n])
    for i in range(n):
        k.set_arc(((ascii_letters[i], 0), (ascii_letters[(i + 1) % n], 1)))
    return k


def wheel_graph(number_of_vertices: int) -> PlanarDiagram:
    """
    Build a wheel graph as a ``PlanarDiagram`` with ``number_of_vertices`` vertices.

    A wheel graph consists of a cycle on ``n`` outer vertices plus a central
    vertex adjacent to all outer vertices (total vertices = ``n + 1``).

    Args:
        number_of_vertices: Total vertex count including the center (≥ 2).

    Returns:
        A planar diagram named ``"W_{n+1}"`` representing the wheel.
    """
    n = number_of_vertices - 1  # number of outer vertices
    k = PlanarDiagram(name=f"W_{n + 1}")
    k.add_vertices_from(ascii_letters[:n + 1])

    for i in range(n):
        # Spokes from the center to each outer vertex
        k.set_arc(((ascii_letters[0], i), (ascii_letters[i + 1], 0)))
        # Rim edges around the outer cycle
        k.set_arc(((ascii_letters[i + 1], 2), (ascii_letters[(i + 1) % n + 1], 1)))
    return k


def star_graph(number_of_vertices: int) -> PlanarDiagram:
    """
    Build a star graph as a ``PlanarDiagram`` with ``number_of_vertices`` vertices.

    One central vertex is connected to all others; ``(n-1)`` outer vertices are not
    mutually adjacent.

    Args:
        number_of_vertices: Total vertex count including the center (≥ 2).

    Returns:
        A planar diagram named ``"S_{n}"`` representing the star.
    """
    n = number_of_vertices - 1  # number of leaves
    k = PlanarDiagram(name=f"S_{n + 1}")
    k.add_vertices_from(ascii_letters[:n + 1])

    for i in range(n):
        k.set_arc(((ascii_letters[0], i), (ascii_letters[i + 1], 0)))
    return k


def bouquet(number_of_arcs: int) -> PlanarDiagram:
    """
    Build a bouquet graph (one vertex with ``number_of_arcs`` loops).

    Args:
        number_of_arcs: Number of loops attached to the single vertex.

    Returns:
        A planar diagram named ``"B_{m}"`` with one vertex and ``m`` loops.
    """
    k = PlanarDiagram(name=f"B_{number_of_arcs}")
    k.add_vertex("a")
    for i in range(number_of_arcs):
        k.set_arc((("a", 2 * i), ("a", 2 * i + 1)))
    return k


def parallel_edges(number_of_arcs: int) -> PlanarDiagram:
    """
    Build two vertices joined by ``number_of_arcs`` parallel arcs.

    Args:
        number_of_arcs: Number of parallel arcs between the two vertices.

    Returns:
        A planar diagram named ``"E_{m}"`` with two vertices and ``m`` parallel arcs.
    """
    k = PlanarDiagram(name=f"E_{number_of_arcs}")
    k.add_vertices_from("ab")
    for i in range(number_of_arcs):
        k.set_arc((("a", i), ("b", number_of_arcs - i - 1)))
    return k


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

def project(k: PlanarDiagram):
    k_copy = k.copy()
    k_copy.convert_nodes(nodes_for_converting=list(k.crossings), node_type=Vertex)
    return k_copy

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


def _non_adjacent_combinations(elements: tuple):
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
    while ls.iter_level(-1):
        ls.new_level()

        for graph in ls.iter_level(-2):
            l = len(graph)

            # 1) Add a new vertex incident to a face edge (respect degree cap).
            if l < n:
                for face in graph.faces:
                    for ep in face:
                        if graph.degree(ep.node) >= max_degree:
                            continue

                        g = graph.copy()
                        v = ascii_letters[l + 1]
                        g.add_vertex(vertex_for_adding=v)
                        insert_arc(g, (ep, (v, 0)))
                        assert sanity_check(g)
                        ls.add(freeze(canonical(g)))

            # 2) Add a new arc inside a face between non-adjacent endpoints.
            for face in graph.faces:
                for arc in _non_adjacent_combinations(face):
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