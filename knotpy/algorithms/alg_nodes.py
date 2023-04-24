"""Simple algorithms/functions regarding nodes."""

__all__ = ['degree_sequence']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

from knotpy.generate.simple import house_graph



def degree_sequence(g):
    return sorted(g.degree().values())


if __name__ == "__main__":
    g = house_graph()
    print(degree_sequence(g))

