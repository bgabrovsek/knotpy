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
from knotpy.utils.string_operations import multi_replace
from knotpy.generate.simple import empty_knot
from knotpy.algorithms.node_algorithms import add_node_to

__all__ = ['from_pd_notation', 'to_pd_notation']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


def _parse_from_knotinfo(s: str) -> list:
    s = multi_replace(s, {" ": "", "(": "[", ")": "]"})
    return [("X", item) for item in eval(s)]


_parse_from_notation_dispatcher = {"knotinfo": _parse_from_knotinfo}


def from_pd_notation(s: str, notation_format: str = "Mathematica", node_type=str, create_using=None):
    """Create planar diagram object from string.
    :param s: string representing the pd notation
    :param notation_format:
    :param nodetype: int (0, 1, 2, ...) or str ("a", "b", ...)
    :param create_using:
    :return: planar diagram object
    """
    notation_format = notation_format.lower().replace(" ", "")

    if notation_format not in _parse_from_notation_dispatcher:
        raise ValueError(f"Unknown PD notation {notation_format}")

    data = _parse_from_notation_dispatcher[notation_format](s)

    letters = string.ascii_lowercase + string.ascii_uppercase if node_type is str else None

    k = empty_knot(create_using=create_using)

    arc_dict = defaultdict(list)  # keys are arc numbers, values are arcs
    for node, (node_abbr, arcs) in enumerate(data):

        node_name = letters[node] if node_type is str else node
        add_node_to(k=k, node=node_name, node_type=node_abbr, degree=len(arcs))
        for pos, arc in enumerate(arcs):
            arc_dict[arc].append((node_name, pos))

    for arc in arc_dict.values():
        k.set_arc(arc)


    return k


def to_pd_notation(pg, notation_format: str = "Mathematica") -> str:

    # enumerate arcs

    """
    arcs = pg.arcs()
    ep_arc_dict = {arc[0]: i for i, arc in enumerate(arcs)} | {arc[1]: i for i, arc in enumerate(arcs)}
    return {node: [ep_arc_dict[adj_ep] for adj_ep in pg.adj[node]] for node in pg.nodes}
    """
    #TODO: use old version, not list of lists
    arcs = pg.arcs()
    ep_arc_dict = {arc[0]: i for i, arc in enumerate(arcs)} | {arc[1]: i for i, arc in enumerate(arcs)}
    return [[ep_arc_dict[adj_ep] for adj_ep in pg.adj[node]] for node in range(pg.number_of_nodes)]


# PD (planar diagram) notation, see http://katlas.org/wiki/Planar_Diagrams


def to_pd(data, create_using=None):
    """Create planar diagram from data and store to create using.
    Supported notations: EM code, PD code

    :param data: known types are:
        string - ...
        dict, where keys are tuples or lists ...
    :param create_using:
    :return:
    """

    if isinstance(data, str):
        raise NotImplemented("Planar Diagram form string not implemented.")

    if isinstance(data, list):
        try:
            return pg_from_list(data, create_using)
        except:
            raise TypeError("create_using is not data valid knotpy type or instance")

    pass




def pg_from_list(data, create_using=None):
    raise NotImplementedError()
    #pd = kp.classical.empty_pd(0, create_using)
    #return pd
    pass


def to_planardiagram(data, create_using=None):
    """Create planar diagram from data and store to create using.
    Supported notations: EM code, PD code

    :param data: known types are:
        string - ...
        dict, where keys are tuples or lists ...
    :param create_using:
    :return:
    """

    if isinstance(data, str):
        raise NotImplemented("Planar Diagram form string not implemented.")

    if isinstance(data, list):
        try:
            return pg_from_list(data, create_using)
        except:
            raise TypeError("create_using is not data valid knotpy type or instance")

    pass

def _test():
    notation_knotinfo = "[[1,7,2,6],[3,9,4,8],[5,12,6,13],[7,3,8,2],[9,15,10,14],[11,1,12,16],[13,4,14,5],[15,11,16,10]]"
    k = from_pd_notation(notation_knotinfo, notation_format="knotinfo", node_type=str)
    print(k)



if __name__ == "__main__":
    _test()