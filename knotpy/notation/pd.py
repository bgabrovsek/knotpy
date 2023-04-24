
from collections import defaultdict

from knotpy.classes.planargraph import PlanarGraph
from knotpy.generate.simple import empty_graph

__all__ = ['from_pd_notation', 'to_pd_notation']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'



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


# PD (planar diagram) notation, see http://katlas.org/wiki/Planar_Diagrams

def from_pd_notation(data):
    """
    :param data: PD code (dictionary of lists)
    :return: planargraph
    """

    _debug = False

    if isinstance(data, str):
        data = eval(data)

    # create inverse dictionary {arc: [(node1, pos1), (node2, pos2)}}
    arc_dict = defaultdict(list)
    for node in data:
        for pos, arc in enumerate(data[node]):
            arc_dict[arc].append((node, pos))

    pg = PlanarGraph()

    if _debug: print("ad", arc_dict)

    for node in data:
        pg.add_node(node, len(data[node]))

    pg.add_arcs(arc_dict.values())

    return pg


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




if __name__ == '__main__':
    pass