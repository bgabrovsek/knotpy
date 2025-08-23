import knotpy as kp
from knotpy import bridges, is_bridge

from time import time

def test_bridges():
    N = 10
    g = kp.path_graph(N)
    assert len(bridges(g)) == N-1

    g = kp.star_graph(N)
    assert len(bridges(g)) == N-1

    for arc in g.arcs["a"]:
        assert is_bridge(g, arc)

    g = kp.star_graph(N)
    assert len(bridges(g)) == N - 1

    g = kp.star_graph(N)
    assert len(bridges(g)) == N - 1

    for arc in g.arcs["a"]:
        assert is_bridge(g, arc)

if __name__ == "__main__":
    test_bridges()
