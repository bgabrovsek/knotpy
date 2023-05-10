"""Simple algorithms/functions regarding arcs."""

__all__ = ['has_parallel_arcs']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

#from knotpy.generate.simple import house_graph




def has_parallel_arcs(self):
    """Checks if graph has parallel arcs/edges."""
    return any((lambda _: len(_) != len(set(_)))(list(zip(*self._adj[v]))[0]) for v in self.nodes)


