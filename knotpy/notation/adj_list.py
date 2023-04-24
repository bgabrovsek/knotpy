
from knotpy.notation.plantri import from_plantri_notation


__all__ = ['to_adjacency_list']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

def to_adjacency_list(g):
    """Converts to a graph adjacency list. This forgets the planar structure (can be reconstructed?)."""
    return [(v, u) for v in g.nodes for u, u_pos in g.adj[v]]


if __name__ == "__main__":
    g = from_plantri_notation("bcde, aec, abfd, acfg, aghb, chgd, dfhe, egf")
    print(to_adjacency_list(g))
