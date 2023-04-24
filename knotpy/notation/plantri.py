"""
Plantri (ascii) planar code notation

See https://users.cecs.anu.edu.au/~bdm/plantri/
    https://users.cecs.anu.edu.au/~bdm/plantri/plantri-guide.txt.
"""

import string
from collections import defaultdict
from knotpy.classes.planargraph import PlanarGraph


__all__ = ['from_plantri_notation', 'to_plantri_notation']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

def ascii_to_numerical(g):
    """Renames the nodes a, b, c,... -> 0, 1, 2,... in place."""
    g.rename_nodes({c: ord(c) - ord('data') for c in g.nodes})


def numerical_to_ascii(g):
    """Renames the nodes 0, 1, 2,... -> data, b, c,... in place."""
    g.rename_nodes({i: chr(i + ord('data')) for i in g.nodes})


def to_plantri_notation(g, separator=",", prepended_node_count=False, ccw=True):
    """

    :param g: PlanarDiagram class
    :param separator:
    :param prepended_node_count:
    :param ccw:
    :return: plantri planar acci code, example "6 bcde,aefc,abfd,acfe,adfb,bedc"
    """

    if ccw is None:
        ccw = True

    if g.has_parallel_arcs():
        raise NotImplementedError("Parallel edges are not yet implemented for the ascii planar code notation.")

    # check if vertices are alphabetic (ascii)
    are_alphabetic = set(g.nodes) == {*string.ascii_lowercase[:g.number_of_nodes]}
    are_numeric = set(g.nodes) == {*range(g.number_of_nodes)}

    if not are_alphabetic and not are_numeric:
        raise ValueError("Can only save graph in ascii format if vertices are lower case characters or "
                         "integers between 0 and 25 (in order).")

    result = f"{g.number_of_nodes} " if prepended_node_count else ""
    if are_alphabetic:
        result += separator.join(["".join(list(zip(*g.adj[v]))[0][::2 * bool(ccw) - 1]) for v in sorted(g.nodes)])
    else:
        result += separator.join(["".join([chr(i + ord('data')) for i in list(zip(*g.adj[v]))[0]][::2 * bool(ccw) - 1])
                                  for v in sorted(g.nodes)])

    return result


def from_plantri_notation(data, separator=",", prepended_node_count=False, ccw=True, create_using=None):
    """Creates a planar graph from an Plantri ASCII planar code string data.
    :param data: plantri ASCII planar ASCII code, example "6 bcde,aefc,abfd,acfe,adfb,bedc"
    :param separator:
    :param prepended_node_count:
    :param ccw:
    :param create_using:
    :return:
    TODO: Resolve ambiguities (?)
    """

    _debug = False

    assert isinstance(data, str), "The data parameter should be a string."
    assert len(separator) == 1, "The separator must be a single character."

    data = data.strip()
    if prepended_node_count:
        n = int(data[:(space_index := data.find(" "))])
        data = data[space_index + 1:].strip()

    if _debug: print(data)

    data = (" " if separator == " " else "").join(data.split())  # clean up string
    #if _debug: print(data)
    data = data.lower().split(separator)  # only works up to 26 vertices
    nodes = string.ascii_lowercase[:len(data)]

    g = PlanarGraph() if create_using is None else create_using

    g.add_nodes(nodes, degrees=[len(word) for word in data])

    _o = lambda c: ord(c) - ord('a')  # 'a'->0, 'b'->1, ...

    # we create a double dictionary of nodes: occurrences[v][u] contains the positions of node u in the word of node v
    occurrences = {node: defaultdict(list) for node in nodes}
    for node, word in zip(nodes, data):
        for pos, letter in enumerate(word):
            occurrences[node][letter].append(pos)

    for v, word in zip(nodes, data):
        if _debug: print(f"{v}:{word}")
        for v_pos, u in enumerate(word):
            u_pos = occurrences[u][v][(-occurrences[v][u].index(v_pos)) % len(occurrences[u][v])]  # reverse cyclic order
            if not ccw:
                v_pos = len(data[_o(v)]) - v_pos - 1
                u_pos = len(data[_o(u)]) - u_pos - 1
            g.add_arc((v, v_pos), (u, u_pos))

    return g


if __name__ == '__main__':
    print(from_plantri_notation("3 cbbb,acaa,ab", prepended_node_count=True, ccw=False))
