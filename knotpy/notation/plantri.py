"""
Plantri planar code notation.

See https://users.cecs.anu.edu.au/~bdm/plantri/
    https://users.cecs.anu.edu.au/~bdm/plantri/plantri-guide.txt.
"""

from string import ascii_letters
import re
from knotpy.classes.planardiagram import PlanarDiagram
#from knotpy.algorithms.structure import parallel_arcs

__all__ = ['from_plantri_notation', 'to_plantri_notation']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


#_numerical_to_ascii = dict(enumerate(ascii_letters))  # {0: 'a', 1: 'b', ...}
_ascii_to_numerical = {letter: index for index, letter in enumerate(ascii_letters)}  # {"a": 0, "b": 1, ...})


def to_plantri_notation(g):
    """
    Convert a `PlanarGraph` into plantri notation.

    Plantri notation represents a planar graph using a compact, human-readable format.
    The output follows the form: ``"5 bcde,aedc,abd,acbe,adb"``.

    **Format Details:**
        - Each node is represented by a letter (e.g., `a, b, c`).
        - The adjacency list for each node is a sequence of letters representing its neighbors in clockwise (CW) order.
        - Nodes are sorted and mapped to alphabetical labels.

    :param g: The planar graph to be converted.
    :type g: PlanarGraph
    :return: The plantri notation string representing the graph.
    :rtype: str
    :raises ValueError: If the graph contains more than 52 nodes.

    .. note::
        - The function assumes nodes are uniquely labeled and do not exceed 52 (`a-z, A-Z`).
        - If `g` has parallel edges, an error is raised (currently unimplemented).
        - Plantri's default orientation is **clockwise (CW)**.

    **Example:**
    ::
        g = PlanarGraph()
        g.add_vertices_from(["a", "b", "c", "d", "e"])
        g.set_arcs_from([ [("a", 0), ("b", 0)], [("b", 1), ("c", 0)], [("c", 1), ("d", 0)], [("d", 1), ("e", 0)] ])
        notation = to_plantri_notation(g)
        print(notation)  # Output: "bcde,aedc,abd,acbe,adb"
    """
    separator = ","

    # TODO: raise error if diagram has parallel arcs

    # convert to ascii nodes ('a', 'b', ...)
    if g.number_of_nodes > len(ascii_letters):
        raise ValueError(f"Number of nodes cannot exceed {len(ascii_letters)}")

    node_dict = dict(zip(sorted(g.nodes), ascii_letters))  # TODO: implement mixed-type nodes

    result = f"{g.number_of_nodes} "  # prepend node count
    result += separator.join(
        [
            "".join([node_dict[ep.node] for ep in g.nodes[v]])
            for v in g.nodes
        ]
    )

    return result



def from_plantri_notation(graph_string: str) -> PlanarDiagram:
    """
    Convert a plantri notation string into a `PlanarDiagram`.

    A plantri notation string represents a graph using either numerical or alphabetical notation.
    This function automatically detects the notation type and parses the graph accordingly.

    **Supported Notation Formats:**
        - **Numerical notation:**
          Example:
          ``"7: 1[2  3  4  5] 2[1  5  6  3] 3[1  2  6  4] 4[1  3  6  5] 5[1  4  6  2] 6[2  5  4  3]"``
        - **Alphabetical notation:**
          Example:
          ``"5 bcde,aedc,abd,acbe,adb"``

    :param graph_string: A string representing a planar graph in plantri notation.
    :type graph_string: str
    :return: A `PlanarDiagram` object representing the parsed graph.
    :rtype: PlanarDiagram
    :raises ValueError: If the number of vertices exceeds the supported limit.

    **Parsing Logic:**
        1. Detect whether the input is in **alphabetical** or **numerical** notation.
        2. Extract connections:
            - **Alphabetical notation**: Extracts sequences separated by commas and spaces.
            - **Numerical notation**: Extracts vertex connections enclosed in square brackets `[ ]`.
        3. Convert numerical indices to alphabetical labels (`1 → 'a'`, `2 → 'b'`, ...).
        4. Construct a `PlanarDiagram` with vertices labeled `"a", "b", "c", ...`.
        5. Add arcs:
            - Reverses connections to match **counterclockwise (CCW) order**, since plantri uses **clockwise (CW)** order.
    """

    # Is the plantri string in alphabetical or numerical notation?
    alphabetical = any(char.isalpha() for char in graph_string)

    # parsing
    # connections are just lists of adjacent nodes
    if alphabetical:
        connections = re.findall(r'\b[a-zA-Z]+\b', graph_string)  # extract sequences separated by commas and spaces

    else:
        connections = re.findall(r'\[([^\]]*)\]', graph_string)  # extract data inside [...]
        if len(connections) >= len(ascii_letters):
            raise ValueError(f"Plantri notation only up to {len(ascii_letters)} vertices is supported.")
        connections = [re.findall(r'\d+', s) for s in connections]  # extract integers separated by whitespace
        # convert indices 1->"a", 2->"b",...,
        connections = ["".join([ascii_letters[int(i)-1] for i in s]) for s in connections]

    connections = [a[0] + a[:0:-1] for a in connections]  # convert clockwise (CW) to counter-clockwise (CCW)
    connections = dict(zip(ascii_letters[:len(connections)], connections))  # make a dict {vertex: neighbours}

    #print("connections", connections)
    # make the graph

    g = PlanarDiagram()
    g.add_vertices_from(connections.keys())  # vertices are just "a", "b", "c", ... TODO: we can avoid making a dict

    # add arcs
    
    for vertex, neighbours in connections.items():
        for position, neighbour in enumerate(neighbours):
            # support for parallel edges
            # Count the previous occurrences of neighbor in a vertex’s neighbors.
            neighbour_occurrence = neighbours[:position].count(neighbour)  # 0 if neighbour appears for the 1st time, 1 if for the 2nd time,...
            # where in the neighbour's neighbour is vertex, but in reverse, since orientation of arcs is reversed between adjacent nodes
            vertex_position = [pos for pos, char in enumerate(connections[neighbour]) if char == vertex][-(neighbour_occurrence + 1)]

            g.set_arc(((vertex, position), (neighbour, vertex_position)))

    return g


if __name__ == '__main__':

    s = "5 bcde,aedc,abd,acbe,adb"
    #s = "bcbd,aca,ab,a"
    k = from_plantri_notation(s)
    s_ = to_plantri_notation(k)
    print(s)
    print(k)
    print(s_)
    exit()
    g = PlanarGraph()
    g.add_vertices_from(["a","b","c"])
    g.set_arcs_from([ [("a",0),("b",0)], [("b",1),("c",0)]  ])
    print(g)
    n = to_plantri_notation(g)
    print(n)
    h = from_plantri_notation(n)
    print(h)
    #print(from_plantri_notation("3 cbbb,acaa,ab", prepended_node_count=True, ccw=False))
