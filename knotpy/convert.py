
import knotpy
from collections import defaultdict
from knotpy.utils import iterable_depth

# from knotpy.generators import simple


def guess_notation_str(s):
    aliases = {
        "em": ["em", "ewing-millett", "ewing/millett"],
        "pd": ["pd", "planar diagram", "planar-diagram"],
    }
    rev_aliases = {val: key for key in aliases for val in aliases[key]}
    return rev_aliases[s.lower()]

    # TODO: raise error




### DATA -> SPATIAL GRAPH

def pg_from_list(data, create_using=None):
    pd = knotpy.classical.empty_pd(0, create_using)
    return knotpy
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
            raise TypeError("create_using is not a valid knotpy type or instance")

    pass


def to_em_notation(pg):
    """Returns EM code of planar diagram."""
    return {node: [adj_ep for adj_ep in pg.adj[node]] for node in pg.nodes}

def from_em_notation(em):
    """
    :param em: dictionary of lists of tuples
    :return: planardiagram
    """

    if isinstance(em, str):
        pd = eval(em)

    pg = knotpy.PlanarGraph()
    for node in em:
        pg.add_node(node, len(em[node]))
        for pos, adj_endpoint in enumerate(em[node]):
            pg._add_single_endpoint((node, pos), adj_endpoint)
    return pg




def to_pd_notation(pg) -> list:
    """Returns PD code of planar diagram."""
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

def from_pd_notation(pd):
    """
    :param pd: PD code (dictionary of lists)
    :return: planargraph
    """

    _debug = False

    if isinstance(pd, str):
        pd = eval(pd)

    # create inverse dictionary {arc: [(node1, pos1), (node2, pos2)}}
    arc_dict = defaultdict(list)
    for node in pd:
        for pos, arc in enumerate(pd[node]):
            arc_dict[arc].append((node, pos))

    pg = knotpy.PlanarGraph()

    if _debug: print("ad", arc_dict)

    for node in pd:
        pg.add_node(node, len(pd[node]))

    pg.add_arcs(arc_dict.values())

    return pg


def from_notation(incoming_data):
    """Auto-detects notation.
    :param incoming_data: PD or EM code
    :return:
    """
    if isinstance(incoming_data, str):
        incoming_data = eval(incoming_data)

    if iterable_depth(incoming_data) == 2:
        return from_pd_notation(incoming_data)

    if iterable_depth(incoming_data) == 3:
        return from_em_notation(incoming_data)


"""
def node_from_list(data, create_using=None):
    pd = simple.empty_node(0, create_using)
    return knotpy
    pass

def to_node(data, create_using=None):
    # if hasattr(data, "is_strict"):
    if isinstance(data, list):
        try:
            return node_from_list(data, create_using)
        except:
            raise TypeError("create_using is not a valid node type or instance")

    pass
"""