# tests/test_dsu.py

from knotpy.utils.disjoint_union_set import DisjointSetUnion


def test_init_and_add():
    dsu = DisjointSetUnion([1, 2, 3])
    assert set(dsu.elements) == {1, 2, 3}
    dsu.add(2)  # no-op
    dsu.add(4)
    assert set(dsu.elements) == {1, 2, 3, 4}


def test_find_unknown_and_known():
    dsu = DisjointSetUnion()
    assert dsu.find("x") is None
    dsu.add("x")
    assert dsu.find("x") == "x"


def test_union_and_connectivity():
    dsu = DisjointSetUnion([1, 2, 3, 4])
    dsu.union(1, 2)
    assert dsu.find(1) == dsu.find(2)
    assert dsu.find(3) != dsu.find(1)
    # union with unknown is a no-op
    dsu.union(1, 999)
    assert dsu.find(1) == dsu.find(2)


def test_iadd_and_setitem_shortcuts():
    dsu = DisjointSetUnion()
    dsu += "a"
    assert "a" in set(dsu.elements)
    dsu["a"] = "b"  # add both + union
    assert dsu.find("a") == dsu.find("b")


def test_iter_components_and_len():
    dsu = DisjointSetUnion([1, 2, 3, 4, 5])
    dsu.union(1, 2)
    dsu.union(3, 4)
    comps = [set(c) for c in dsu]  # iterate components
    assert {1, 2} in comps
    assert {3, 4} in comps
    assert {5} in comps
    assert len(dsu) == 3  # three components


def test_to_set_and_unknown():
    dsu = DisjointSetUnion([1, 2, 3])
    dsu.union(1, 2)
    assert dsu.to_set(1) == {1, 2}
    assert dsu.to_set(999) == set()


def test_representatives_and_classes():
    dsu = DisjointSetUnion([10, 20, 30, 40])
    dsu.union(10, 30)
    reps = list(dsu.representatives())
    # reps are mins of each component; order not guaranteed
    assert set(reps) == {10, 20, 40}
    classes = dsu.classes()
    assert any(set(c) == {10, 30} for c in classes)
    assert any(set(c) == {20} for c in classes)
    assert any(set(c) == {40} for c in classes)


def test_to_dict_rep_map():
    dsu = DisjointSetUnion([1, 2, 3, 4])
    dsu.union(1, 2)
    d = dsu.to_dict()
    # reps are mins of each component
    assert d[1] == {2}
    assert d[3] == set()
    assert d[4] == set()


def test_path_compression_idempotence():
    dsu = DisjointSetUnion(range(6))
    # chain unions to form a tall-ish tree
    dsu.union(0, 1)
    dsu.union(1, 2)
    dsu.union(2, 3)
    dsu.union(3, 4)
    dsu.union(4, 5)

    r1 = dsu.find(5)
    r2 = dsu.find(5)  # second find should be quick and yield same rep
    assert r1 == r2
    # all in one component
    assert len(dsu) == 1


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

def test_find_class():
    dsu = DisjointSetUnion([0,1,2,3,4,5,6])
    dsu[0] = 1
    dsu[2] = 3
    dsu[4] = 5
    dsu[5] = 1
    assert dsu.find(0) == dsu.find(1) == dsu.find(5)

    print(dsu.find(5))


if __name__ == "__main__":
    test_find_class()
    exit()


    # Manual runner: invoke all tests directly (handy without pytest)
    for name, func in list(globals()).items():
        if name.startswith("test_") and callable(func):
            print(f"Running {name}...")
            func()
    print("All manual DSU tests passed.")
