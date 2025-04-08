import os

from knotpy.drawing.draw_matplotlib import export_pdf, draw, plt
from knotpy.notation.pd import from_pd_notation
from knotpy.notation.native import from_knotpy_notation

def test_draw_knot():
    knots_and_links = [
        "a=X(b1 c0 c3 b2) b=X(c1 a0 a3 c2) c=X(a1 b0 b3 a2) ['name'='3_1']",
        "a=X(c3 d0 b3 b2) b=X(d3 c0 a3 a2) c=X(b1 d2 d1 a0) d=X(a1 c2 c1 b0) ['name'='4_1']",
        "a=X(c1 d0 d3 c2) b=X(d1 e0 e3 d2) c=X(e1 a0 a3 e2) d=X(a1 b0 b3 a2) e=X(b1 c0 c3 b2) ['name'='5_1']",
        "a=X(c1 c0 d3 b2) b=X(d1 e0 a3 d2) c=X(a1 a0 e3 e2) d=X(e1 b0 b3 a2) e=X(b1 d0 c3 c2) ['name'='5_2']",
        "a=X(d1 d0 c3 c2) b=X(c1 e2 e1 f0) c=X(e3 b0 a3 a2) d=X(a1 a0 f3 f2) e=X(f1 b2 b1 c0) f=X(b3 e0 d3 d2) ['name'='6_1']",
        "a=X(c1 d2 d1 e0) b=X(d3 f0 f3 e2) c=X(f1 a0 e3 f2) d=X(e1 a2 a1 b0) e=X(a3 d0 b3 c2) f=X(b1 c0 c3 b2) ['name'='6_2']",
        "a=X(b1 f0 d1 c2) b=X(f1 a0 c1 f2) c=X(e3 b2 a3 d0) d=X(c3 a2 e1 e0) e=X(d3 d2 f3 c0) f=X(a1 b0 b3 e2) ['name'='6_3']",
        "a=X(d1 e0 e3 d2) b=X(e1 f0 f3 e2) c=X(f1 g0 g3 f2) d=X(g1 a0 a3 g2) e=X(a1 b0 b3 a2) f=X(b1 c0 c3 b2) g=X(c1 d0 d3 c2) ['name'='7_1']",
        "a=X(d1 e0 g3 d2) b=X(g1 g0 f3 f2) c=X(f1 f0 e3 e2) d=X(e1 a0 a3 g2) e=X(a1 d0 c3 c2) f=X(c1 c0 b3 b2) g=X(b1 b0 d3 a2) ['name'='7_2']",
        "a=X(c1 e0 e3 d2) b=X(e1 f0 f3 e2) c=X(f1 a0 g3 g2) d=X(g1 g0 a3 f2) e=X(a1 b0 b3 a2) f=X(b1 c0 d3 b2) g=X(d1 d0 c3 c2) ['name'='7_3']",
        "a=X(e1 e0 d3 d2) b=X(d1 f0 g3 e2) c=X(g1 g0 f3 f2) d=X(f1 b0 a3 a2) e=X(a1 a0 b3 g2) f=X(b1 d0 c3 c2) g=X(c1 c0 e3 b2) ['name'='7_4']",
        "a=X(b1 e0 e3 d2) b=X(e1 a0 f3 g2) c=X(f1 g0 g3 f2) d=X(g1 f0 a3 e2) e=X(a1 b0 d3 a2) f=X(d1 c0 c3 b2) g=X(c1 d0 b3 c2) ['name'='7_5']",
        "a=X(c1 g0 e3 f2) b=X(e1 e0 g3 d2) c=X(g1 a0 f1 g2) d=X(f3 e2 b3 f0) e=X(b1 b0 d1 a2) f=X(d3 c2 a3 d0) g=X(a1 c0 c3 b2) ['name'='7_6']",
        "a=X(c3 e2 e1 f0) b=X(e3 g0 d3 f2) c=X(d1 g2 g1 a0) d=X(g3 c0 f3 b2) e=X(f1 a2 a1 b0) f=X(a3 e0 b3 d2) g=X(b1 c2 c1 d0) ['name'='7_7']",
        "a=X(b3 b2 b1 b0) b=X(a3 a2 a1 a0) ['name'='L2a1{0}']",
        "a=X(b1 b0 b3 b2) b=X(a1 a0 a3 a2) ['name'='L2a1{1}']",
        "a=X(c3 d2 d1 c0) b=X(d3 c2 c1 d0) c=X(a3 b2 b1 a0) d=X(b3 a2 a1 b0) ['name'='L4a1{0}']",
        "a=X(d1 c0 c3 d2) b=X(c1 d0 d3 c2) c=X(a1 b0 b3 a2) d=X(b1 a0 a3 b2) ['name'='L4a1{1}']",
        "a=X(c3 c2 b1 d0) b=X(d1 a2 c1 e0) c=X(e1 b2 a1 a0) d=X(a3 b0 e3 e2) e=X(b3 c0 d3 d2) ['name'='L5a1{0}']",
        "a=X(b3 d0 c3 c2) b=X(c1 e2 d1 a0) c=X(e3 b0 a3 a2) d=X(a1 b2 e1 e0) e=X(d3 d2 b1 c0) ['name'='L5a1{1}']",
        "a=X(e3 f2 c3 e0) b=X(f3 e2 d3 f0) c=X(d1 d0 e1 a2) d=X(c1 c0 f1 b2) e=X(a3 c2 b1 a0) f=X(b3 d2 a1 b0) ['name'='L6a1{0}']",
        "a=X(c1 e0 e3 f2) b=X(d1 f0 f3 e2) c=X(e1 a0 d3 d2) d=X(f1 b0 c3 c2) e=X(a1 c0 b3 a2) f=X(b1 d0 a3 b2) ['name'='L6a1{1}']",
        "a=X(e3 f2 f1 e0) b=X(d3 d2 e1 f0) c=X(f3 e2 d1 d0) d=X(c3 c2 b1 b0) e=X(a3 b2 c1 a0) f=X(b3 a2 a1 c0) ['name'='L6a2{0}']",
        "a=X(f1 e0 e3 f2) b=X(e1 f0 d3 d2) c=X(d1 d0 f3 e2) d=X(c1 c0 b3 b2) e=X(a1 b0 c3 a2) f=X(b1 a0 a3 c2) ['name'='L6a2{1}']",
        "a=X(e3 e2 b1 b0) b=X(a3 a2 c1 c0) c=X(b3 b2 f1 f0) d=X(f3 f2 e1 e0) e=X(d3 d2 a1 a0) f=X(c3 c2 d1 d0) ['name'='L6a3{0}']",
        "a=X(b1 b0 e3 e2) b=X(a1 a0 c3 c2) c=X(f1 f0 b3 b2) d=X(e1 e0 f3 f2) e=X(d1 d0 a3 a2) f=X(c1 c0 d3 d2) ['name'='L6a3{1}']",
        "a=X(d3 c2 b3 f0) b=X(c1 e0 f1 a2) c=X(e1 b0 a1 d2) d=X(f3 e2 c3 a0) e=X(b1 c0 d1 f2) f=X(a3 b2 e3 d0) ['name'='L6a4{0,0}']",
        "a=X(b3 f0 d3 c2) b=X(c1 e2 f1 a0) c=X(e3 b0 a3 d2) d=X(f3 e0 c3 a2) e=X(d1 f2 b1 c0) f=X(a1 b2 e1 d0) ['name'='L6a4{1,0}']",
        "a=X(d1 c2 b1 f0) b=X(f1 a2 c1 e0) c=X(e1 b2 a1 d0) d=X(c3 a0 f3 e2) e=X(b3 c0 d3 f2) f=X(a3 b0 e3 d2) ['name'='L6a4{0,1}']",
        "a=X(b1 f0 d1 c2) b=X(f1 a0 c1 e2) c=X(e3 b2 a3 d0) d=X(c3 a2 f3 e0) e=X(d3 f2 b3 c0) f=X(a1 b0 e1 d2) ['name'='L6a4{1,1}']",
        "a=X(e3 f2 c1 e0) b=X(f3 e2 d1 f0) c=X(d3 a2 f1 d0) d=X(c3 b2 e1 c0) e=X(a3 d2 b1 a0) f=X(b3 c2 a1 b0) ['name'='L6a5{0,0}']",
        "a=X(c1 e0 e3 f2) b=X(f3 e2 d3 f0) c=X(d1 a0 f1 d2) d=X(e1 c0 c3 b2) e=X(a1 d0 b1 a2) f=X(b3 c2 a3 b0) ['name'='L6a5{1,0}']",
        "a=X(e3 f2 c3 e0) b=X(d1 f0 f3 e2) c=X(f1 d0 d3 a2) d=X(c1 b0 e1 c2) e=X(a3 d2 b3 a0) f=X(b1 c0 a1 b2) ['name'='L6a5{0,1}']",
        "a=X(c3 e0 e3 f2) b=X(d3 f0 f3 e2) c=X(f1 d2 d1 a0) d=X(e1 c2 c1 b0) e=X(a1 d0 b3 a2) f=X(b1 c0 a3 b2) ['name'='L6a5{1,1}']",
    ]

    filename = "_test_draw_knots.pdf"

    knots = [from_knotpy_notation(code) for code in knots_and_links]

    # batch draw to PDF

    try:
        export_pdf(knots, filename)
    except Exception as e:
        assert False, f"Exporting PDF failed: {e}"


    assert os.path.exists(filename), f"File does not exist: {filename}"  # Check if file exists
    file_size = os.path.getsize(filename)  # Check if file is larger than 10 KB (10 * 1024 bytes)
    assert file_size > 10 * 1024, f"File is too small: {file_size} bytes"
    os.remove(filename)  # Remove the file

    # batch draw to PNG


def test_draw_theta():

    theta_curves = [
        "a=V(b0 b2 b1) b=V(a0 a2 a1) ['name'='t0_1']",
        "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 e1 d0) d=X(c3 e0 b1 a2) e=X(d1 c2 c1 b2) ['name'='+t3_1']",
        "a=V(b0 c0 d3) b=X(a0 d2 e3 c1) c=V(a1 b3 e2) d=X(e1 e0 b1 a2) e=X(d1 d0 c2 b2) ['name'='-t3_1']",
        "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 e3 f0) d=X(f3 e0 b1 a2) e=X(d1 f2 f1 c2) f=X(c3 e2 e1 d0) ['name'='t4_1.1']",
        "a=V(b0 c0 d3) b=X(a0 e0 f3 c1) c=V(a1 b3 d0) d=X(c2 f2 e1 a2) e=X(b1 d2 f1 f0) f=X(e3 e2 d1 b2) ['name'='t4_1.2']",
        "a=V(b0 c0 d3) b=X(a0 e0 e3 f0) c=X(a1 f2 g3 d0) d=X(c3 g2 e1 a2) e=X(b1 d2 g1 b2) f=V(b3 g0 c1) g=X(f1 e2 d1 c2) ['name'='t5_1.1']",
        "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=X(a1 f2 g3 g2) d=X(g1 e0 b1 a2) e=X(d1 g0 f1 b2) f=V(b3 e2 c1) g=X(e1 d0 c3 c2) ['name'='t5_1.2']",
        "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=X(a1 e1 f3 f2) d=X(f1 g0 b1 a2) e=X(g2 c1 b3 b2) f=X(g1 d0 c3 c2) g=V(d1 f0 e0) ['name'='+t5_2']",
        "a=V(b0 c3 d3) b=X(a0 e0 f0 c0) c=X(b3 g0 g3 a1) d=X(g2 e2 e1 a2) e=X(b1 d2 d1 f1) f=V(b2 e3 g1) g=X(c1 f2 d0 c2) ['name'='-t5_2']",
        "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 d0) d=X(c2 f0 f3 a2) e=X(b1 g0 g3 b2) f=X(d1 g2 g1 d2) g=X(e1 f2 f1 e2) ['name'='+t5_3']",
        "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 e3 e2) d=X(f3 f2 b1 a2) e=X(g3 g2 c3 c2) f=X(g1 g0 d1 d0) g=X(f1 f0 e1 e0) ['name'='-t5_3']",
        "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 f1 d0) d=X(c3 g0 g3 a2) e=X(b1 g2 g1 f0) f=X(e3 c2 c1 b2) g=X(d1 e2 e1 d2) ['name'='+t5_4']",
        "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=V(a1 e1 f0) d=X(g3 g2 b1 a2) e=X(f1 c1 b3 b2) f=X(c2 e0 g1 g0) g=X(f3 f2 d1 d0) ['name'='-t5_4']",
        "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 e3 e2) d=X(f3 g0 b1 a2) e=X(g3 f0 c3 c2) f=X(e1 g2 g1 d0) g=X(d1 f2 f1 e0) ['name'='+t5_5']",
        "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 d0) d=X(c2 f0 g3 a2) e=X(b1 g2 f1 b2) f=X(d1 e2 g1 g0) g=X(f3 f2 e1 d2) ['name'='-t5_5']",
        "a=V(b0 c0 d3) b=V(a0 e0 c1) c=X(a1 b2 f3 d0) d=X(c3 f2 e1 a2) e=X(b1 d2 g3 g2) f=X(g1 g0 d1 c2) g=X(f1 f0 e3 e2) ['name'='+t5_6']",
        "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=V(a1 f3 d0) d=X(c2 e0 b1 a2) e=X(d1 g0 g3 b2) f=X(b3 g2 g1 c1) g=X(e1 f2 f1 e2) ['name'='-t5_6']",
        "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=V(a1 f3 g0) d=X(g3 g2 b1 a2) e=X(g1 f2 f1 b2) f=X(b3 e2 e1 c1) g=X(c2 e0 d1 d0) ['name'='+t5_7']",
        "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 f1 d0) d=X(c3 g0 e1 a2) e=X(b1 d2 g3 g2) f=X(g1 c2 c1 b2) g=X(d1 f0 e3 e2) ['name'='-t5_7']",
        "a=V(b0 c3 d3) b=X(a0 d2 e3 f0) c=X(f2 g0 g3 a1) d=X(g2 e0 b1 a2) e=X(d1 h0 h3 b2) f=V(b3 h2 c0) g=X(c1 h1 d0 c2) h=X(e1 g1 f1 e2) ['name'='t6_1.1']",
        "a=V(b0 c0 d3) b=X(a0 e0 f3 f2) c=X(a1 f1 g3 d0) d=X(c3 g2 e1 a2) e=V(b1 d2 h3) f=X(h2 c1 b3 b2) g=X(h1 h0 d1 c2) h=X(g1 g0 f0 e2) ['name'='t6_1.2']",
        "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 e0 e3 d0) d=X(c3 e2 e1 b1) e=X(c1 d2 d1 c2) ['name'='t0_1#+3_1']",
        "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 d2 e3 e2) d=X(e1 e0 c1 b1) e=X(d1 d0 c3 c2) ['name'='t0_1#-3_1']",
        "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 e0 f3 d0) d=X(c3 f2 e1 b1) e=X(c1 d2 f1 f0) f=X(e3 e2 d1 c2) ['name'='t0_1#4_1']",
        "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 e0 e3 d0) d=X(c3 f0 f3 b1) e=X(c1 g0 g3 c2) f=X(d1 g2 g1 d2) g=X(e1 f2 f1 e2) ['name'='t0_1#+5_1']",
        "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 d2 e3 e2) d=X(f3 f2 c1 b1) e=X(g3 g2 c3 c2) f=X(g1 g0 d1 d0) g=X(f1 f0 e1 e0) ['name'='t0_1#-5_1']",
        "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 e0 f3 f2) d=X(f1 g0 g3 b1) e=X(c1 g2 g1 f0) f=X(e3 d0 c3 c2) g=X(d1 e2 e1 d2) ['name'='t0_1#+5_2']",
        "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 e0 f3 f2) d=X(g3 e2 e1 b1) e=X(c1 d2 d1 g2) f=X(g1 g0 c3 c2) g=X(f1 f0 e3 d0) ['name'='t0_1#-5_2']",
        "a=V(a1 a0 b0) b=V(a2 b2 b1) ['name'='h0_1']",
        "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2) ['name'='h2_1.1']",
        "a=V(b0 c0 d3) b=X(a0 d2 d1 c1) c=V(a1 b3 d0) d=X(c2 b2 b1 a2) ['name'='h2_1.2']",
        "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 e3 e2) d=X(f3 f2 b1 a2) e=X(f1 f0 c3 c2) f=X(e1 e0 d1 d0) ['name'='h4_1.1']",
        "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 d0) d=X(c2 f0 f3 a2) e=X(b1 f2 f1 b2) f=X(d1 e2 e1 d2) ['name'='h4_1.2']",
        "a=V(b0 c0 d3) b=X(a0 d2 e3 c1) c=V(a1 b3 f0) d=X(g3 e0 b1 a2) e=X(d1 g2 f1 b2) f=X(c2 e2 g1 g0) g=X(f3 f2 e1 d0) ['name'='h5_1.1']",
        "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 f0 g3 d0) d=X(c3 g2 b1 a2) e=X(g1 f2 f1 b2) f=X(c1 e2 e1 g0) g=X(f3 e0 d1 c2) ['name'='h5_1.2']",
        "a=V(b0 c0 d3) b=X(a0 e0 e3 f0) c=X(a1 f2 g3 g2) d=X(g1 h0 e1 a2) e=X(b1 d2 h3 b2) f=V(b3 h2 c1) g=X(h1 d0 c3 c2) h=X(d1 g0 f1 e2) ['name'='h6_1']",
        "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=X(a1 f0 f3 g0) d=X(g2 h0 b1 a2) e=X(h3 f1 b3 b2) f=X(c1 e1 h2 c2) g=V(c3 h1 d0) h=X(d1 g1 f2 e0) ['name'='h6_2.1']",
        "a=V(b0 c0 d3) b=X(a0 e0 f3 f2) c=X(a1 f1 g3 d0) d=X(c3 h0 e1 a2) e=V(b1 d2 h3) f=X(g0 c1 b3 b2) g=X(f0 h2 h1 c2) h=X(d1 g2 g1 e2) ['name'='h6_2.2']",
    ]
    filename = "_test_draw_thetas.pdf"
    thetas = [from_knotpy_notation(code) for code in theta_curves]

    # batch draw to PDF

    try:
        export_pdf(thetas, filename)
    except Exception as e:
        assert False, f"Exporting PDF failed: {e}"

    assert os.path.exists(filename), f"File does not exist: {filename}"  # Check if file exists
    file_size = os.path.getsize(filename)
    assert file_size > 10 * 1024, f"File is too small: {file_size} bytes"  # Check if file is larger than 10 KB (10 * 1024 bytes)
    os.remove(filename)   # Remove the file

    # batch draw to PNG
    # for k in thetas:
    #     draw(k)
    #     plt.savefig(f"./{k.name}.png")



def test_draw_bridges():
    graph_with_bridge = from_pd_notation("[[0,1,2],[0,3,4],[5,6,7,2],[1,7,6,5],[4,8,9,10],[8,3,10,9]]")
    print(graph_with_bridge)

if __name__ == "__main__":
    test_draw_knot()
    test_draw_theta()
