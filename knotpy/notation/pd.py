"""
The planar diagram (PD) notation of a knotted structure is represented as an incidence list. 
See https://katlas.org/wiki/Planar_Diagrams.

Supported notation formats:
  - Mathematica: "Xp[1,9,2,8],Xn[3,10,4,11],X[5,3,6,2],X[7,1,8,13],X[9,4,10,5],X[11,7,12,6],P[12,13]"
  - KnotInfo: "[[1,5,2,4],[3,1,4,6],[5,3,6,2]]"
  - Topoly: "V[3,23];X[1,0,3,2];X[0,9,14,13];X[17,14,16,15];X[15,16,9,18];X[13,17,24,23];X[18,1,2,24]"

Node abbreviations:
  - V - vertex,
  - X - unsigned crossing,
  - Xp, + - positively signed crossing,
  - Xm, - - negatively signed crossing,
  - P, B - bivalent vertex,
"""
import re
import string

from collections import defaultdict

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.utils.string_utils import multi_replace, nested_split, abcABC
from knotpy.generate.simple import empty_knot
from knotpy.algorithms.node_operations import add_node_to
from knotpy.classes.node import Vertex, Crossing


__all__ = ['from_pd_notation', 'to_pd_notation']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


# def _parse_from_knotinfo(s: str) -> list:
#     """Return a list of pairs (node_abbr, list of adjacent nodes) from the knotinfo PD notation.
#     Example: "[[1,2],[2,0]]" -> [("X", [1,2]), ("X", [2,0])]
#     :param s: knotinfo PD notation
#     :return: list of pairs
#     """
#     s = multi_replace(s, {" ": "", "(": "[", ")": "]"})
#     return [("X", item) for item in eval(s)]
#
#
# _parse_from_notation_dispatcher = {"knotinfo": _parse_from_knotinfo}

_node_abbreviations = {
    "X": Crossing,
    "V": Vertex,
    #"B": BivalentVertex
}

_node_abbreviations_inv = {val: key for key, val in _node_abbreviations.items()}


def from_pd_notation(text: str, node_type=str, create_using=None, **attr):
    """Create planar diagram object from string containing the PD code.
    Autodetect PD codes of formats:
    - Mathematica: "V[1,2,3], X[2,3,4,5]", see https://knotinfo.math.indiana.edu/descriptions/pd_notation.html,
    - Knotinfo: "[[1,5,2,4],[3,1,4,6],[5,3,6,2]]", see http://katlas.org/wiki/Planar_Diagrams.

    :param text: string containing the PD notation
    :param node_type: int for nodes 0, 1, 2, or str for nodes "a", "b", ...
    :param create_using:
    :param attr: additional attributes to assign to the planar diagram (name, framing, ...)
    :return: planar diagram object
    """

    if create_using is not None and type(create_using) is not type:
        raise TypeError("Creating PD diagram with create_using instance not yet supported.")

    text = text.strip()
    text = multi_replace(text, ")]", {"] ": "]", ", ": ","}, ";,", ("],", "];"))

    # extract nested list (KnotInfo)
    if text[:2] in ("[[", "[(", "([", "((") and text[-2:] in ("]]", "])", ")]", "))"):
        text = text[1:-1]

    k = empty_knot(create_using=create_using)
    arc_dict = defaultdict(list)  # keys are arc numbers, values are arcs


    for node, subtext in enumerate(text.split(";")):
        # get node type and arc data
        if (i0 := subtext.find("[")) == -1 or \
           (i1 := subtext.find("]")) == -1:
            raise ValueError(f"Invalid PD node notation {subtext}.")
        node_arcs = eval(subtext[i0:i1+1])  # list of arcs
        node_abbr = subtext[:i0] if 1 <= i0 <= 2 else "X" if len(node_arcs) == 4 else "V"  # str, e.g. "X"
        node_name = abcABC[node] if node_type is str else node  # abc or 123

        k.add_node(node_for_adding=node_name,
                   create_using=_node_abbreviations[node_abbr],
                   degree=len(node_arcs))

        for pos, arc in enumerate(node_arcs):
            arc_dict[arc].append((node_name, pos))

    for arc in arc_dict.values():
        k.set_arc(arc)

    k.attr.update(attr)  # update given attribures

    #print(k)

    return k


def to_pd_notation(k: PlanarDiagram) -> str:
    """

    :param k:
    :return:
    """

    # associate each endpoint to its arc number (starting from 0).
    endpoint_dict = dict()
    for arc_number, (ep0, ep1) in enumerate(k.arcs):
        endpoint_dict[ep0] = arc_number
        endpoint_dict[ep1] = arc_number

    # print(endpoint_dict)
    # print(k)
    # print(list(k.arcs))
    # for node in k.nodes:
    #     print([ (ep, ep in endpoint_dict) for ep in k.nodes[node]   ])


    return ",".join(
        _node_abbreviations_inv[type(k.nodes[node])] +
        "[" +
        ",".join(str(endpoint_dict[ep]) for ep in k.nodes[node]) +
        "]"
        for node in k.nodes
        )

def _test():
    from knotpy.classes.knot import Knot
    from knotpy.classes.spatialgraph import SpatialGraph
    pd_code_mathematica = "X[1, 9, 2, 8], X[3, 10, 4, 11], X[5, 3, 6, 2],X[7, 1, 8, 12], X[9, 4, 10, 5], X[11,7,12,6]"
    pd_code_knotinfo = "[[4,2,5,1],[8,6,1,5],[6,3,7,4],[2,7,3,8]]"
    pd_code_topoly = "V[12,14,5],V[14,13,2],X[11,10,13,12],X[7,11,5,6],X[10,7,6,2]"

    k1 = from_pd_notation(pd_code_mathematica, node_type=str, create_using=Knot)
    print(k1)
    k2 = from_pd_notation(pd_code_knotinfo, node_type=str, create_using=Knot)
    print(k2)
    k3 = from_pd_notation(pd_code_topoly, node_type=str, create_using=SpatialGraph)
    print(k3)

    print(to_pd_notation(k1))
    print(to_pd_notation(k2))
    print(to_pd_notation(k3))

if __name__ == "__main__":
    _test()