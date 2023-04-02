import knotpy as kp
#from networkx.classes.graphviews import reverse_view, subgraph_view

__all__ = [
    "degree_sequence",
]


def degree_sequence(PG):
    """Returns the degree sequence of the (planar) graph G."""
    return sorted(PG.degree().values())

