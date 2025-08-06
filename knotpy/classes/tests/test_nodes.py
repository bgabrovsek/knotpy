import knotpy as kp
import knotpy.algorithms.remove


def test_remove_bivalent_vertex():

    k = kp.from_pd_notation("V(0,1),X(0,3,2,4),X(3,1,4,2)", create_using=kp.PlanarDiagram)

    assert k.nodes["b"][0].node == "a"
    assert k.nodes["c"][1].node == "a"

    knotpy.algorithms.remove.remove_bivalent_vertices(k)

    assert len(k.nodes) == 2
    assert len(k.crossings) == 2
    assert len(k.vertices) == 0

    assert k.nodes["b"][0].node == "c"
    assert k.nodes["c"][1].node == "b"

    # do not remove
    k = kp.from_pd_notation("V(0,0)", create_using=kp.PlanarDiagram)
    knotpy.algorithms.remove.remove_bivalent_vertices(k)
    assert len(k.vertices) == 1


if __name__ == "__main__":
    test_remove_bivalent_vertex()