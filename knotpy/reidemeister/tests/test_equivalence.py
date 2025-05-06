from knotpy.reidemeister.reidemeister import randomize_diagram
from knotpy.reidemeister.equivalence import reduce_equivalent_diagrams
from knotpy.classes.planardiagram import PlanarDiagram

def test_equivalence():
    a1 = PlanarDiagram("3_1")
    a2 = randomize_diagram(a1)
    a3 = randomize_diagram(a1)
    a4 = randomize_diagram(a1)

    b1 = PlanarDiagram("4_1")
    b2 = randomize_diagram(b1)
    b3 = randomize_diagram(b1)
    b4 = randomize_diagram(b1)

    result = reduce_equivalent_diagrams([a1, a2, a3, a4, b1, b2, b3, b4], allowed_moves="r1,r2,r3")

    assert len(result) == 2

    assert a1 in result
    assert b1 in result
    assert a2 not in result
    assert b2 not in result
    assert a3 not in result
    assert b3 not in result
    assert a4 not in result
    assert b4 not in result
    pass

if __name__ == '__main__':
    test_equivalence()
