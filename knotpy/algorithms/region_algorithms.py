__all__ = ['regions']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'

from knotpy.classes.planardiagram import PlanarDiagram


def regions(k: PlanarDiagram):
    """Iterates over regions (planar graph faces) of a planar diagram. The function takes the
    set of all endpoints, select an unused endpoint and travels along the edges, until there are no endpoints left.
    :param k: knotted object
    """

    unused_endpoints = set(k.endpoints)

    while unused_endpoints:
        ep = unused_endpoints.pop()
        region = list()
        while True:
            region.append(ep)
            ep = k.nodes[ep.node][(ep.position - 1) % len(k.nodes[ep.node])]
            if ep in unused_endpoints:
                unused_endpoints.remove(ep)
            else:
                break
        yield region


