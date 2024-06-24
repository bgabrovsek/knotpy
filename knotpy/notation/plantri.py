"""
Plantri (ascii) planar code notation

See https://users.cecs.anu.edu.au/~bdm/plantri/
    https://users.cecs.anu.edu.au/~bdm/plantri/plantri-guide.txt.
"""

from string import ascii_letters
from collections import defaultdict
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.structure import parallel_arcs

__all__ = ['from_plantri_notation', 'to_plantri_notation']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

# TODO: call only once
# {0: 'a', 1: 'b', ...}
_numerical_to_ascii = dict(enumerate(ascii_letters))
# {'a': 0, 'b': 1, ...}
_ascii_to_numerical = dict(map(reversed, enumerate(ascii_letters)))


def to_plantri_notation(g, separator=",", ccw=False):
    """
    :param g: PlanarGraph class
    :param separator:
    :param ccw:
    :return: plantri planar acci code, example "bcde,aefc,abfd,acfe,adfb,bedc"
    """

    prepended_node_count = False  # do not prepend the node count

    if has_parallel_arcs(g):
        raise NotImplementedError("Parallel edges are not yet implemented for the ascii planar code notation.")

    # convert to ascii nodes ('a', 'b', ...)
    if g.number_of_nodes > len(ascii_letters):
        raise ValueError(f"Number of nodes cannot exceed {len(ascii_letters)}")

    node_dict = dict(zip(sorted(g.nodes), ascii_letters))  # TODO: implement mixed-type nodes

    result = f"{g.number_of_nodes} " if prepended_node_count else ""
    result += separator.join(
        [
            "".join([node_dict[ep.node] for ep in g.nodes[v]])
            for v in sorted(g.nodes)
        ]
    )

    return result


def from_plantri_notation(data: str, separator=",", ccw=True, node_type=str):
    """Creates a planar graph from an Plantri ASCII planar code string data.
    :param data: plantri ASCII planar ASCII code, example "6 bcde,aefc,abfd,acfe,adfb,bedc"
    :param separator:
    :param ccw:
    :param node_type:
    #:param create_using:
    :return:
    TODO: create using?
    TODO: Resolve ambiguities (?)
    """

    data = " ".join(data.split())

    # ignore prepended node count
    if '0' <= data[0] <= '9':
        data = data[data.find(" ") + 1:]

    if separator != " ":
        "".join(data.split())  # clean up string

    data = data.split(separator)
    nodes = ascii_letters[:len(data)]

    g = PlanarDiagram() #PlanarGraph()
    g.add_vertices_from(nodes, degrees=[len(word) for word in data])


    if len(nodes) == 1 and len(data[0]) == 4:
        g.set_arc(((nodes[0],0), (nodes[0],1)))
        g.set_arc(((nodes[0],2), (nodes[0],3)))
        return g

    #print(nodes)

    # create a double dictionary of nodes: occurrences[v][u] contains the positions of node u in the word of node v
    occurrences = {node: defaultdict(list) for node in nodes}
    for node, word in zip(nodes, data):
        for pos, letter in enumerate(word):
            occurrences[node][letter].append(pos)

    #print(occurrences)
    for v, word in zip(nodes, data):
        for v_pos, u in enumerate(word):
            u_pos = occurrences[u][v][(-occurrences[v][u].index(v_pos)) % len(occurrences[u][v])]  # reverse cyclic order
            if not ccw:
                v_pos = len(data[_ascii_to_numerical[v]]) - v_pos - 1
                u_pos = len(data[_ascii_to_numerical[u]]) - u_pos - 1
            g.set_arc(((v, v_pos), (u, u_pos)))

    return g


if __name__ == '__main__':
    g = PlanarGraph()
    g.add_vertices_from(["a","b","c"])
    g.set_arcs_from([ [("a",0),("b",0)], [("b",1),("c",0)]  ])
    print(g)
    n = to_plantri_notation(g)
    print(n)
    h = from_plantri_notation(n)
    print(h)
    #print(from_plantri_notation("3 cbbb,acaa,ab", prepended_node_count=True, ccw=False))
