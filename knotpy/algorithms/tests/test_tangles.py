import knotpy as kp

def test_decompose():
    for name in ("6_3", "5_2", "8_10", "8_16", "9_2", "9_21", "10_114"):
        k = kp.knot(name)

        for d in kp.tangle_decompositions(k):
            assert len(d) == 2
            assert sum(len(_) - 4 for _ in d) == len(k)

            k_reconstructed = kp.compose_tangles(*d)
            assert len(k) == len(k_reconstructed)

            assert kp.canonical(k) == kp.canonical(k_reconstructed)

def test_tangle_63():
    k = kp.knot("6_3")

    assert len(kp.arc_cut_sets(k, 4, minimum_partition_nodes=2)) == 3
    assert len(kp.arc_cut_sets(k, 4, minimum_partition_nodes=2, return_partition=True)) == 3
    assert len(kp.arc_cut_sets(k, 4, minimum_partition_nodes=2, return_ccw_ordered_endpoints=True)) == 3
    assert len(kp.arc_cut_sets(k, 4, minimum_partition_nodes=2, return_partition=True, return_ccw_ordered_endpoints=True)) == 3

if __name__ == "__main__":
    test_tangle_63()
    test_decompose()
