from knotpy.utils.disjoint_union_set import DisjointSetUnion
def test_dsu():
    # Example usage
    dsu = DisjointSetUnion([0, 1, 2, 3, 4])
    dsu.add(7)
    dsu[0] = 0
    dsu[3] = 0
    dsu[2] = 4
    dsu[0] = 0
    dsu[1] = 3
    dsu[5] = 6

    assert len(list(dsu.representatives())) == 4
    assert set(frozenset(x) for x in dsu) == {frozenset({2, 4}), frozenset({5, 6}), frozenset({0, 1, 3}), frozenset({7})}
    classes = dsu.classes()
    assert len(classes) == 4
    assert {0,1,3} in classes
    assert {2,4} in classes
    assert {5,6} in classes
    assert {7} in classes

if __name__ == '__main__':
    test_dsu()