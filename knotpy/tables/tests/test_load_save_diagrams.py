
from knotpy.tables.diagram_reader import load_diagrams, load_diagram_sets
from knotpy.tables.diagram_writer import save_diagrams, save_diagram_sets
from knotpy.notation.native import from_knotpy_notation

from knotpy.tables.tests._helper import _safe_delete_file, _unique


def test_read_write_diagram():
    knots = [
        "a=X(b1 c0 c3 b2) b=X(c1 a0 a3 c2) c=X(a1 b0 b3 a2)",
        "a=X(c1 d0 d3 c2) b=X(d1 e0 e3 d2) c=X(e1 a0 a3 e2) d=X(a1 b0 b3 a2) e=X(b1 c0 c3 b2)",
        "a=X(c3 d0 b3 b2) b=X(d3 c0 a3 a2) c=X(b1 d2 d1 a0) d=X(a1 c2 c1 b0)",
        "a=V(a1 a0)",
        "a=X(c1 c0 d3 b2) b=X(d1 e0 a3 d2) c=X(a1 a0 e3 e2) d=X(e1 b0 b3 a2) e=X(b1 d0 c3 c2)",
    ]
    knots = set(from_knotpy_notation(k) for k in knots)

    save_diagrams(f"{_unique}_knots.csv", knots)
    knots2 = load_diagrams(f"{_unique}_knots.csv")


    assert knots == set(knots2)

    _safe_delete_file(f"{_unique}_knots.csv")

def test_read_write_diagram_sets():

    knots = [
        [
        "a=X(b1 c0 c3 b2) b=X(c1 a0 a3 c2) c=X(a1 b0 b3 a2)",
        "a=X(c1 d0 d3 c2) b=X(d1 e0 e3 d2) c=X(e1 a0 a3 e2) d=X(a1 b0 b3 a2) e=X(b1 c0 c3 b2)",
        "a=X(c3 d0 b3 b2) b=X(d3 c0 a3 a2) c=X(b1 d2 d1 a0) d=X(a1 c2 c1 b0)",
        ],[
        "a=V(a1 a0)",
        "a=X(c1 c0 d3 b2) b=X(d1 e0 a3 d2) c=X(a1 a0 e3 e2) d=X(e1 b0 b3 a2) e=X(b1 d0 c3 c2)",
        ],
        [
            "a=X(b1 c0 c3 b2) b=X(c1 a0 a3 c2) c=X(a1 b0 b3 a2)",
        ]
    ]
    knots = [set(from_knotpy_notation(k) for k in kn) for kn in knots]


    save_diagram_sets(f"{_unique}_knot_sets.csv", knots)
    knots2 = load_diagram_sets(f"{_unique}_knot_sets.csv")
    knots2= [set(kn) for kn in knots]

    assert knots == knots2

    _safe_delete_file(f"{_unique}_knot_sets.csv")
def test_read():
    pass


if __name__ == '__main__':
    test_read_write_diagram()
    test_read_write_diagram_sets()