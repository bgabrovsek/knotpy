"""
EM (Ewing-Millett) notation

This notation should be used as data default notation, since it is the most similar to the native class structure).

See "Ewing, B. & Millett, K. C. in The mathematical heritage of CF Gauss 225–266 (World Scientific, 1991)".
"""

from knotpy.classes.planargraph import PlanarGraph


__all__ = ['to_em_notation', 'from_em_notation']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


def to_em_notation(pg):
    """Returns EM code of planar diagram."""
    return {node: [adj_ep for adj_ep in pg.adj[node]] for node in pg.nodes}

def from_em_notation(data):
    """
    :param em: dictionary of lists of tuples
    :return: planardiagram
    """

    if isinstance(data, str):
        pd = eval(data)

    pg = PlanarGraph()
    for node in data:
        pg.add_node(node, len(data[node]))
        for pos, adj_endpoint in enumerate(data[node]):
            pg._add_single_endpoint((node, pos), adj_endpoint)
    return pg