import knotpy as kp

from knotpy.tables.tests._helper import _safe_delete_file, _unique

def test_export():
    s = """
    a=V(b0) b=X(a0 c3 d3 c0) c=X(b3 d2 d1 b1) d=X(e0 c2 c1 b2) e=X(d0 f0 f3 g3) f=X(e1 g2 g0 e2) g=X(f2 h0 f1 e3) h=V(g1)
    a=V(b0) b=X(a0 c0 c3 d3) c=X(b1 e3 e1 b2) d=X(f3 g0 e0 b3) e=X(d2 c2 h0 c1) f=X(i3 i2 g1 d0) g=X(d1 f2 i1 i0) h=V(e2) i=X(g3 g2 f1 f0)
    a=V(b0) b=X(a0 c3 d3 c0) c=X(b3 e0 e3 b1) d=X(f0 g3 h0 b2) e=X(c1 f2 f1 c2) f=X(d0 e2 e1 i0) g=X(j3 j2 h1 d1) h=X(d2 g2 j1 j0) i=V(f3) j=X(h3 h2 g1 g0)
    a=V(b3) b=X(c0 d0 d3 a0) c=X(b0 e3 f0 g3) d=X(b1 e2 e0 b2) e=X(d2 h0 d1 c1) f=X(c2 g2 i3 i2) g=X(i1 i0 f1 c3) h=V(e1) i=X(g1 g0 f3 f2)
    a=V(b0) b=X(a0 c3 d3 c0) c=X(b3 e0 e3 b1) d=X(f0 g0 h3 b2) e=X(c1 f2 f1 c2) f=X(d0 e2 e1 i0) g=X(d1 h2 j3 j2) h=X(j1 j0 g1 d2) i=V(f3) j=X(h1 h0 g3 g2)
    a=V(b0) b=X(a0 c3 d3 c0) c=X(b3 e0 e3 b1) d=X(f3 g3 h0 b2) e=X(c1 i0 i3 c2) f=X(i2 h3 g0 d0) g=X(f2 h2 h1 d1) h=X(d2 g2 g1 f1) i=X(e1 j0 f0 e2) j=V(i1)
    a=V(b0) b=X(a0 c0 c3 d0) c=X(b1 e3 e1 b2) d=X(b3 e0 f0 g3) e=X(d1 c2 h0 c1) f=X(d2 g2 i3 i2) g=X(i1 i0 f1 d3) h=V(e2) i=X(g1 g0 f3 f2)
    a=V(b0) b=X(a0 c3 d0 c0) c=X(b3 e0 e3 b1) d=X(b2 f3 g0 h0) e=X(c1 i0 i3 c2) f=X(h2 g2 g1 d1) g=X(d2 f2 f1 h1) h=X(d3 g3 f0 i2) i=X(e1 j0 h3 e2) j=V(i1)
    a=V(b3) b=X(c0 d0 d3 a0) c=X(b0 e3 f3 g0) d=X(b1 e2 e0 b2) e=X(d2 h0 d1 c1) f=X(i3 i2 g1 c2) g=X(c3 f2 i1 i0) h=V(e1) i=X(g3 g2 f1 f0)
    a=V(b0) b=X(a0 c0 c3 d3) c=X(b1 e3 e1 b2) d=X(f0 g3 e0 b3) e=X(d2 c2 h0 c1) f=X(d0 g2 i3 i2) g=X(i1 i0 f1 d1) h=V(e2) i=X(g1 g0 f3 f2)
    a=V(b3) b=X(c3 d0 c0 a0) c=X(b2 e0 e3 b0) d=X(b1 f3 g0 e2) e=X(c1 h0 d3 c2) f=X(i3 i2 g1 d1) g=X(d2 f2 i1 i0) h=V(e1) i=X(g3 g2 f1 f0)
    a=V(b3) b=X(c3 d0 c0 a0) c=X(b2 e0 e3 b0) d=X(b1 f0 g3 e2) e=X(c1 h0 d3 c2) f=X(d1 g2 i3 i2) g=X(i1 i0 f1 d2) h=V(e1) i=X(g1 g0 f3 f2)
    a=V(b0) b=X(a0 c0 c3 d0) c=X(b1 e3 e1 b2) d=X(b3 e0 f3 g0) e=X(d1 c2 h0 c1) f=X(i3 i2 g1 d2) g=X(d3 f2 i1 i0) h=V(e2) i=X(g3 g2 f1 f0)
    a=V(b0) b=X(a0 c3 d0 c0) c=X(b3 e0 e3 b1) d=X(b2 f3 g0 h0) e=X(c1 h2 h1 c2) f=X(i3 i2 g1 d1) g=X(d2 f2 i1 i0) h=X(d3 e2 e1 j0) i=X(g3 g2 f1 f0) j=V(h3)
    a=V(b0) b=X(a0 c3 d0 c0) c=X(b3 e0 e3 b1) d=X(b2 f0 g3 h0) e=X(c1 h2 h1 c2) f=X(d1 g2 i3 i2) g=X(i1 i0 f1 d2) h=X(d3 e2 e1 j0) i=X(g1 g0 f3 f2) j=V(h3)
    a=V(b3) b=X(c3 d0 c0 a0) c=X(b2 e0 e3 b0) d=X(b1 f3 g0 h0) e=X(c1 i0 h3 c2) f=X(h2 g2 g1 d1) g=X(d2 f2 f1 h1) h=X(d3 g3 f0 e2) i=V(e1)
    """

    s = s.strip().splitlines()
    k = [kp.from_knotpy_notation(_) for _ in s]

    kp.export_pdf(k, _unique + "_export.pdf")
    _safe_delete_file(_unique + "_export.pdf")

    kp.export_pdf_groups([[k[0], k[1], k[3]], [k[4], k[5], k[6]]], _unique + "_export_group.pdf")
    _safe_delete_file(_unique + "_export_group.pdf")



if __name__ == "__main__":
    test_export()