import os

import matplotlib.pyplot as plt
from knotpy import to_knotpy_notation
from knotpy.drawing.save import export_pdf
from knotpy.drawing.draw import draw
from knotpy.notation.pd import from_pd_notation
from knotpy.notation.native import from_knotpy_notation
from knotpy.algorithms.canonical import canonical

from knotpy.tables.tests._helper import _safe_delete_file, _unique

def test_draw_knot():
    knots_and_links = [
        "a=X(b1 c0 c3 b2) b=X(c1 a0 a3 c2) c=X(a1 b0 b3 a2) ['name'='3_1']",
        "a=X(c3 d0 b3 b2) b=X(d3 c0 a3 a2) c=X(b1 d2 d1 a0) d=X(a1 c2 c1 b0) ['name'='4_1']",
        "a=X(c1 d0 d3 c2) b=X(d1 e0 e3 d2) c=X(e1 a0 a3 e2) d=X(a1 b0 b3 a2) e=X(b1 c0 c3 b2) ['name'='5_1']",
        "a=X(c1 c0 d3 b2) b=X(d1 e0 a3 d2) c=X(a1 a0 e3 e2) d=X(e1 b0 b3 a2) e=X(b1 d0 c3 c2) ['name'='5_2']",
        "a=X(d1 d0 c3 c2) b=X(c1 e2 e1 f0) c=X(e3 b0 a3 a2) d=X(a1 a0 f3 f2) e=X(f1 b2 b1 c0) f=X(b3 e0 d3 d2) ['name'='6_1']",
        "a=X(c1 d2 d1 e0) b=X(d3 f0 f3 e2) c=X(f1 a0 e3 f2) d=X(e1 a2 a1 b0) e=X(a3 d0 b3 c2) f=X(b1 c0 c3 b2) ['name'='6_2']",
        "a=X(b1 f0 d1 c2) b=X(f1 a0 c1 f2) c=X(e3 b2 a3 d0) d=X(c3 a2 e1 e0) e=X(d3 d2 f3 c0) f=X(a1 b0 b3 e2) ['name'='6_3']",
        # "a=X(d1 e0 e3 d2) b=X(e1 f0 f3 e2) c=X(f1 g0 g3 f2) d=X(g1 a0 a3 g2) e=X(a1 b0 b3 a2) f=X(b1 c0 c3 b2) g=X(c1 d0 d3 c2) ['name'='7_1']",
        # "a=X(d1 e0 g3 d2) b=X(g1 g0 f3 f2) c=X(f1 f0 e3 e2) d=X(e1 a0 a3 g2) e=X(a1 d0 c3 c2) f=X(c1 c0 b3 b2) g=X(b1 b0 d3 a2) ['name'='7_2']",
        "a=X(c1 e0 e3 d2) b=X(e1 f0 f3 e2) c=X(f1 a0 g3 g2) d=X(g1 g0 a3 f2) e=X(a1 b0 b3 a2) f=X(b1 c0 d3 b2) g=X(d1 d0 c3 c2) ['name'='7_3']",
        # "a=X(e1 e0 d3 d2) b=X(d1 f0 g3 e2) c=X(g1 g0 f3 f2) d=X(f1 b0 a3 a2) e=X(a1 a0 b3 g2) f=X(b1 d0 c3 c2) g=X(c1 c0 e3 b2) ['name'='7_4']",
        # "a=X(b1 e0 e3 d2) b=X(e1 a0 f3 g2) c=X(f1 g0 g3 f2) d=X(g1 f0 a3 e2) e=X(a1 b0 d3 a2) f=X(d1 c0 c3 b2) g=X(c1 d0 b3 c2) ['name'='7_5']",
        # "a=X(c1 g0 e3 f2) b=X(e1 e0 g3 d2) c=X(g1 a0 f1 g2) d=X(f3 e2 b3 f0) e=X(b1 b0 d1 a2) f=X(d3 c2 a3 d0) g=X(a1 c0 c3 b2) ['name'='7_6']",
        "a=X(c3 e2 e1 f0) b=X(e3 g0 d3 f2) c=X(d1 g2 g1 a0) d=X(g3 c0 f3 b2) e=X(f1 a2 a1 b0) f=X(a3 e0 b3 d2) g=X(b1 c2 c1 d0) ['name'='7_7']",
        "a=X(b3 b2 b1 b0) b=X(a3 a2 a1 a0) ['name'='L2a1{0}']",
        # "a=X(b1 b0 b3 b2) b=X(a1 a0 a3 a2) ['name'='L2a1{1}']",
        "a=X(c3 d2 d1 c0) b=X(d3 c2 c1 d0) c=X(a3 b2 b1 a0) d=X(b3 a2 a1 b0) ['name'='L4a1{0}']",
        # "a=X(d1 c0 c3 d2) b=X(c1 d0 d3 c2) c=X(a1 b0 b3 a2) d=X(b1 a0 a3 b2) ['name'='L4a1{1}']",
        "a=X(c3 c2 b1 d0) b=X(d1 a2 c1 e0) c=X(e1 b2 a1 a0) d=X(a3 b0 e3 e2) e=X(b3 c0 d3 d2) ['name'='L5a1{0}']",
        # "a=X(b3 d0 c3 c2) b=X(c1 e2 d1 a0) c=X(e3 b0 a3 a2) d=X(a1 b2 e1 e0) e=X(d3 d2 b1 c0) ['name'='L5a1{1}']",
        "a=X(e3 f2 c3 e0) b=X(f3 e2 d3 f0) c=X(d1 d0 e1 a2) d=X(c1 c0 f1 b2) e=X(a3 c2 b1 a0) f=X(b3 d2 a1 b0) ['name'='L6a1{0}']",
        # "a=X(c1 e0 e3 f2) b=X(d1 f0 f3 e2) c=X(e1 a0 d3 d2) d=X(f1 b0 c3 c2) e=X(a1 c0 b3 a2) f=X(b1 d0 a3 b2) ['name'='L6a1{1}']",
        "a=X(e3 f2 f1 e0) b=X(d3 d2 e1 f0) c=X(f3 e2 d1 d0) d=X(c3 c2 b1 b0) e=X(a3 b2 c1 a0) f=X(b3 a2 a1 c0) ['name'='L6a2{0}']",
        # "a=X(f1 e0 e3 f2) b=X(e1 f0 d3 d2) c=X(d1 d0 f3 e2) d=X(c1 c0 b3 b2) e=X(a1 b0 c3 a2) f=X(b1 a0 a3 c2) ['name'='L6a2{1}']",
        "a=X(e3 e2 b1 b0) b=X(a3 a2 c1 c0) c=X(b3 b2 f1 f0) d=X(f3 f2 e1 e0) e=X(d3 d2 a1 a0) f=X(c3 c2 d1 d0) ['name'='L6a3{0}']",
        # "a=X(b1 b0 e3 e2) b=X(a1 a0 c3 c2) c=X(f1 f0 b3 b2) d=X(e1 e0 f3 f2) e=X(d1 d0 a3 a2) f=X(c1 c0 d3 d2) ['name'='L6a3{1}']",
        "a=X(d3 c2 b3 f0) b=X(c1 e0 f1 a2) c=X(e1 b0 a1 d2) d=X(f3 e2 c3 a0) e=X(b1 c0 d1 f2) f=X(a3 b2 e3 d0) ['name'='L6a4{0,0}']",
        # "a=X(b3 f0 d3 c2) b=X(c1 e2 f1 a0) c=X(e3 b0 a3 d2) d=X(f3 e0 c3 a2) e=X(d1 f2 b1 c0) f=X(a1 b2 e1 d0) ['name'='L6a4{1,0}']",
        # "a=X(d1 c2 b1 f0) b=X(f1 a2 c1 e0) c=X(e1 b2 a1 d0) d=X(c3 a0 f3 e2) e=X(b3 c0 d3 f2) f=X(a3 b0 e3 d2) ['name'='L6a4{0,1}']",
        # "a=X(b1 f0 d1 c2) b=X(f1 a0 c1 e2) c=X(e3 b2 a3 d0) d=X(c3 a2 f3 e0) e=X(d3 f2 b3 c0) f=X(a1 b0 e1 d2) ['name'='L6a4{1,1}']",
        "a=X(e3 f2 c1 e0) b=X(f3 e2 d1 f0) c=X(d3 a2 f1 d0) d=X(c3 b2 e1 c0) e=X(a3 d2 b1 a0) f=X(b3 c2 a1 b0) ['name'='L6a5{0,0}']",
        # "a=X(c1 e0 e3 f2) b=X(f3 e2 d3 f0) c=X(d1 a0 f1 d2) d=X(e1 c0 c3 b2) e=X(a1 d0 b1 a2) f=X(b3 c2 a3 b0) ['name'='L6a5{1,0}']",
        # "a=X(e3 f2 c3 e0) b=X(d1 f0 f3 e2) c=X(f1 d0 d3 a2) d=X(c1 b0 e1 c2) e=X(a3 d2 b3 a0) f=X(b1 c0 a1 b2) ['name'='L6a5{0,1}']",
        # "a=X(c3 e0 e3 f2) b=X(d3 f0 f3 e2) c=X(f1 d2 d1 a0) d=X(e1 c2 c1 b0) e=X(a1 d0 b3 a2) f=X(b1 c0 a3 b2) ['name'='L6a5{1,1}']",
    ]

    filename = _unique + "_draw_knots.pdf"

    knots = [from_knotpy_notation(code) for code in knots_and_links]

    # batch draw to PDF

    try:
        export_pdf(knots, filename)
    except Exception as e:
        assert False, f"Exporting PDF failed: {e}"


    assert os.path.exists(filename), f"File does not exist: {filename}"  # Check if file exists
    file_size = os.path.getsize(filename)  # Check if file is larger than 10 KB (10 * 1024 bytes)
    assert file_size > 10 * 1024, f"File is too small: {file_size} bytes"
    #os.remove(filename)  # Remove the file

    # batch draw to PNG

    _safe_delete_file(filename)


def test_draw_theta():

    theta_curves = [
        "a=V(b0 b2 b1) b=V(a0 a2 a1) ['name'='t0_1']",
        "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 e1 d0) d=X(c3 e0 b1 a2) e=X(d1 c2 c1 b2) ['name'='+t3_1']",
        "a=V(b0 c0 d3) b=X(a0 d2 e3 c1) c=V(a1 b3 e2) d=X(e1 e0 b1 a2) e=X(d1 d0 c2 b2) ['name'='-t3_1']",
        "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 e3 f0) d=X(f3 e0 b1 a2) e=X(d1 f2 f1 c2) f=X(c3 e2 e1 d0) ['name'='t4_1.1']",
        # "a=V(b0 c0 d3) b=X(a0 e0 f3 c1) c=V(a1 b3 d0) d=X(c2 f2 e1 a2) e=X(b1 d2 f1 f0) f=X(e3 e2 d1 b2) ['name'='t4_1.2']",
        "a=V(b0 c0 d3) b=X(a0 e0 e3 f0) c=X(a1 f2 g3 d0) d=X(c3 g2 e1 a2) e=X(b1 d2 g1 b2) f=V(b3 g0 c1) g=X(f1 e2 d1 c2) ['name'='t5_1.1']",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=X(a1 f2 g3 g2) d=X(g1 e0 b1 a2) e=X(d1 g0 f1 b2) f=V(b3 e2 c1) g=X(e1 d0 c3 c2) ['name'='t5_1.2']",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=X(a1 e1 f3 f2) d=X(f1 g0 b1 a2) e=X(g2 c1 b3 b2) f=X(g1 d0 c3 c2) g=V(d1 f0 e0) ['name'='+t5_2']",
        # "a=V(b0 c3 d3) b=X(a0 e0 f0 c0) c=X(b3 g0 g3 a1) d=X(g2 e2 e1 a2) e=X(b1 d2 d1 f1) f=V(b2 e3 g1) g=X(c1 f2 d0 c2) ['name'='-t5_2']",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 d0) d=X(c2 f0 f3 a2) e=X(b1 g0 g3 b2) f=X(d1 g2 g1 d2) g=X(e1 f2 f1 e2) ['name'='+t5_3']",
        # "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 e3 e2) d=X(f3 f2 b1 a2) e=X(g3 g2 c3 c2) f=X(g1 g0 d1 d0) g=X(f1 f0 e1 e0) ['name'='-t5_3']",
        "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 f1 d0) d=X(c3 g0 g3 a2) e=X(b1 g2 g1 f0) f=X(e3 c2 c1 b2) g=X(d1 e2 e1 d2) ['name'='+t5_4']",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=V(a1 e1 f0) d=X(g3 g2 b1 a2) e=X(f1 c1 b3 b2) f=X(c2 e0 g1 g0) g=X(f3 f2 d1 d0) ['name'='-t5_4']",
        # "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 e3 e2) d=X(f3 g0 b1 a2) e=X(g3 f0 c3 c2) f=X(e1 g2 g1 d0) g=X(d1 f2 f1 e0) ['name'='+t5_5']",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 d0) d=X(c2 f0 g3 a2) e=X(b1 g2 f1 b2) f=X(d1 e2 g1 g0) g=X(f3 f2 e1 d2) ['name'='-t5_5']",
        # "a=V(b0 c0 d3) b=V(a0 e0 c1) c=X(a1 b2 f3 d0) d=X(c3 f2 e1 a2) e=X(b1 d2 g3 g2) f=X(g1 g0 d1 c2) g=X(f1 f0 e3 e2) ['name'='+t5_6']",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=V(a1 f3 d0) d=X(c2 e0 b1 a2) e=X(d1 g0 g3 b2) f=X(b3 g2 g1 c1) g=X(e1 f2 f1 e2) ['name'='-t5_6']",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=V(a1 f3 g0) d=X(g3 g2 b1 a2) e=X(g1 f2 f1 b2) f=X(b3 e2 e1 c1) g=X(c2 e0 d1 d0) ['name'='+t5_7']",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 f1 d0) d=X(c3 g0 e1 a2) e=X(b1 d2 g3 g2) f=X(g1 c2 c1 b2) g=X(d1 f0 e3 e2) ['name'='-t5_7']",
        # "a=V(b0 c3 d3) b=X(a0 d2 e3 f0) c=X(f2 g0 g3 a1) d=X(g2 e0 b1 a2) e=X(d1 h0 h3 b2) f=V(b3 h2 c0) g=X(c1 h1 d0 c2) h=X(e1 g1 f1 e2) ['name'='t6_1.1']",
        # "a=V(b0 c0 d3) b=X(a0 e0 f3 f2) c=X(a1 f1 g3 d0) d=X(c3 g2 e1 a2) e=V(b1 d2 h3) f=X(h2 c1 b3 b2) g=X(h1 h0 d1 c2) h=X(g1 g0 f0 e2) ['name'='t6_1.2']",
        "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 e0 e3 d0) d=X(c3 e2 e1 b1) e=X(c1 d2 d1 c2) ['name'='t0_1#+3_1']",
        # "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 d2 e3 e2) d=X(e1 e0 c1 b1) e=X(d1 d0 c3 c2) ['name'='t0_1#-3_1']",
        "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 e0 f3 d0) d=X(c3 f2 e1 b1) e=X(c1 d2 f1 f0) f=X(e3 e2 d1 c2) ['name'='t0_1#4_1']",
        "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 e0 e3 d0) d=X(c3 f0 f3 b1) e=X(c1 g0 g3 c2) f=X(d1 g2 g1 d2) g=X(e1 f2 f1 e2) ['name'='t0_1#+5_1']",
        # "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 d2 e3 e2) d=X(f3 f2 c1 b1) e=X(g3 g2 c3 c2) f=X(g1 g0 d1 d0) g=X(f1 f0 e1 e0) ['name'='t0_1#-5_1']",
        # "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 e0 f3 f2) d=X(f1 g0 g3 b1) e=X(c1 g2 g1 f0) f=X(e3 d0 c3 c2) g=X(d1 e2 e1 d2) ['name'='t0_1#+5_2']",
        # "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 e0 f3 f2) d=X(g3 e2 e1 b1) e=X(c1 d2 d1 g2) f=X(g1 g0 c3 c2) g=X(f1 f0 e3 d0) ['name'='t0_1#-5_2']",
        "a=V(a1 a0 b0) b=V(a2 b2 b1) ['name'='h0_1']",
        "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2) ['name'='h2_1.1']",
        # "a=V(b0 c0 d3) b=X(a0 d2 d1 c1) c=V(a1 b3 d0) d=X(c2 b2 b1 a2) ['name'='h2_1.2']",
        "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 e3 e2) d=X(f3 f2 b1 a2) e=X(f1 f0 c3 c2) f=X(e1 e0 d1 d0) ['name'='h4_1.1']",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 d0) d=X(c2 f0 f3 a2) e=X(b1 f2 f1 b2) f=X(d1 e2 e1 d2) ['name'='h4_1.2']",
        "a=V(b0 c0 d3) b=X(a0 d2 e3 c1) c=V(a1 b3 f0) d=X(g3 e0 b1 a2) e=X(d1 g2 f1 b2) f=X(c2 e2 g1 g0) g=X(f3 f2 e1 d0) ['name'='h5_1.1']",
        # "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 f0 g3 d0) d=X(c3 g2 b1 a2) e=X(g1 f2 f1 b2) f=X(c1 e2 e1 g0) g=X(f3 e0 d1 c2) ['name'='h5_1.2']",
        "a=V(b0 c0 d3) b=X(a0 e0 e3 f0) c=X(a1 f2 g3 g2) d=X(g1 h0 e1 a2) e=X(b1 d2 h3 b2) f=V(b3 h2 c1) g=X(h1 d0 c3 c2) h=X(d1 g0 f1 e2) ['name'='h6_1']",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=X(a1 f0 f3 g0) d=X(g2 h0 b1 a2) e=X(h3 f1 b3 b2) f=X(c1 e1 h2 c2) g=V(c3 h1 d0) h=X(d1 g1 f2 e0) ['name'='h6_2.1']",
        # "a=V(b0 c0 d3) b=X(a0 e0 f3 f2) c=X(a1 f1 g3 d0) d=X(c3 h0 e1 a2) e=V(b1 d2 h3) f=X(g0 c1 b3 b2) g=X(f0 h2 h1 c2) h=X(d1 g2 g1 e2) ['name'='h6_2.2']",
    ]
    filename = _unique + "_draw_thetas.pdf"
    thetas = [from_knotpy_notation(code) for code in theta_curves]

    # batch draw to PDF

    try:
        export_pdf(thetas, filename)
    except Exception as e:
        assert False, f"Exporting PDF failed: {e}"

    assert os.path.exists(filename), f"File does not exist: {filename}"  # Check if file exists
    file_size = os.path.getsize(filename)
    assert file_size > 10 * 1024, f"File is too small: {file_size} bytes"  # Check if file is larger than 10 KB (10 * 1024 bytes)

    _safe_delete_file(filename)



def DO_NOTtest_draw_bridges():
    graph_with_bridge = from_pd_notation("[[0,1,2],[0,3,4],[5,6,7,2],[1,7,6,5],[4,8,9,10],[8,3,10,9]]")
    print(graph_with_bridge)


def test_draw_bonded():
    bonded_knots = [
        "a=X(b0 b3 c3 d3) b=X(a0 d2 e0 a1) c=X(e3 e2 d0 a2) d=X(c2 e1 b1 a3) e=X(b2 d1 c1 c0)",
        "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 e1 d0) d=X(c3 e0 b1 a2) e=X(d1 c2 c1 b2)",
        "a=V(b0 c0 d0) b=X(a0 d3 e0 c1) c=X(a1 b3 e2 d1) d=X(a2 c3 e1 b1) e=V(b2 d2 c2)",
        # "a=X(b0 b3 c0 d0) b=X(a0 e0 c1 a1) c=X(a2 b2 e3 d1) d=X(a3 c3 e2 e1) e=X(b1 d3 d2 c2)",
        "a=V(b0 c0 d3) b=V(a0 e3 c1) c=X(a1 b2 e2 d0) d=X(c3 e1 e0 a2) e=X(d2 d1 c2 b1)",
        # "a=V(b0 c0 d0) b=V(a0 d3 e0) c=V(a1 e2 d1) d=X(a2 c2 e1 b1) e=V(b2 d2 c1)",
        "a=V(b0 c0 d3) b=V(a0 e3 c1) c=X(a1 b2 e2 d0) d=X(c3 f3 f2 a2) e=X(f1 f0 c2 b1) f=X(e1 e0 d2 d1)",
        "a=V(b0 c0 d0) b=V(a0 e0 c1) c=X(a1 b2 f3 f2) d=V(a2 f1 e1) e=V(b1 d2 f0) f=X(e2 d1 c3 c2)",
        # "a=V(b0 c3 d3) b=V(a0 e3 f3) c=X(f2 f1 d0 a1) d=X(c2 e1 e0 a2) e=X(d2 d1 f0 b1) f=X(e2 c1 c0 b2)",
        # "a=V(b0 c0 d0) b=V(a0 e3 c1) c=X(a1 b2 e2 d1) d=X(a2 c3 f0 f3) e=X(f2 f1 c2 b1) f=X(d2 e1 e0 d3)",
        "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 f0 f3 d0) d=X(c3 e0 b1 a2) e=X(d1 f2 f1 b2) f=X(c1 e2 e1 c2)",
        "a=V(b0 c0 d0) b=V(a0 d2 e0) c=V(a1 e2 f0) d=V(a2 f2 b1) e=V(b2 f1 c1) f=V(c2 e1 d1)",
        "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 f3 d0) d=X(c3 g0 b1 a2) e=X(g3 f0 c1 b2) f=X(e1 g2 g1 c2) g=X(d1 f2 f1 e0)",
        # "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 f0 f3 g0) d=X(g3 e0 b1 a2) e=X(d1 g2 f1 b2) f=X(c1 e2 g1 c2) g=X(c3 f2 e1 d0)",
        "a=V(b0 c0 d0) b=V(a0 d2 e0) c=X(a1 e2 f3 g0) d=V(a2 g3 b1) e=V(b2 f0 c1) f=X(e1 g2 g1 c2) g=X(c3 f2 f1 d1)",
        "a=V(b0 c0 d0) b=V(a0 d3 e0) c=V(a1 e2 f0) d=X(a2 f2 g0 b1) e=V(b2 g2 c1) f=V(c2 g1 d1) g=V(d2 f1 e1)",
        # "a=V(b0 c0 d0) b=V(a0 d3 e0) c=V(a1 e2 f3) d=X(a2 f2 g3 b1) e=V(b2 g2 c1) f=X(g1 g0 d1 c2) g=X(f1 f0 e1 d2)",
        # "a=V(b0 c0 d3) b=X(a0 e0 f3 g0) c=X(a1 g2 d1 d0) d=X(c3 c2 e1 a2) e=X(b1 d2 f1 f0) f=X(e3 e2 g1 b2) g=V(b3 f2 c1)",
        # "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 e1 f0) d=X(g3 g2 b1 a2) e=X(f1 c2 c1 b2) f=X(c3 e0 g1 g0) g=X(f3 f2 d1 d0)",
        "a=V(b0 c0 d0) b=V(a0 d3 e3) c=V(a1 f0 g3) d=X(a2 g2 g1 b1) e=X(h3 h2 f1 b2) f=V(c1 e2 h1) g=X(h0 d2 d1 c2) h=X(g0 f2 e1 e0)",
        # "a=V(b0 c0 d0) b=V(a0 e0 c1) c=X(a1 b2 f3 f2) d=V(a2 g0 e1) e=V(b1 d2 h0) f=X(h2 g1 c3 c2) g=V(d1 f1 h1) h=V(e2 g2 f0)",
        "a=V(b0 c0 d0) b=V(a0 d3 e0) c=V(a1 e2 f0) d=X(a2 f3 g0 b1) e=V(b2 g3 c1) f=X(c2 h0 h3 d1) g=X(d2 h2 h1 e1) h=X(f1 g2 g1 f2)",
        # "a=V(b0 c0 d0) b=V(a0 d2 e0) c=V(a1 e2 f0) d=V(a2 g0 b1) e=V(b2 h0 c1) f=V(c2 h2 g1) g=V(d1 f2 h1) h=V(e1 g2 f1)",
        # "a=V(b0 c0 d0) b=V(a0 e0 c1) c=X(a1 b2 f3 f2) d=X(a2 g3 g2 h0) e=V(b1 h3 i0) f=X(i2 g0 c3 c2) g=X(f1 h1 d2 d1) h=X(d3 g1 i1 e1) i=V(e2 h2 f0)",
        # "a=V(b0 c0 d3) b=V(a0 e0 f0) c=V(a1 f2 g3) d=X(g2 e2 e1 a2) e=X(b1 d2 d1 h0) f=V(b2 i0 c1) g=X(i2 h1 d0 c2) h=V(e3 g1 i1) i=V(f1 h2 g0)",
        # "a=V(b0 c3 d3) b=V(a0 e0 f0) c=X(f2 d1 d0 a1) d=X(c2 c1 e1 a2) e=X(b1 d2 g0 h0) f=V(b2 i0 c0) g=V(e2 i2 h1) h=V(e3 g2 i1) i=V(f1 h2 g1)",
        "a=V(b0 c0 d0) b=V(a0 e3 c1) c=X(a1 b2 e2 f0) d=V(a2 f3 g0) e=X(g3 h0 c2 b1) f=X(c3 i0 i3 d1) g=X(d2 i2 h1 e0) h=V(e1 g2 i1) i=X(f1 h2 g1 f2)",
        # "a=V(b0 c0 d3) b=X(a0 d2 e0 f0) c=V(a1 g0 d0) d=X(c2 e1 b1 a2) e=V(b2 d1 g3) f=V(b3 h0 i0) g=X(c1 i3 h1 e2) h=X(f1 g2 i2 i1) i=X(f2 h3 h2 g1)",
        # "a=V(b0 c0 d0) b=V(a0 e0 f0) c=X(a1 f2 g0 h0) d=V(a2 h3 e1) e=X(b1 d2 i3 i2) f=V(b2 j0 c1) g=V(c2 j2 h1) h=X(c3 g2 i0 d1) i=X(h2 j1 e3 e2) j=V(f1 i1 g1)",
        # "a=V(b0 c0 d3) b=V(a0 d2 e3) c=V(a1 e2 f0) d=X(g3 g2 b1 a2) e=X(h0 i0 c1 b2) f=V(c2 i3 j0) g=X(j2 h1 d1 d0) h=V(e0 g1 i1) i=X(e1 h2 j1 f1) j=V(f2 i2 g0)",
        # "a=V(b0 c0 d3) b=V(a0 e3 f0) c=V(a1 f2 d0) d=X(c2 g0 e0 a2) e=X(d2 h0 i0 b1) f=V(b2 j0 c1) g=V(d1 j2 h1) h=V(e1 g2 i1) i=V(e2 h2 j1) j=V(f1 i2 g1)",
        # "a=V(b0 c0 d0) b=V(a0 d2 e3) c=X(a1 e2 e1 f0) d=V(a2 g0 b1) e=X(h3 c2 c1 b2) f=V(c3 i0 g1) g=V(d1 f2 j0) h=X(j3 j2 i1 e0) i=V(f1 h2 j1) j=X(g2 i2 h1 h0)"
    ]

    bonded = [from_knotpy_notation(code) for code in bonded_knots]
    filename = _unique + "_draw_bonded.pdf"

    try:
        export_pdf(bonded, filename)
    except Exception as e:
        assert False, f"Exporting PDF failed: {e}"

    assert os.path.exists(filename), f"File does not exist: {filename}"  # Check if file exists
    file_size = os.path.getsize(filename)
    assert file_size > 10 * 1024, f"File is too small: {file_size} bytes"  # Check if file is larger than 10 KB (10 * 1024 bytes)

    _safe_delete_file(filename)

def test_thetas_sums():
    theta_codes = [
        "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 e0 f3 d0) d=X(c3 g0 e1 b1) e=X(c1 d2 g3 h0) f=X(h3 i0 i3 c2) g=X(d1 i2 h1 e2) h=X(e3 g2 i1 f0) i=X(f1 h2 g1 f2)",
        "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 g0 e3 d0) d=X(c3 e2 e1 a2) e=X(b1 d2 d1 c2) f=X(g3 h0 h3 b2) g=X(c1 h2 h1 f0) h=X(f1 g2 g1 f2)",
        # "a=V(b0 c0 d3) b=V(a0 e0 c1) c=X(a1 b2 f3 d0) d=X(c3 e2 e1 a2) e=X(b1 d2 d1 g0) f=X(h3 h2 i3 c2) g=X(e3 i2 i1 h0) h=X(g3 i0 f1 f0) i=X(h1 g2 g1 f2)",
        "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 g3 d0) d=X(c3 g2 g1 a2) e=X(b1 h0 h3 f0) f=X(e3 h2 c1 b2) g=X(h1 d2 d1 c2) h=X(e1 g0 f1 e2)",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 f0) c=V(a1 f3 g0) d=X(h3 e2 e1 a2) e=X(b1 d2 d1 b2) f=X(b3 i0 i3 c1) g=X(c2 i2 h1 h0) h=X(g3 g2 i1 d0) i=X(f1 h2 g1 f2)",
        # "a=V(b0 c3 d3) b=X(a0 e0 e3 c0) c=X(b3 f0 g0 a1) d=X(h3 e2 e1 a2) e=X(b1 d2 d1 b2) f=V(c1 h2 i3) g=X(c2 i2 i1 j0) h=X(j3 j2 f1 d0) i=X(j1 g2 g1 f2) j=X(g3 i0 h1 h0)",
        "a=V(b0 c0 d3) b=V(a0 e0 c1) c=X(a1 b2 e3 d0) d=X(c3 f0 f3 a2) e=X(b1 g3 h0 c2) f=X(d1 i0 i3 d2) g=X(i2 j0 j3 e1) h=X(e2 j2 j1 i1) i=X(f1 h3 g0 f2) j=X(g1 h2 h1 g2)",
        "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=X(a1 e1 f0 g0) d=X(g3 h0 b1 a2) e=X(i3 c1 b3 b2) f=V(c2 i2 g1) g=X(c3 f2 j3 d0) h=X(d1 j2 j1 i0) i=X(h3 j0 f1 e0) j=X(i1 h2 h1 g2)",
        # "a=V(b0 c0 d0) b=V(a0 e0 c1) c=X(a1 b2 f3 g3) d=X(a2 g2 h0 e1) e=X(b1 d3 i3 f0) f=X(e3 i2 j0 c2) g=X(j3 j2 d1 c3) h=X(d2 j1 k3 k2) i=X(k1 k0 f1 e2) j=X(f2 h1 g1 g0) k=X(i1 i0 h3 h2)",
        "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 g3 d0) d=X(c3 g2 e1 a2) e=X(b1 d2 h3 h2) f=X(i3 i2 c1 b2) g=X(i1 h0 d1 c2) h=X(g1 i0 e3 e2) i=X(h1 g0 f1 f0)",
        "a=V(b0 c0 d3) b=V(a0 e0 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 f3 a2) e=X(b1 g0 g3 f0) f=X(e3 g2 g1 d2) g=X(e1 f2 f1 e2)",
        # "a=V(b0 c3 d3) b=X(a0 d2 d1 e0) c=X(e2 f0 f3 a1) d=X(f2 b2 b1 a2) e=V(b3 f1 c0) f=X(c1 e1 d0 c2)",
        "a=V(b0 c0 d3) b=V(a0 e3 f0) c=X(a1 f3 d1 d0) d=X(c3 c2 e0 a2) e=X(d2 g0 g3 b1) f=X(b2 g2 g1 c1) g=X(e1 f2 f1 e2)",
        # "a=V(b0 c0 d3) b=X(a0 d2 d1 e0) c=V(a1 e3 f0) d=X(f3 b2 b1 a2) e=X(b3 g0 g3 c1) f=X(c2 g2 g1 d0) g=X(e1 f2 f1 e2)",
    ]

    thetas = [from_knotpy_notation(code) for code in theta_codes]
    filename = _unique + "_draw_thetas_complicated.pdf"

    try:
        export_pdf(thetas, filename)
    except Exception as e:
        assert False, f"Exporting PDF failed: {e}"

    assert os.path.exists(filename), f"File does not exist: {filename}"  # Check if file exists
    file_size = os.path.getsize(filename)
    assert file_size > 10 * 1024, f"File is too small: {file_size} bytes"  # Check if file is larger than 10 KB (10 * 1024 bytes)

    _safe_delete_file(filename)

def test_draw_knotoid():
    knotoid_codes = [
        "a=V(b0) b=X(a0 c3 d3 c0) c=X(b3 d2 e3 b1) d=X(f3 e0 c1 b2) e=X(d1 f2 f0 c2) f=X(e2 g0 e1 d0) g=V(f1) ['name'='26']",
        "a=V(b0) b=X(a0 c0 c3 d3) c=X(b1 d2 e3 b2) d=X(e2 f0 c1 b3) e=X(g3 g2 d0 c2) f=X(d1 g1 h0 g0) g=X(f3 f1 e1 e0) h=V(f2) ['name'='31']",
        "a=V(b0) b=X(a0 c0 c3 d0) c=X(b1 e0 d1 b2) d=X(b3 c2 e3 f0) e=X(c1 g0 f1 d2) f=X(d3 e2 g3 g2) g=X(e1 h0 f3 f2) h=V(g1) ['name'='65']",
        "a=V(b0) b=X(a0 c0 d3 d2) c=X(b1 e0 f3 d0) d=X(c3 f2 b3 b2) e=X(c1 g0 h3 h2) f=X(h1 h0 d1 c2) g=V(e1) h=X(f1 f0 e3 e2) ['name'='66']",
        "a=V(b0) b=X(a0 c0 c3 d0) c=X(b1 e0 e3 b2) d=X(b3 f0 g3 h0) e=X(c1 g2 f1 c2) f=X(d1 e2 g1 g0) g=X(f3 f2 e1 d2) h=V(d3) ['name'='78']",
        "a=V(b0) b=X(a0 c0 c3 d3) c=X(b1 e0 f0 b2) d=X(f3 g0 e1 b3) e=X(c1 d2 h3 h2) f=X(c2 h1 g1 d0) g=X(d1 f2 i0 h0) h=X(g3 f1 e3 e2) i=V(g2) ['name'='360']",
        "a=V(b0) b=X(a0 c0 c3 d0) c=X(b1 d3 e0 b2) d=X(b3 e3 f0 c1) e=X(c2 f3 g3 d1) f=X(d2 h0 h3 e1) g=X(i0 j0 i3 e2) h=X(f1 i2 i1 f2) i=X(g0 h2 h1 g2) j=V(g1) ['name'='465']",
        # "a=V(b0) b=X(a0 c0 c3 d0) c=X(b1 d3 e3 b2) d=X(b3 f0 e0 c1) e=X(d2 f3 g3 c2) f=X(d1 h0 g0 e1) g=X(f2 i0 h1 e2) h=X(f1 g2 i3 i2) i=X(g1 j0 h3 h2) j=V(i1) ['name'='563']",
        # "a=V(b0) b=X(a0 c0 c3 d0) c=X(b1 e3 f0 b2) d=X(b3 f3 e1 e0) e=X(d3 d2 g0 c1) f=X(c2 g3 h3 d1) g=X(e2 h2 i0 f1) h=X(i3 i2 g1 f2) i=X(g2 j0 h1 h0) j=V(i1) ['name'='611']",
        # "a=V(b0) b=X(a0 c0 c3 d0) c=X(b1 e3 f3 b2) d=X(b3 g0 e1 e0) e=X(d3 d2 f0 c1) f=X(e2 h0 i3 c2) g=X(d1 i2 h1 j0) h=X(f1 g2 i1 i0) i=X(h3 h2 g1 f2) j=V(g3) ['name'='643']",
        # "a=V(b3) b=X(c0 d0 c1 a0) c=X(b0 b2 d3 e0) d=X(b1 f3 g3 c2) e=X(c3 g2 g1 h3) f=X(h2 i0 g0 d1) g=X(f2 e2 e1 d2) h=X(i3 i2 f0 e3) i=X(f1 j0 h1 h0) j=V(i1) ['name'='711']",
        # "a=V(b0) b=X(a0 c3 d3 c0) c=X(b3 d2 e3 b1) d=X(e2 f3 c1 b2) e=X(f2 g0 d0 c2) f=X(g3 h0 e0 d1) g=X(e1 i0 i3 f0) h=X(f1 i2 i1 j0) i=X(g1 h2 h1 g2) j=V(h3) ['name'='805']",
        # "a=V(b0) b=X(a0 c0 d0 c1) c=X(b1 b3 d3 e0) d=X(b2 f3 g3 c2) e=X(c3 g2 h3 f0) f=X(e3 h2 i0 d1) g=X(i3 h0 e1 d2) h=X(g1 i2 f1 e2) i=X(f2 j0 h1 g0) j=V(i1) ['name'='871']",
        # "a=V(b3) b=X(c3 d3 c0 a0) c=X(b2 d2 e3 b0) d=X(e2 f3 c1 b1) e=X(g0 h3 d0 c2) f=X(i3 g2 g1 d1) g=X(e0 f2 f1 h0) h=X(g3 i2 i0 e1) i=X(h2 j0 h1 f0) j=V(i1) ['name'='872']",
        "a=V(b0) b=X(a0 c3 d0 c0) c=X(b3 e3 f0 b1) d=X(b2 f3 e1 e0) e=X(d3 d2 g3 c1) f=X(c2 h0 g0 d1) g=X(f2 i0 i3 e2) h=X(f1 i2 j0 i1) i=X(g1 h3 h1 g2) j=V(h2) ['name'='874']",
        "a=V(b3) b=X(c0 d3 c1 a0) c=X(b0 b2 e0 f3) d=X(f2 e2 e1 b1) e=X(c2 d2 d1 g0) f=X(g3 h3 d0 c3) g=X(e3 h2 h1 f0) h=X(i0 g2 g1 f1) i=V(h0) ['name'='875']",
        "a=V(b3) b=X(c3 d0 c0 a0) c=X(b2 e0 d1 b0) d=X(b1 c2 f0 g3) e=X(c1 g2 h3 i3) f=X(d2 i2 i1 g0) g=X(f3 h0 e1 d3) h=X(g1 i0 j0 e2) i=X(h1 f2 f1 e3) j=V(h2) ['name'='941']",
        # "a=V(b3) b=X(c3 d0 c0 a0) c=X(b2 e0 d1 b0) d=X(b1 c2 f3 f2) e=X(c1 g0 g3 h0) f=X(i3 g1 d3 d2) g=X(e1 f1 i2 e2) h=X(e3 j0 i1 i0) i=X(h3 h2 g2 f0) j=V(h1) ['name'='943']",
        # "a=V(b0) b=X(a0 c3 d0 c0) c=X(b3 e0 e3 b1) d=X(b2 e2 f3 g3) e=X(c1 g2 d1 c2) f=X(g1 h0 h3 d2) g=X(i3 f0 e1 d3) h=X(f1 i2 i0 f2) i=X(h2 j0 h1 g0) j=V(i1) ['name'='948']",
        # "a=V(b0) b=X(a0 c0 c3 d3) c=X(b1 d2 e3 b2) d=X(e2 f0 c1 b3) e=X(g3 g2 d0 c2) f=X(d1 g1 h3 h2) g=X(i3 f1 e1 e0) h=X(i1 i0 f3 f2) i=X(h1 h0 j0 g0) j=V(i2) ['name'='955']",
        # "a=V(b0) b=X(a0 c3 d0 c0) c=X(b3 e3 f0 b1) d=X(b2 f3 g3 h0) e=X(h3 h2 f1 c1) f=X(c2 e2 i3 d1) g=X(i2 i0 h1 d2) h=X(d3 g2 e1 e0) i=X(g1 j0 g0 f2) j=V(i1) ['name'='965']",
        # "a=V(b0) b=X(a0 c3 d3 c0) c=X(b3 d2 e0 b1) d=X(f3 g3 c1 b2) e=X(c2 g2 g1 h3) f=X(i3 h0 g0 d0) g=X(f2 e2 e1 d1) h=X(f1 i2 i0 e3) i=X(h2 j0 h1 f0) j=V(i1) ['name'='967']",
        "a=V(b0) b=X(a0 c0 d0 c1) c=X(b1 b3 e3 e2) d=X(b2 e1 f3 g0) e=X(g3 d1 c3 c2) f=X(h3 i0 i3 d2) g=X(d3 i2 h0 e0) h=X(g2 j0 i1 f0) i=X(f1 h2 g1 f2) j=V(h1) ['name'='979']",
        "a=V(b0) b=X(a0 c3 d0 c0) c=X(b3 e0 e3 b1) d=X(b2 e2 f3 g0) e=X(c1 g3 d1 c2) f=X(h3 i0 i3 d2) g=X(d3 i2 h0 e1) h=X(g2 j0 i1 f0) i=X(f1 h2 g1 f2) j=V(h1) ['name'='980']"
    ]

    knotoids = [from_knotpy_notation(code) for code in knotoid_codes]
    filename = _unique + "_draw_knotoid.pdf"

    try:
        export_pdf(knotoids, filename)
    except Exception as e:
        assert False, f"Exporting PDF failed: {e}"

    assert os.path.exists(filename), f"File does not exist: {filename}"  # Check if file exists
    file_size = os.path.getsize(filename)
    assert file_size > 10 * 1024, f"File is too small: {file_size} bytes"  # Check if file is larger than 10 KB (10 * 1024 bytes)
    # os.remove(filename)   # Remove the file
    _safe_delete_file(filename)

if __name__ == "__main__":

    test_draw_knot()
    test_draw_theta()
    test_draw_bonded()
    test_thetas_sums()
    test_draw_knotoid()
