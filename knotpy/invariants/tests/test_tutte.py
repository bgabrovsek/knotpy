from knotpy import from_knotpy_notation
from knotpy.tables.families import parallel_edges, bouquet, path_graph, cycle_graph
from knotpy.invariants.tutte import deletion_contraction
from knotpy.algorithms.canonical import canonical
from knotpy.algorithms.attributes import clear_attributes

def test_deletion_contraction_parallel_edges():

    g = parallel_edges(3)
    result = deletion_contraction(g, contract_bridges=False)
    result = sorted([canonical(g) for g in result])
    expected_result = [bouquet(1), bouquet(2), path_graph(2)]
    expected_result = sorted([canonical(g) for g in expected_result])

    for _ in result:
        clear_attributes(_)

    assert sorted(result) == sorted(expected_result)


def test_deletion_contraction_cycle():
    N = 5
    g = cycle_graph(N)
    result = deletion_contraction(g, contract_bridges=False)
    result = sorted([canonical(g) for g in result])
    expected_result = [path_graph(i) for i in range(2, N+1)] + [bouquet(1)]
    expected_result = sorted([canonical(g) for g in expected_result])

    for _ in result:
        clear_attributes(_)

    assert sorted(result) == sorted(expected_result)



def test_deletion_contraction_square_with_diagonal():

    g = from_knotpy_notation("a=V(c0 d1 b0) b=V(a2 d0) c=V(a0 d2) d=V(b1 a1 c1)")

    result = deletion_contraction(g, contract_bridges=False)
    result = sorted([canonical(g) for g in result])

    lollypop = from_knotpy_notation("a=V(b2) b=V(b1 b0 a0)")
    expected_result = deletion_contraction(cycle_graph(4), contract_bridges=False) + [path_graph(3), bouquet(2), lollypop, lollypop.copy()]

    expected_result = sorted([canonical(g) for g in expected_result])

    for _ in result:
        clear_attributes(_)

    assert sorted(result) == sorted(expected_result)

if __name__ == '__main__':
    test_deletion_contraction_parallel_edges()
    test_deletion_contraction_cycle()
    test_deletion_contraction_square_with_diagonal()