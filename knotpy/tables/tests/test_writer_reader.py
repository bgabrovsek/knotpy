import knotpy as kp
from knotpy.tables.tests._helper import _safe_delete_file, _unique

def test_writer_table_diagram():

    diagrams = [
        kp.from_knotpy_notation("a=V(b0) b=X(a0 c0 d3 c1) c=X(b1 b3 e3 f0) d=X(f3 f2 e1 b2) e=X(g0 d2 f1 c2) f=X(c3 e2 d1 d0) g=V(e0) ['name'=1]"),
        kp.from_knotpy_notation("a=V(b0) b=V(a0) ['name'=2]"),
        kp.from_knotpy_notation("a=V(b3) b=X(c3 d0 c0 a0) c=X(b2 e0 e3 b0) d=X(b1 f0 f3 g0) e=X(c1 f2 f1 c2) f=X(d1 e2 e1 d2) g=V(d3) ['name'=3]"),
        kp.from_knotpy_notation("a=V(b0) b=X(a0 c0 c3 d0) c=X(b1 e0 d1 b2) d=X(b3 c2 f3 e1) e=X(c1 d3 f1 f0) f=X(e3 e2 g0 d2) g=V(f2) ['name'=4]")
    ]

    table = [
        {"diagram": k, "affine": kp.affine_index_polynomial(k)}
        for k in diagrams
    ]

    kp.save_invariant_table(filename=_unique + "_writer_reader_diagram.txt", table=table)
    loaded = kp.load_invariant_table(filename=_unique + "_writer_reader_diagram.txt")
    load_should_be = {
        d["diagram"]: {"affine": d["affine"]}
        for d in table
    }
    assert loaded == load_should_be

    _safe_delete_file(_unique + "_writer_reader_diagram.txt")



def test_writer_dict_diagram():

    diagrams = [
        kp.from_knotpy_notation("a=V(b0) b=X(a0 c0 d3 c1) c=X(b1 b3 e3 f0) d=X(f3 f2 e1 b2) e=X(g0 d2 f1 c2) f=X(c3 e2 d1 d0) g=V(e0) ['name'=1]"),
        kp.from_knotpy_notation("a=V(b0) b=V(a0) ['name'=2]"),
        kp.from_knotpy_notation("a=V(b3) b=X(c3 d0 c0 a0) c=X(b2 e0 e3 b0) d=X(b1 f0 f3 g0) e=X(c1 f2 f1 c2) f=X(d1 e2 e1 d2) g=V(d3) ['name'=3]"),
        kp.from_knotpy_notation("a=V(b0) b=X(a0 c0 c3 d0) c=X(b1 e0 d1 b2) d=X(b3 c2 f3 e1) e=X(c1 d3 f1 f0) f=X(e3 e2 g0 d2) g=V(f2) ['name'=4]")
    ]

    table = {
        k: {"affine": kp.affine_index_polynomial(k)}
        for k in diagrams
    }

    kp.save_invariant_table(filename=_unique + "_writer_reader_diagram2.txt", table=table)
    loaded = kp.load_invariant_table(filename=_unique + "_writer_reader_diagram2.txt")
    assert loaded == table

    _safe_delete_file(_unique + "_writer_reader_diagram2.txt")


def test_writer_table_name():

    diagrams = [
        kp.from_knotpy_notation("a=V(b0) b=X(a0 c0 d3 c1) c=X(b1 b3 e3 f0) d=X(f3 f2 e1 b2) e=X(g0 d2 f1 c2) f=X(c3 e2 d1 d0) g=V(e0) ['name'=1]"),
        kp.from_knotpy_notation("a=V(b0) b=V(a0) ['name'=2]"),
        kp.from_knotpy_notation("a=V(b3) b=X(c3 d0 c0 a0) c=X(b2 e0 e3 b0) d=X(b1 f0 f3 g0) e=X(c1 f2 f1 c2) f=X(d1 e2 e1 d2) g=V(d3) ['name'=3]"),
        kp.from_knotpy_notation("a=V(b0) b=X(a0 c0 c3 d0) c=X(b1 e0 d1 b2) d=X(b3 c2 f3 e1) e=X(c1 d3 f1 f0) f=X(e3 e2 g0 d2) g=V(f2) ['name'=4]")
    ]

    table = [
        {"name":k.name, "diagram": k, "affine": kp.affine_index_polynomial(k)}
        for k in diagrams
    ]

    kp.save_invariant_table(filename=_unique + "_writer_reader_name.txt", table=table)
    loaded = kp.load_invariant_table(filename=_unique + "_writer_reader_name.txt")
    load_should_be = {
        str(d["name"]): {"diagram":d["diagram"], "affine": d["affine"]}
        for d in table
    }
    assert loaded == load_should_be


    _safe_delete_file(_unique + "_writer_reader_name.txt")


def test_writer_dict_name():

    diagrams = [
        kp.from_knotpy_notation("a=V(b0) b=X(a0 c0 d3 c1) c=X(b1 b3 e3 f0) d=X(f3 f2 e1 b2) e=X(g0 d2 f1 c2) f=X(c3 e2 d1 d0) g=V(e0) ['name'=1]"),
        kp.from_knotpy_notation("a=V(b0) b=V(a0) ['name'=2]"),
        kp.from_knotpy_notation("a=V(b3) b=X(c3 d0 c0 a0) c=X(b2 e0 e3 b0) d=X(b1 f0 f3 g0) e=X(c1 f2 f1 c2) f=X(d1 e2 e1 d2) g=V(d3) ['name'=3]"),
        kp.from_knotpy_notation("a=V(b0) b=X(a0 c0 c3 d0) c=X(b1 e0 d1 b2) d=X(b3 c2 f3 e1) e=X(c1 d3 f1 f0) f=X(e3 e2 g0 d2) g=V(f2) ['name'=4]")
    ]

    table = {
        str(k.name): {"diagram": k, "affine": kp.affine_index_polynomial(k)}
        for k in diagrams
    }

    kp.save_invariant_table(filename=_unique + "_writer_reader_name2.txt", table=table)
    loaded = kp.load_invariant_table(filename=_unique + "_writer_reader_name2.txt")
    assert loaded == table

    _safe_delete_file(_unique + "_writer_reader_name2.txt")



if __name__ == "__main__":
    test_writer_table_diagram()
    test_writer_table_name()
    test_writer_dict_diagram()
    test_writer_dict_name()