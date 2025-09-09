from knotpy.tables.theta import theta
from knotpy.reidemeister.reidemeister import randomize_diagram
from knotpy.reidemeister.simplify import reduce_equivalent_diagrams
from knotpy.classes.planardiagram import PlanarDiagram
import knotpy as kp

def test_equivalence_knots():
    """ Create 8 diagrams, four trefoils and four figure-8s, and check that they are reduced to two."""
    trefoil = PlanarDiagram("3_1")
    figure8 = PlanarDiagram("4_1")

    trefoil_r = kp.to_condensed_em_notation(trefoil)
    figure8_r = kp.to_condensed_em_notation(figure8)

    trefoil_r = kp.from_condensed_em_notation(trefoil_r)
    figure8_r = kp.from_condensed_em_notation(figure8_r)

    assert trefoil == trefoil_r
    assert figure8 == figure8_r
    #print("k")

    while True:
        diagrams = [trefoil, randomize_diagram(trefoil), randomize_diagram(trefoil), randomize_diagram(trefoil),
                    figure8, randomize_diagram(figure8), randomize_diagram(figure8), randomize_diagram(figure8)]
        if not (diagrams[1] == diagrams[0] or diagrams[2] == diagrams[0] or diagrams[3] == diagrams[0]
            or diagrams[5] == diagrams[4] or diagrams[6] == diagrams[4] or diagrams[7] == diagrams[4]):
            break


    #print("INPUT:", diagrams)

    result = reduce_equivalent_diagrams(diagrams)

    #print("OUTPUT:", result)

    assert len(result) == 2
    assert trefoil in result
    assert figure8 in result

    for k in diagrams[1:4] + diagrams[5:]:
        assert k not in result

def test_equivalence_theta_curves():
    t1 = PlanarDiagram("t0_1")
    t2 = PlanarDiagram("t3_1")
    t3 = PlanarDiagram("t4_1")
    t4 = PlanarDiagram("h0_1")
    t5 = PlanarDiagram("h2_1")

    thetas = [t1, t2, t3, t4, t5]
    print("..")
    for k in thetas:
        print(k)


if __name__ == '__main__':

    test_equivalence_knots()


"""
Problem:

assert here:
for k in diagrams[1:4] + diagrams[5:]:
    assert k not in result
        


INPUT: [Diagram named 3_1 a → X(b3 c0 c3 b0), b → X(a3 c2 c1 a0), c → X(a1 b2 b1 a2), Diagram named 3_1 b → X(f1 h3 h2 f2), c → X(f3 g0 g3 f0), f → X(c3 b0 b3 c0), g → X(c1 h1 h0 c2), h → X(g2 g1 b2 b1), Diagram named 3_1 a → X(e3 f3 c3 e0), c → X(f2 e2 e1 a2), e → X(a3 c2 c1 a0), f → X(f1 f0 c0 a1), Diagram named 3_1 a → X(c2 b1 e3 e2), b → X(e0 a1 c1 c0) _r3=True, c → X(b3 b2 a0 e1) _r3=True, e → X(b0 c3 a3 a2) _r3=True, Diagram named 4_1 a → X(b3 b2 c3 d0), b → X(d3 c0 a1 a0), c → X(b1 d2 d1 a2), d → X(a3 c2 c1 b0), Diagram named 4_1 a → X(c0 f0 f3 e1) _r3=True, b → X(e2 g3 g2 c3) _r3=True, c → X(a0 d2 d1 b3), d → X(e3 c2 c1 e0), e → X(d3 a3 b0 d0) _r3=True, f → X(a1 g1 g0 a2), g → X(f2 f1 b2 b1), Diagram named 4_1 a → X(b3 b2 c3 d0), b → X(d3 c0 a1 a0), c → X(b1 f3 d1 a2), d → X(a3 c2 f0 b0), f → X(d2 f2 f1 c1), Diagram named 4_1 a → X(b3 b2 c3 d0), b → X(d3 c0 a1 a0), c → X(b1 d2 d1 a2), d → X(a3 c2 c1 b0)]
OUTPUT: {Diagram named 3_1 a → X(b3 c0 c3 b0), b → X(a3 c2 c1 a0), c → X(a1 b2 b1 a2): {Diagram named 3_1 a → X(e3 f3 c3 e0), c → X(f2 e2 e1 a2), e → X(a3 c2 c1 a0), f → X(f1 f0 c0 a1), Diagram named 3_1 a → X(c2 b1 e3 e2), b → X(e0 a1 c1 c0) _r3=True, c → X(b3 b2 a0 e1) _r3=True, e → X(b0 c3 a3 a2) _r3=True, Diagram named 3_1 b → X(f1 h3 h2 f2), c → X(f3 g0 g3 f0), f → X(c3 b0 b3 c0), g → X(c1 h1 h0 c2), h → X(g2 g1 b2 b1)}, Diagram named 4_1 a → X(b3 b2 c3 d0), b → X(d3 c0 a1 a0), c → X(b1 d2 d1 a2), d → X(a3 c2 c1 b0): {Diagram named 4_1 a → X(b3 b2 c3 d0), b → X(d3 c0 a1 a0), c → X(b1 f3 d1 a2), d → X(a3 c2 f0 b0), f → X(d2 f2 f1 c1), Diagram named 4_1 a → X(c0 f0 f3 e1) _r3=True, b → X(e2 g3 g2 c3) _r3=True, c → X(a0 d2 d1 b3), d → X(e3 c2 c1 e0), e → X(d3 a3 b0 d0) _r3=True, f → X(a1 g1 g0 a2), g → X(f2 f1 b2 b1)}}
Traceback (most recent call last):
  File "/home/bostjan/Dropbox/Code/knotpy/knotpy/reidemeister/tests/test_equivalence.py", line 43, in <module>
    test_equivalence_knots()
  File "/home/bostjan/Dropbox/Code/knotpy/knotpy/reidemeister/tests/test_equivalence.py", line 25, in test_equivalence_knots
    assert k not in result
AssertionError
(knotpy) bostjan@H

"""