from knotpy import simplify_decreasing
from knotpy.notation.native import from_knotpy_notation
from knotpy.reidemeister.reidemeister_5 import reidemeister_5_twist, reidemeister_5_untwist, find_reidemeister_5_twists, find_reidemeister_5_untwists
from knotpy.invariants.yamada import yamada
from knotpy.algorithms import sanity_check


def test_reidemeister_5():

    theta_codes = [
        # Theta curves (Moriuchi)
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
        # Bonded knots (Wanda)
        "a=X(b0 b3 c3 d3) b=X(a0 d2 e0 a1) c=X(e3 e2 d0 a2) d=X(c2 e1 b1 a3) e=X(b2 d1 c1 c0)",
        "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 e1 d0) d=X(c3 e0 b1 a2) e=X(d1 c2 c1 b2)",
        "a=V(b0 c0 d0) b=X(a0 d3 e0 c1) c=X(a1 b3 e2 d1) d=X(a2 c3 e1 b1) e=V(b2 d2 c2)",
        "a=X(b0 b3 c0 d0) b=X(a0 e0 c1 a1) c=X(a2 b2 e3 d1) d=X(a3 c3 e2 e1) e=X(b1 d3 d2 c2)",
        "a=V(b0 c0 d3) b=V(a0 e3 c1) c=X(a1 b2 e2 d0) d=X(c3 e1 e0 a2) e=X(d2 d1 c2 b1)",
        "a=V(b0 c0 d0) b=V(a0 d3 e0) c=V(a1 e2 d1) d=X(a2 c2 e1 b1) e=V(b2 d2 c1)",
        "a=V(b0 c0 d3) b=V(a0 e3 c1) c=X(a1 b2 e2 d0) d=X(c3 f3 f2 a2) e=X(f1 f0 c2 b1) f=X(e1 e0 d2 d1)",
        "a=V(b0 c0 d0) b=V(a0 e0 c1) c=X(a1 b2 f3 f2) d=V(a2 f1 e1) e=V(b1 d2 f0) f=X(e2 d1 c3 c2)",
        "a=V(b0 c3 d3) b=V(a0 e3 f3) c=X(f2 f1 d0 a1) d=X(c2 e1 e0 a2) e=X(d2 d1 f0 b1) f=X(e2 c1 c0 b2)",
        "a=V(b0 c0 d0) b=V(a0 e3 c1) c=X(a1 b2 e2 d1) d=X(a2 c3 f0 f3) e=X(f2 f1 c2 b1) f=X(d2 e1 e0 d3)",
        "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 f0 f3 d0) d=X(c3 e0 b1 a2) e=X(d1 f2 f1 b2) f=X(c1 e2 e1 c2)",
        "a=V(b0 c0 d0) b=V(a0 d2 e0) c=V(a1 e2 f0) d=V(a2 f2 b1) e=V(b2 f1 c1) f=V(c2 e1 d1)",
        "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 f3 d0) d=X(c3 g0 b1 a2) e=X(g3 f0 c1 b2) f=X(e1 g2 g1 c2) g=X(d1 f2 f1 e0)",
        "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 f0 f3 g0) d=X(g3 e0 b1 a2) e=X(d1 g2 f1 b2) f=X(c1 e2 g1 c2) g=X(c3 f2 e1 d0)",
        "a=V(b0 c0 d0) b=V(a0 d2 e0) c=X(a1 e2 f3 g0) d=V(a2 g3 b1) e=V(b2 f0 c1) f=X(e1 g2 g1 c2) g=X(c3 f2 f1 d1)",
        "a=V(b0 c0 d0) b=V(a0 d3 e0) c=V(a1 e2 f0) d=X(a2 f2 g0 b1) e=V(b2 g2 c1) f=V(c2 g1 d1) g=V(d2 f1 e1)",
        "a=V(b0 c0 d0) b=V(a0 d3 e0) c=V(a1 e2 f3) d=X(a2 f2 g3 b1) e=V(b2 g2 c1) f=X(g1 g0 d1 c2) g=X(f1 f0 e1 d2)",
        "a=V(b0 c0 d3) b=X(a0 e0 f3 g0) c=X(a1 g2 d1 d0) d=X(c3 c2 e1 a2) e=X(b1 d2 f1 f0) f=X(e3 e2 g1 b2) g=V(b3 f2 c1)",
        "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 e1 f0) d=X(g3 g2 b1 a2) e=X(f1 c2 c1 b2) f=X(c3 e0 g1 g0) g=X(f3 f2 d1 d0)",
        "a=V(b0 c0 d0) b=V(a0 d3 e3) c=V(a1 f0 g3) d=X(a2 g2 g1 b1) e=X(h3 h2 f1 b2) f=V(c1 e2 h1) g=X(h0 d2 d1 c2) h=X(g0 f2 e1 e0)",
        "a=V(b0 c0 d0) b=V(a0 e0 c1) c=X(a1 b2 f3 f2) d=V(a2 g0 e1) e=V(b1 d2 h0) f=X(h2 g1 c3 c2) g=V(d1 f1 h1) h=V(e2 g2 f0)",
        "a=V(b0 c0 d0) b=V(a0 d3 e0) c=V(a1 e2 f0) d=X(a2 f3 g0 b1) e=V(b2 g3 c1) f=X(c2 h0 h3 d1) g=X(d2 h2 h1 e1) h=X(f1 g2 g1 f2)",
        "a=V(b0 c0 d0) b=V(a0 d2 e0) c=V(a1 e2 f0) d=V(a2 g0 b1) e=V(b2 h0 c1) f=V(c2 h2 g1) g=V(d1 f2 h1) h=V(e1 g2 f1)",
        "a=V(b0 c0 d0) b=V(a0 e0 c1) c=X(a1 b2 f3 f2) d=X(a2 g3 g2 h0) e=V(b1 h3 i0) f=X(i2 g0 c3 c2) g=X(f1 h1 d2 d1) h=X(d3 g1 i1 e1) i=V(e2 h2 f0)",
        "a=V(b0 c0 d3) b=V(a0 e0 f0) c=V(a1 f2 g3) d=X(g2 e2 e1 a2) e=X(b1 d2 d1 h0) f=V(b2 i0 c1) g=X(i2 h1 d0 c2) h=V(e3 g1 i1) i=V(f1 h2 g0)",
        "a=V(b0 c3 d3) b=V(a0 e0 f0) c=X(f2 d1 d0 a1) d=X(c2 c1 e1 a2) e=X(b1 d2 g0 h0) f=V(b2 i0 c0) g=V(e2 i2 h1) h=V(e3 g2 i1) i=V(f1 h2 g1)",
        "a=V(b0 c0 d0) b=V(a0 e3 c1) c=X(a1 b2 e2 f0) d=V(a2 f3 g0) e=X(g3 h0 c2 b1) f=X(c3 i0 i3 d1) g=X(d2 i2 h1 e0) h=V(e1 g2 i1) i=X(f1 h2 g1 f2)",
        "a=V(b0 c0 d3) b=X(a0 d2 e0 f0) c=V(a1 g0 d0) d=X(c2 e1 b1 a2) e=V(b2 d1 g3) f=V(b3 h0 i0) g=X(c1 i3 h1 e2) h=X(f1 g2 i2 i1) i=X(f2 h3 h2 g1)",
        "a=V(b0 c0 d0) b=V(a0 e0 f0) c=X(a1 f2 g0 h0) d=V(a2 h3 e1) e=X(b1 d2 i3 i2) f=V(b2 j0 c1) g=V(c2 j2 h1) h=X(c3 g2 i0 d1) i=X(h2 j1 e3 e2) j=V(f1 i1 g1)",
        "a=V(b0 c0 d3) b=V(a0 d2 e3) c=V(a1 e2 f0) d=X(g3 g2 b1 a2) e=X(h0 i0 c1 b2) f=V(c2 i3 j0) g=X(j2 h1 d1 d0) h=V(e0 g1 i1) i=X(e1 h2 j1 f1) j=V(f2 i2 g0)",
        "a=V(b0 c0 d3) b=V(a0 e3 f0) c=V(a1 f2 d0) d=X(c2 g0 e0 a2) e=X(d2 h0 i0 b1) f=V(b2 j0 c1) g=V(d1 j2 h1) h=V(e1 g2 i1) i=V(e2 h2 j1) j=V(f1 i2 g1)",
        "a=V(b0 c0 d0) b=V(a0 d2 e3) c=X(a1 e2 e1 f0) d=V(a2 g0 b1) e=X(h3 c2 c1 b2) f=V(c3 i0 g1) g=V(d1 f2 j0) h=X(j3 j2 i1 e0) i=V(f1 h2 j1) j=X(g2 i2 h1 h0)",
        # Connected sums (Topoly)
        "a=V(b0 b2 c0) b=V(a0 d3 a1) c=X(a2 e0 f3 d0) d=X(c3 g0 e1 b1) e=X(c1 d2 g3 h0) f=X(h3 i0 i3 c2) g=X(d1 i2 h1 e2) h=X(e3 g2 i1 f0) i=X(f1 h2 g1 f2)",
        "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 g0 e3 d0) d=X(c3 e2 e1 a2) e=X(b1 d2 d1 c2) f=X(g3 h0 h3 b2) g=X(c1 h2 h1 f0) h=X(f1 g2 g1 f2)",
        "a=V(b0 c0 d3) b=V(a0 e0 c1) c=X(a1 b2 f3 d0) d=X(c3 e2 e1 a2) e=X(b1 d2 d1 g0) f=X(h3 h2 i3 c2) g=X(e3 i2 i1 h0) h=X(g3 i0 f1 f0) i=X(h1 g2 g1 f2)",
        "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 g3 d0) d=X(c3 g2 g1 a2) e=X(b1 h0 h3 f0) f=X(e3 h2 c1 b2) g=X(h1 d2 d1 c2) h=X(e1 g0 f1 e2)",
        "a=V(b0 c0 d3) b=X(a0 e0 e3 f0) c=V(a1 f3 g0) d=X(h3 e2 e1 a2) e=X(b1 d2 d1 b2) f=X(b3 i0 i3 c1) g=X(c2 i2 h1 h0) h=X(g3 g2 i1 d0) i=X(f1 h2 g1 f2)",
        "a=V(b0 c3 d3) b=X(a0 e0 e3 c0) c=X(b3 f0 g0 a1) d=X(h3 e2 e1 a2) e=X(b1 d2 d1 b2) f=V(c1 h2 i3) g=X(c2 i2 i1 j0) h=X(j3 j2 f1 d0) i=X(j1 g2 g1 f2) j=X(g3 i0 h1 h0)",
        "a=V(b0 c0 d3) b=V(a0 e0 c1) c=X(a1 b2 e3 d0) d=X(c3 f0 f3 a2) e=X(b1 g3 h0 c2) f=X(d1 i0 i3 d2) g=X(i2 j0 j3 e1) h=X(e2 j2 j1 i1) i=X(f1 h3 g0 f2) j=X(g1 h2 h1 g2)",
        "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=X(a1 e1 f0 g0) d=X(g3 h0 b1 a2) e=X(i3 c1 b3 b2) f=V(c2 i2 g1) g=X(c3 f2 j3 d0) h=X(d1 j2 j1 i0) i=X(h3 j0 f1 e0) j=X(i1 h2 h1 g2)",
        "a=V(b0 c0 d0) b=V(a0 e0 c1) c=X(a1 b2 f3 g3) d=X(a2 g2 h0 e1) e=X(b1 d3 i3 f0) f=X(e3 i2 j0 c2) g=X(j3 j2 d1 c3) h=X(d2 j1 k3 k2) i=X(k1 k0 f1 e2) j=X(f2 h1 g1 g0) k=X(i1 i0 h3 h2)",
        "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 g3 d0) d=X(c3 g2 e1 a2) e=X(b1 d2 h3 h2) f=X(i3 i2 c1 b2) g=X(i1 h0 d1 c2) h=X(g1 i0 e3 e2) i=X(h1 g0 f1 f0)",
        "a=V(b0 c0 d3) b=V(a0 e0 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 f3 a2) e=X(b1 g0 g3 f0) f=X(e3 g2 g1 d2) g=X(e1 f2 f1 e2)",
        "a=V(b0 c3 d3) b=X(a0 d2 d1 e0) c=X(e2 f0 f3 a1) d=X(f2 b2 b1 a2) e=V(b3 f1 c0) f=X(c1 e1 d0 c2)",
        "a=V(b0 c0 d3) b=V(a0 e3 f0) c=X(a1 f3 d1 d0) d=X(c3 c2 e0 a2) e=X(d2 g0 g3 b1) f=X(b2 g2 g1 c1) g=X(e1 f2 f1 e2)",
        "a=V(b0 c0 d3) b=X(a0 d2 d1 e0) c=V(a1 e3 f0) d=X(f3 b2 b1 a2) e=X(b3 g0 g3 c1) f=X(c2 g2 g1 d0) g=X(e1 f2 f1 e2)",
    ]

    for code in theta_codes[::20]:
        #print(code)
        k = from_knotpy_notation(code)
        assert sanity_check(k)
        y = yamada(k)
        for location in find_reidemeister_5_twists(k):
            #print(k, location)
            k_2 = reidemeister_5_twist(k, location, inplace=False)
            assert sanity_check(k_2)
            y_2 = yamada(k_2)
            # for location_2 in find_reidemeister_5_untwists(k_2):
            #     print(".  ", k_2, location_2)

def test_framing_5():
    from knotpy import settings
    settings.allowed_moves = "r1, r2, r3, r4, r5"
    # settings.trace_moves = False

    t = from_knotpy_notation("a=V(b0 b2 b1) b=V(a0 a2 a1)")
    k = from_knotpy_notation("a=V(b0 c3 c2) b=V(a0 c1 c0) c=X(b2 b1 a2 a1)")
    q=    simplify_decreasing(k, inplace=False)
    assert yamada(q) == yamada(t)
    # print(q)
    # print(yamada(k))
    # print(yamada(t))

def test_simple_5():
    k = from_knotpy_notation("a → V(a1 a0 c2), b → V(c3 c1 c0), c → X(b2 b1 a2 b0)")
    print(k)
    l = list(find_reidemeister_5_untwists(k))
    kk = reidemeister_5_untwist(k, l[0], inplace=False)
    print(kk)
    print(l)


if __name__ == "__main__":
    print("testing reidemeister 5")
    test_reidemeister_5()
    print("testing framing")
    test_framing_5()
    print("testing simple")
    test_simple_5()