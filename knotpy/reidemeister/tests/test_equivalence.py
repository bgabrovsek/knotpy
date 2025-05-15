from knotpy.catalog.knot_tables import get_theta_curves
from knotpy.reidemeister.reidemeister import randomize_diagram
from knotpy.reidemeister.equivalence import reduce_equivalent_diagrams
from knotpy.classes.planardiagram import PlanarDiagram

def test_equivalence_knots():
    """ Create 8 diagrams, four trefoils and four figure-8s, and check that they are reduced to two."""
    trefoil = PlanarDiagram("3_1")
    figure8 = PlanarDiagram("4_1")

    diagrams = [trefoil, randomize_diagram(trefoil), randomize_diagram(trefoil), randomize_diagram(trefoil),
                figure8, randomize_diagram(figure8), randomize_diagram(figure8), randomize_diagram(figure8)]
    result = reduce_equivalent_diagrams(diagrams)

    assert len(result) == 2
    assert trefoil in result
    assert figure8 in result

    for k in diagrams[1:4] + diagrams[5:]:
        assert k not in result

# def test_equivalence_theta_curves():
#     t1 = PlanarDiagram("t0_1")
#     t2 = PlanarDiagram("+t3_1")
#     t3 = PlanarDiagram("t4_1.1")
#     t4 = PlanarDiagram("h0_1")
#     t5 = PlanarDiagram("h2_1.1")
#
#     thetas = [t1, t2, t3, t4, t5]
#     print("..")
#     for k in thetas:
#         print(k)


if __name__ == '__main__':
    test_equivalence_knots()
    # test_equivalence_theta_curves()
