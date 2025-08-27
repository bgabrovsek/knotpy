from knotpy import bouquet
from knotpy.tables.families import path_graph, cycle_graph
from knotpy.algorithms.remove import remove_arc, remove_empty_nodes
from knotpy.algorithms.canonical import canonical


def test_remove_edge():
    N = 6

    # If we remove an edge from a path P(n) it becomes P(n-1)

    g = path_graph(N)
    remove_arc(g, g.arcs["a"][0], inplace=True)
    remove_empty_nodes(g, inplace=True)

    assert canonical(g) == canonical(path_graph(N - 1))

    # If we remove an edge from a cycle C(n) it becomes a path P(n)

    g = cycle_graph(N)
    remove_arc(g, g.arcs["a"][0], inplace=True)
    remove_empty_nodes(g, inplace=True)

    assert canonical(g) == canonical(path_graph(N))

    g = bouquet(N)
    remove_arc(g, g.arcs["a"][0], inplace=True)
    assert canonical(g) == canonical(bouquet(N - 1))


if __name__ == "__main__":
    test_remove_edge()
