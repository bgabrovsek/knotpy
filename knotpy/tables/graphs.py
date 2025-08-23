from __future__ import annotations

from string import ascii_letters
from knotpy import PlanarDiagram


def path_graph(number_of_vertices: int) -> PlanarDiagram:
    """
    Build a path graph on ``number_of_vertices`` vertices as a ``PlanarDiagram``.

    Vertices are named ``'a', 'b', 'c', ...`` and connected in a single chain.

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
    Build a cycle graph on ``number_of_vertices`` vertices as a ``PlanarDiagram``.

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
    Build a wheel graph as a ``PlanarDiagram``.

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
    Build a star graph as a ``PlanarDiagram``.

    One central vertex is connected to all others; outer vertices are not
    mutually adjacent. Total vertices = ``number_of_vertices``.

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

