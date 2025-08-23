from knotpy.notation.pd import from_pd_notation
from knotpy.algorithms.disjoint_union import number_of_disjoint_components, disjoint_union_decomposition, add_unknot, is_disjoint_union, disjoint_union
from knotpy.algorithms.canonical import canonical
from knotpy.algorithms.remove import remove_unknots
from knotpy.algorithms.topology import number_of_unknots
def test_unknots():
    pd_K_8_13 = "X[1,9,2,8],X[3,14,4,15],X[5,12,6,13],X[7,11,8,10],X[9,3,10,2],X[11,16,12,1],X[13,4,14,5],X[15,6,16,7]"

    k = from_pd_notation(pd_K_8_13)
    assert number_of_unknots(k) == 0
    assert not is_disjoint_union(k)
    assert number_of_disjoint_components(k) == 1

    k = add_unknot(k)
    assert number_of_unknots(k) == 1
    assert is_disjoint_union(k)
    assert number_of_disjoint_components(k) == 2

    k = add_unknot(k, number_of_unknots=2)
    assert number_of_unknots(k) == 3
    assert is_disjoint_union(k)
    assert number_of_disjoint_components(k) == 4

    remove_unknots(k)
    assert number_of_unknots(k) == 0
    assert not is_disjoint_union(k)
    assert number_of_disjoint_components(k) == 1


def test_disjoint_sum():
    pd_a = "X[1,5,2,4], X[3,1,4,6], X[5,3,6,2]"
    pd_b = "X[1,9,2,8],X[3,14,4,15],X[5,12,6,13],X[7,11,8,10],X[9,3,10,2],X[11,16,12,1],X[13,4,14,5],X[15,6,16,7]"
    pd_ab = "X[1,9,2,8],X[3,14,4,15],X[5,12,6,13],X[7,11,8,10],X[9,3,10,2],X[11,16,12,1],X[13,4,14,5],X[15,6,16,7],X[21,25,22,24],X[23,21,24,26],X[25,23,26,22]"

    a = from_pd_notation(pd_a)
    b = from_pd_notation(pd_b)
    ab = from_pd_notation(pd_ab)

    assert not is_disjoint_union(a)
    assert not is_disjoint_union(b)
    assert is_disjoint_union(ab)

    ab2 = disjoint_union(a, b)
    assert is_disjoint_union(ab2)

    assert len(ab2.nodes) == len(ab.nodes) == len(a.nodes) + len(b.nodes)


    a2, b2 = disjoint_union_decomposition(ab2)
    assert not is_disjoint_union(a2)
    assert not is_disjoint_union(b2)

    if len(a) < len(b):
        assert canonical(a) == canonical(a2) and canonical(a) != canonical(b2)
        assert canonical(b) == canonical(b2) and canonical(b) != canonical(a2)
    else:
        assert canonical(a) != canonical(a2) and canonical(a) == canonical(b2)
        assert canonical(b) != canonical(b2) and canonical(b) == canonical(a2)


if __name__ == "__main__":
    test_unknots()
    test_disjoint_sum()