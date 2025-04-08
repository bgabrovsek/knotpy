from knotpy import PlanarDiagram
from string import ascii_letters


def path_graph(number_of_vertices: int):
    """
    Create a path graph with the specified number of vertices.

    Args:
        number_of_vertices: The number of vertices in the path graph. Should be a
            positive integer representing the total vertices.

    Returns:
        The generated path graph as a PlanarDiagram object with the given number
        of vertices connected linearly, representing the path structure.
    """
    n = number_of_vertices
    k = PlanarDiagram(name=f"P_{n}")
    k.add_vertices_from(ascii_letters[:n])
    for i in range(number_of_vertices-1):
        k.set_arc(((ascii_letters[i], 0), (ascii_letters[i + 1], 0 if i == number_of_vertices-2else 1)))

    return k


def cycle_graph(number_of_vertices: int):
    """
    Create a cycle graph represented as a PlanarDiagram.

    Args:
        number_of_vertices (int): The number of vertices in the cycle graph.

    Returns:
        PlanarDiagram: A PlanarDiagram object representing the cycle graph with
        the specified number of vertices.
    """

    n = number_of_vertices
    k = PlanarDiagram(name=f"C_{n}")
    k.add_vertices_from(ascii_letters[:n])
    for i in range(n):
        k.set_arc(((ascii_letters[i], 0), (ascii_letters[(i + 1) % n], 1)))

    return k


def wheel_graph(number_of_vertices: int):
    """
    Create a wheel graph with the specified number of vertices.

    Args:
        number_of_vertices (int): The total number of vertices in the wheel graph, including the center.

    Returns:
        PlanarDiagram: A planar diagram representing the constructed wheel graph.
    """
    n = number_of_vertices - 1  # outer vertices
    k = PlanarDiagram(name=f"W_{n + 1}")
    k.add_vertices_from(ascii_letters[:n + 1])

    for i in range(n):
        k.set_arc(((ascii_letters[0], i), (ascii_letters[i + 1], 0)))  # center arc
        k.set_arc(((ascii_letters[i + 1], 2), (ascii_letters[(i + 1) % n + 1], 1)))  # circular arcs

    return k


def star_graph(number_of_vertices: int):
    """
    Generates a star graph with a specified number of vertices.

    A star graph is a type of graph where one central node is connected to all
    other nodes, and those other nodes have no connections to each other.

    Args:
        number_of_vertices (int): The total number of vertices in the star graph,
            including the central vertex. Must be greater than or equal to 2.

    Returns:
        PlanarDiagram: A planar diagram object of the star graph, with vertices
            labeled using the ASCII alphabet starting from 'a'. The arcs represent
            the connections from the central node to each outer node.

    Raises:
        ValueError: If the `number_of_vertices` is less than 2.
    """
    n = number_of_vertices - 1  # outer vertices
    k = PlanarDiagram(name=f"S_{n + 1}")
    k.add_vertices_from(ascii_letters[:n + 1])

    for i in range(n):
        k.set_arc(((ascii_letters[0], i), (ascii_letters[i + 1], 0)))  # center arc

    return k


def bouquet(number_of_arcs: int):
    """
    Creates a bouquet graph represented as a PlanarDiagram.

    This function generates a bouquet graph with the specified number
    of arcs. A bouquet graph is a graph with a single vertex where
    each arc is a loop that starts and ends at the same vertex.

    Args:
        number_of_arcs (int): The number of arcs (loops) to include in
            the bouquet graph.

    """
    k = PlanarDiagram(name=f"B_{number_of_arcs}")
    k.add_vertex("a")
    for i in range(number_of_arcs):
        k.set_arc((("a", 2 * i), ("a", 2 * i + 1)))

    return k


def parallel_edges(number_of_arcs: int):
    """
    Creates a planar diagram with parallel edges between two sets of vertices.

    Args:
        number_of_arcs (int): The number of arcs to create between the vertices.

    Returns:
        PlanarDiagram: A planar diagram object with the defined arcs.
    """
    k = PlanarDiagram(name=f"E_{number_of_arcs}")
    k.add_vertices_from("ab")
    for i in range(number_of_arcs):
        k.set_arc((("a", i), ("b", number_of_arcs - i - 1)))

    return k


def handcuff_link():
    k = PlanarDiagram(name="H")
    k.add_vertices_from("ab")
    k.set_arc((("a", 0), ("a", 1)))
    k.set_arc((("b", 0), ("b", 1)))
    k.set_arc((("a", 2), ("b", 2)))

    return k


def theta_curve():
    k = PlanarDiagram(name="Θ")
    k.add_vertices_from("ab")
    k.set_arc((("a", 0), ("b", 2)))
    k.set_arc((("a", 1), ("b", 1)))
    k.set_arc((("a", 2), ("b", 0)))

    return k

