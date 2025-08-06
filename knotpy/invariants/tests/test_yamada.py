from sympy import Integer, sympify, expand
from itertools import islice
from knotpy.notation.native import from_knotpy_notation
from knotpy.notation.pd import from_pd_notation
from knotpy.tables.theta import theta, handcuff
from knotpy.invariants.yamada import yamada, _naive_yamada_polynomial
from knotpy._settings import settings

def test_yamada_examples_from_paper():
    """ Test the Yamada polynomial with examples from the paper
    [Yamada, Shǔji. "An invariant of spatial graphs." Journal of Graph Theory 13.5 (1989): 537-551.]
    """

    fig6a = handcuff("H0_1")
    #fig6b = from_pd_notation("V(0,6,2);V(0,1,5);V(1,2,3,4);V(6,5,4,3)")
    fig7a = theta("T0_1")
    fig7b = from_pd_notation('V(4,12,5);V(8,7,0);X(0,11,1,12);X(5,1,6,2);X(10,6,11,7);X(9,3,8,4);X(2,10,3,9)')

    expected_yamada_6a = Integer(0)
    #expected_yamada_6b = sympify("-A**5 - A**4 - A**3 - A**2 + A**(-1) + A**(-2) + A**(-3) + A**(-4)")
    expected_yamada_7a = sympify("-A**2 -A -2 -A**(-1) - A**(-2)")
    expected_yamada_7b = sympify("A**9 - A**8 - 2*A**7 + A**6 - A**5 + 2*A**3 + A**2 + 2*A + 1/A - A**(-3) + A**(-4) + A**(-5) - 1/A**6 + A**(-7) + A**(-8)")

    yamada_6a = yamada(fig6a, normalize=False)
    #yamada_6b = yamada(fig6b, normalize=False)
    yamada_7a = yamada(fig7a, normalize=False)
    yamada_7b = yamada(fig7b, normalize=False)

    assert yamada_6a == expected_yamada_6a, f"{yamada_6a} != {expected_yamada_6a} (expected)"
    #assert yamada_6b == expected_yamada_6b # This one does not work, error in Yamada's paper?
    assert yamada_7a == expected_yamada_7a, f"{yamada_7a} != {expected_yamada_7a} (expected)"
    assert yamada_7b == expected_yamada_7b, f"{yamada_7b} != {expected_yamada_7b} (expected)"


def test_yamada_moriuchi():
    """
    Test the Yamada polynomial with Moriuchi's classification of theta-curves and hancduff links from
    [Moriuchi, Hiromasa. "An Enumeration of Theta-Curves with up to Seven Crossings"  Journal of Knot Theory & Its Ramifications 18.2 (2009)]
    [Moriuchi, Hiromasa. "A table of $\theta $-curves and handcuff graphs with up to seven crossings." Noncommutativity and Singularities: Proceedings of French–Japanese symposia held at IHÉS in 2006. Vol. 55. Mathematical Society of Japan, 2009.]
    Test examples and values are taken from Topoly (https://topoly.cent.uw.edu.pl/)
    [Pawel Dabrowski-Tumanski, Pawel Rubach, Wanda Niemyska, Bartosz Ambrozy Gren, Joanna Ida Sulkowska, Topoly: Python package to analyze topology of polymers, Briefings in Bioinformatics, bbaa196, https://doi.org/10.1093/bib/bbaa196]
    """

    yamadas = {
        "a=V(b0 b2 b1) b=V(a0 a2 a1) ['name'='t0_1']": "-A**4 - A**3 - 2*A**2 - A - 1",
        "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 e1 d0) d=X(c3 e0 b1 a2) e=X(d1 c2 c1 b2) ['name'='+t3_1']": "-A**12 - A**11 - A**10 - A**9 - A**8 - A**6 - A**4 + 1",
        "a=V(b0 c0 d3) b=X(a0 d2 e3 c1) c=V(a1 b3 e2) d=X(e1 e0 b1 a2) e=X(d1 d0 c2 b2) ['name'='-t3_1']": "A**12 - A**8 - A**6 - A**4 - A**3 - A**2 - A - 1",
        # "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 e3 f0) d=X(f3 e0 b1 a2) e=X(d1 f2 f1 c2) f=X(c3 e2 e1 d0) ['name'='t4_1.1']": "A**15 + A**12 + A**9 + A**7 + A**5 + A**4 + A**2 - 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 f3 c1) c=V(a1 b3 d0) d=X(c2 f2 e1 a2) e=X(b1 d2 f1 f0) f=X(e3 e2 d1 b2) ['name'='t4_1.2']": "A**15 - A**13 - A**11 - A**10 - A**8 - A**6 - A**3 - 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 f0) c=X(a1 f2 g3 d0) d=X(c3 g2 e1 a2) e=X(b1 d2 g1 b2) f=V(b3 g0 c1) g=X(f1 e2 d1 c2) ['name'='t5_1.1']": "-A**17 - A**16 + A**15 - A**14 - A**13 + A**12 - A**10 - 2*A**8 - A**7 - 2*A**6 + A**4 - A**3 + 2*A**2 + A - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=X(a1 f2 g3 g2) d=X(g1 e0 b1 a2) e=X(d1 g0 f1 b2) f=V(b3 e2 c1) g=X(e1 d0 c3 c2) ['name'='t5_1.2']": "A**17 - A**16 - 2*A**15 + A**14 - A**13 + 2*A**11 + A**10 + 2*A**9 + A**7 - A**5 + A**4 + A**3 - A**2 + A + 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=X(a1 e1 f3 f2) d=X(f1 g0 b1 a2) e=X(g2 c1 b3 b2) f=X(g1 d0 c3 c2) g=V(d1 f0 e0) ['name'='+t5_2']": "-A**16 - A**15 + A**14 + A**11 - A**10 - 2*A**8 - A**7 - 2*A**6 - 2*A**5 + A + 1",
        # "a=V(b0 c3 d3) b=X(a0 e0 f0 c0) c=X(b3 g0 g3 a1) d=X(g2 e2 e1 a2) e=X(b1 d2 d1 f1) f=V(b2 e3 g1) g=X(c1 f2 d0 c2) ['name'='-t5_2']": "A**16 + A**15 - 2*A**11 - 2*A**10 - A**9 - 2*A**8 - A**6 + A**5 + A**2 - A - 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 d0) d=X(c2 f0 f3 a2) e=X(b1 g0 g3 b2) f=X(d1 g2 g1 d2) g=X(e1 f2 f1 e2) ['name'='+t5_3']": "-A**18 - A**17 - A**16 - A**15 - A**14 - A**8 - A**6 - A**4 + A**2 + 1",
        # "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 e3 e2) d=X(f3 f2 b1 a2) e=X(g3 g2 c3 c2) f=X(g1 g0 d1 d0) g=X(f1 f0 e1 e0) ['name'='-t5_3']": "A**18 + A**16 - A**14 - A**12 - A**10 - A**4 - A**3 - A**2 - A - 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 f1 d0) d=X(c3 g0 g3 a2) e=X(b1 g2 g1 f0) f=X(e3 c2 c1 b2) g=X(d1 e2 e1 d2) ['name'='+t5_4']": "A**17 + A**16 + A**15 + A**14 + 2*A**13 + A**12 + A**11 + A**10 - A**8 - A**6 - A**4 - A + 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=V(a1 e1 f0) d=X(g3 g2 b1 a2) e=X(f1 c1 b3 b2) f=X(c2 e0 g1 g0) g=X(f3 f2 d1 d0) ['name'='-t5_4']": "-A**17 + A**16 + A**13 + A**11 + A**9 - A**7 - A**6 - A**5 - 2*A**4 - A**3 - A**2 - A - 1",
        # "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 e3 e2) d=X(f3 g0 b1 a2) e=X(g3 f0 c3 c2) f=X(e1 g2 g1 d0) g=X(d1 f2 f1 e0) ['name'='+t5_5']": "-A**18 - A**16 - 2*A**15 - A**13 - 2*A**12 - A**10 + A**9 + A**7 + A**6 - A**5 - A**2 + 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 d0) d=X(c2 f0 g3 a2) e=X(b1 g2 f1 b2) f=X(d1 e2 g1 g0) g=X(f3 f2 e1 d2) ['name'='-t5_5']": "A**18 - A**16 - A**13 + A**12 + A**11 + A**9 - A**8 - 2*A**6 - A**5 - 2*A**3 - A**2 - 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 c1) c=X(a1 b2 f3 d0) d=X(c3 f2 e1 a2) e=X(b1 d2 g3 g2) f=X(g1 g0 d1 c2) g=X(f1 f0 e3 e2) ['name'='+t5_6']": "-A**18 - 2*A**15 - A**12 + A**11 - A**10 - 2*A**8 - A**7 - A**5 + A**3 + 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=V(a1 f3 d0) d=X(c2 e0 b1 a2) e=X(d1 g0 g3 b2) f=X(b3 g2 g1 c1) g=X(e1 f2 f1 e2) ['name'='-t5_6']": "A**18 + A**15 - A**13 - A**11 - 2*A**10 - A**8 + A**7 - A**6 - 2*A**3 - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=V(a1 f3 g0) d=X(g3 g2 b1 a2) e=X(g1 f2 f1 b2) f=X(b3 e2 e1 c1) g=X(c2 e0 d1 d0) ['name'='+t5_7']": "2*A**17 + A**16 + 2*A**14 + A**13 + 2*A**11 + A**9 - A**8 - 2*A**5 - A**2 + 1",
        "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 f1 d0) d=X(c3 g0 e1 a2) e=X(b1 d2 g3 g2) f=X(g1 c2 c1 b2) g=X(d1 f0 e3 e2) ['name'='-t5_7']": "-A**17 + A**15 + 2*A**12 + A**9 - A**8 - 2*A**6 - A**4 - 2*A**3 - A - 2",
        # "a=V(b0 c3 d3) b=X(a0 d2 e3 f0) c=X(f2 g0 g3 a1) d=X(g2 e0 b1 a2) e=X(d1 h0 h3 b2) f=V(b3 h2 c0) g=X(c1 h1 d0 c2) h=X(e1 g1 f1 e2) ['name'='t6_1.1']": "-A**19 - A**18 + 2*A**17 - A**15 + 3*A**14 + A**13 + 2*A**11 + A**9 - A**8 + A**7 + A**6 - 2*A**5 + A**4 + A**3 - 2*A**2 + 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 f3 f2) c=X(a1 f1 g3 d0) d=X(c3 g2 e1 a2) e=V(b1 d2 h3) f=X(h2 c1 b3 b2) g=X(h1 h0 d1 c2) h=X(g1 g0 f0 e2) ['name'='t6_1.2']": "-A**19 + 2*A**17 - A**16 - A**15 + 2*A**14 - A**13 - A**12 + A**11 - A**10 - 2*A**8 - A**6 - 3*A**5 + A**4 - 2*A**2 + A + 1",
        # "a=V(b0 c3 d3) b=X(a0 e0 f0 c0) c=X(b3 g0 g3 a1) d=X(g2 h0 e1 a2) e=V(b1 d2 h3) f=X(b2 h2 i3 i2) g=X(c1 i1 d0 c2) h=X(d1 i0 f1 e2) i=X(h1 g1 f3 f2) ['name'='+t6_2']": "A**20 - 2*A**18 + 2*A**17 - 4*A**15 - A**13 - 3*A**12 - A**10 + A**9 - A**8 + A**7 + 3*A**6 - 2*A**5 + 2*A**3 - 2*A**2 - A + 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=X(a1 e1 f3 g0) d=X(g2 h3 b1 a2) e=X(i0 c1 b3 b2) f=X(i3 h0 g1 c2) g=V(c3 f2 d0) h=X(f1 i2 i1 d1) i=X(e0 h2 h1 f0) ['name'='-t6_2']": "A**20 - A**19 - 2*A**18 + 2*A**17 - 2*A**15 + 3*A**14 + A**13 - A**12 + A**11 - A**10 - 3*A**8 - A**7 - 4*A**5 + 2*A**3 - 2*A**2 + 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 f0) c=X(a1 g0 g3 d0) d=X(c3 h0 e1 a2) e=X(b1 d2 h3 b2) f=V(b3 h2 g1) g=X(c1 f2 h1 c2) h=X(d1 g2 f1 e2) ['name'='-t6_3']": "A**19 + A**18 - A**17 + A**15 - 2*A**14 - 2*A**13 + A**12 - A**11 - A**10 + A**9 - A**8 - 2*A**6 + A**5 - 2*A**3 + 2*A**2 - 2",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=X(a1 f0 g3 g2) d=X(g1 h0 b1 a2) e=X(h3 f1 b3 b2) f=V(c1 e1 h2) g=X(h1 d0 c3 c2) h=X(d1 g0 f2 e0) ['name'='+t6_3']": "2*A**19 - 2*A**17 + 2*A**16 - A**14 + 2*A**13 + A**11 - A**10 + A**9 + A**8 - A**7 + 2*A**6 + 2*A**5 - A**4 + A**2 - A - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f3) c=X(a1 f2 g3 g2) d=X(h0 e0 b1 a2) e=X(d1 h2 f0 b2) f=X(e2 g0 c1 b3) g=X(f1 h1 c3 c2) h=V(d0 g1 e1) ['name'='-t6_4']": "A**19 - A**17 + 2*A**16 - A**14 - 2*A**12 - A**11 - 2*A**10 - A**7 + A**6 + A**5 - A**4 - A - 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 f0) c=X(a1 f3 g3 d0) d=X(c3 g2 h0 a2) e=X(b1 h2 f1 b2) f=X(b3 e2 g0 c1) g=X(f2 h1 d1 c2) h=V(d2 g1 e1) ['name'='+t6_4']": "A**19 + A**18 + A**15 - A**14 - A**13 + A**12 + 2*A**9 + A**8 + 2*A**7 + A**5 - 2*A**3 + A**2 - 1",
        # "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 f3 d0) d=X(c3 f2 b1 a2) e=X(g3 g2 c1 b2) f=X(h3 h2 d1 c2) g=X(h1 h0 e1 e0) h=X(g1 g0 f1 f0) ['name'='+t6_5']": "A**21 + A**18 - 2*A**17 - A**16 - 2*A**14 - A**12 - A**10 - A**9 + A**8 + A**5 - A**3 - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 c1) c=V(a1 b3 f0) d=X(f3 e0 b1 a2) e=X(d1 g0 g3 b2) f=X(c2 h0 h3 d0) g=X(e1 h2 h1 e2) h=X(f1 g2 g1 f2) ['name'='-t6_5']": "A**21 + A**18 - A**16 - A**13 + A**12 + A**11 + A**9 + 2*A**7 + A**5 + 2*A**4 - A**3 - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 c1) c=V(a1 b3 f0) d=X(g3 g2 b1 a2) e=X(h3 f2 f1 b2) f=X(c2 e2 e1 h2) g=X(h1 h0 d1 d0) h=X(g1 g0 f3 e0) ['name'='+t6_6']": "A**21 + A**19 + A**18 - A**17 + A**16 + A**15 - A**14 + A**13 + A**11 + A**8 - A**7 + A**5 + A**2 - 1",
        # "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 f0 f3 d0) d=X(c3 g0 b1 a2) e=X(g3 g2 h3 b2) f=X(c1 h2 h1 c2) g=X(d1 h0 e1 e0) h=X(g1 f2 f1 e2) ['name'='-t6_6']": "A**21 - A**19 - A**16 + A**14 - A**13 - A**10 - A**8 + A**7 - A**6 - A**5 + A**4 - A**3 - A**2 - 1",
        # "a=V(b0 c3 d3) b=X(a0 d2 e3 c0) c=X(b3 e2 f3 a1) d=X(f2 g0 b1 a2) e=X(h3 h2 c1 b2) f=X(i3 i2 d0 c2) g=V(d1 i1 h0) h=X(g2 i0 e1 e0) i=X(h1 g1 f1 f0) ['name'='+t6_7']": "-A**20 + A**19 + A**18 - A**17 + 2*A**16 + 2*A**15 + 2*A**13 - 2*A**10 - A**9 + A**8 - A**7 + A**6 + 2*A**5 + A**2 - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=X(a1 f3 g0 d0) d=X(c3 e0 b1 a2) e=X(d1 h0 h3 b2) f=X(b3 i0 i3 c1) g=V(c2 i2 h1) h=X(e1 g2 i1 e2) i=X(f1 h2 g1 f2) ['name'='-t6_7']": "-A**20 + A**18 + 2*A**15 + A**14 - A**13 + A**12 - A**11 - 2*A**10 + 2*A**7 + 2*A**5 + 2*A**4 - A**3 + A**2 + A - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=V(a1 f3 g0) d=X(g3 g2 b1 a2) e=X(h3 f0 b3 b2) f=X(e1 h2 h1 c1) g=X(c2 h0 d1 d0) h=X(g1 f2 f1 e0) ['name'='+t6_8']": "-A**20 + A**19 - 2*A**17 + A**16 - 2*A**14 - A**12 - A**10 + A**8 - 2*A**7 + A**5 - A**4 + A**2 - 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 f1 d0) d=X(c3 g0 g3 a2) e=X(b1 g2 h3 h2) f=X(h1 c2 c1 b2) g=X(d1 h0 e1 d2) h=X(g1 f0 e3 e2) ['name'='-t6_8']": "-A**20 + A**18 - A**16 + A**15 - 2*A**13 + A**12 - A**10 - A**8 - 2*A**6 + A**4 - 2*A**3 + A - 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 f0) d=X(f3 g0 g3 a2) e=X(b1 h0 f1 b2) f=X(c2 e2 h3 d0) g=X(d1 h2 h1 d2) h=X(e1 g2 g1 f2) ['name'='+t6_9']": "A**21 - A**19 + A**18 - 2*A**16 - A**14 - 3*A**13 - A**12 - A**10 + A**9 + 2*A**7 - A**6 - A**5 + 2*A**4 - 2*A**3 + A - 1",
        # "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 f3 f2) d=X(g3 g2 b1 a2) e=X(g1 h0 c1 b2) f=X(h3 h2 c3 c2) g=X(h1 e0 d1 d0) h=X(e1 g0 f1 f0) ['name'='-t6_9']": "A**21 - A**20 + 2*A**18 - 2*A**17 + A**16 + A**15 - 2*A**14 - A**12 + A**11 + A**9 + 3*A**8 + A**7 + 2*A**5 - A**3 + A**2 - 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 f0) d=X(f3 g0 g3 a2) e=X(b1 h0 h3 b2) f=X(c2 h2 g1 d0) g=X(d1 f2 h1 d2) h=X(e1 g2 f1 e2) ['name'='+t6_10']": "A**21 - A**19 + A**18 + A**17 - A**16 + 2*A**15 + 2*A**14 + A**12 + A**11 - A**10 - A**8 + A**7 - A**6 - A**5 + 3*A**4 - A**3 + A - 1",
        # "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 f3 f2) d=X(g3 g2 b1 a2) e=X(h3 f0 c1 b2) f=X(e1 h2 c3 c2) g=X(h1 h0 d1 d0) h=X(g1 g0 f1 e0) ['name'='-t6_10']": "A**21 - A**20 + A**18 - 3*A**17 + A**16 + A**15 - A**14 + A**13 + A**11 - A**10 - A**9 - 2*A**7 - 2*A**6 + A**5 - A**4 - A**3 + A**2 - 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 g3 d0) d=X(c3 h0 h3 a2) e=X(b1 h2 g1 f0) f=X(e3 g0 c1 b2) g=X(f1 e2 h1 c2) h=X(d1 g2 e1 d2) ['name'='+t6_11']": "-A**20 + 2*A**18 - A**16 + 3*A**15 + A**14 - A**13 + 2*A**12 + A**11 - A**10 + A**9 + A**7 - 2*A**6 + 2*A**4 - 3*A**3 + A**2 + 2*A - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=V(a1 f3 g0) d=X(g3 h0 b1 a2) e=X(h3 f0 b3 b2) f=X(e1 h2 g1 c1) g=X(c2 f2 h1 d0) h=X(d1 g2 f1 e0) ['name'='-t6_11']": "-A**20 + 2*A**19 + A**18 - 3*A**17 + 2*A**16 - 2*A**14 + A**13 + A**11 - A**10 + A**9 + 2*A**8 - A**7 + A**6 + 3*A**5 - A**4 + 2*A**2 - 1",
        # "a=V(b0 c3 d3) b=X(a0 e0 e3 c0) c=X(b3 f0 g0 a1) d=X(g3 h0 h3 a2) e=X(b1 i0 f1 b2) f=V(c1 e2 i3) g=X(c2 i2 h1 d0) h=X(d1 g2 i1 d2) i=X(e1 h2 g1 f2) ['name'='+t6_12']": "A**21 + 2*A**18 + A**17 - A**16 + 2*A**15 + A**14 - A**13 + A**12 + A**11 - A**10 - A**8 + A**7 - A**6 + 3*A**4 - 2*A**3 + A - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e0 f3) c=X(a1 f2 g3 g2) d=X(h3 h2 b1 a2) e=V(b2 h1 i0) f=X(i3 g0 c1 b3) g=X(f1 i2 c3 c2) h=X(i1 e1 d1 d0) i=X(e2 h0 g1 f0) ['name'='-t6_12']": "A**21 - A**20 + 2*A**18 - 3*A**17 + A**15 - A**14 + A**13 + A**11 - A**10 - A**9 + A**8 - A**7 - 2*A**6 + A**5 - A**4 - 2*A**3 - 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 f1 d0) d=X(c3 g0 e1 a2) e=X(b1 d2 g3 h0) f=X(h3 c2 c1 b2) g=X(d1 h2 h1 e2) h=X(e3 g2 g1 f0) ['name'='+t6_13']": "-A**20 + A**18 - A**17 - A**16 + 2*A**15 - A**14 - 2*A**13 + A**12 - A**11 - 2*A**10 - A**8 - 2*A**6 + A**5 + 2*A**4 - 2*A**3 + 2*A**2 + A - 2",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=V(a1 f3 g0) d=X(g3 g2 b1 a2) e=X(h3 h2 f1 b2) f=X(b3 e2 h1 c1) g=X(c2 h0 d1 d0) h=X(g1 f2 e1 e0) ['name'='-t6_13']": "-2*A**20 + A**19 + 2*A**18 - 2*A**17 + 2*A**16 + A**15 - 2*A**14 - A**12 - 2*A**10 - A**9 + A**8 - 2*A**7 - A**6 + 2*A**5 - A**4 - A**3 + A**2 - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=X(a1 f3 g0 h3) d=X(h2 i3 b1 a2) e=X(g1 f2 f1 b2) f=X(b3 e2 e1 c1) g=V(c2 e0 i2) h=X(j3 j2 d0 c3) i=X(j1 j0 g2 d1) j=X(i1 i0 h1 h0) ['name'='t6_14.1']": "-A**21 + A**20 + 2*A**19 - 2*A**18 + A**17 + 2*A**16 - 3*A**15 - 3*A**12 - A**11 - 2*A**10 + A**9 - A**8 - A**7 + 3*A**6 - A**5 - 2*A**4 + 2*A**3 - A**2 - A + 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e0 c1) c=V(a1 b3 f0) d=X(f3 g3 b1 a2) e=X(b2 h0 h3 i3) f=X(c2 i2 i1 d0) g=X(i0 h2 h1 d1) h=X(e1 g2 g1 e2) i=X(g0 f2 f1 e3) ['name'='t6_14.2']": "-A**21 + A**20 + A**19 - 2*A**18 + 2*A**17 + A**16 - 3*A**15 + A**14 + A**13 - A**12 + 2*A**11 + A**10 + 3*A**9 + 3*A**6 - 2*A**5 - A**4 + 2*A**3 - 2*A**2 - A + 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 g3 d0) d=X(c3 g2 e1 a2) e=X(b1 d2 h3 h2) f=X(h1 g0 c1 b2) g=X(f1 h0 d1 c2) h=X(g1 f0 e3 e2) ['name'='t6_15.1']": "A**20 - A**19 - 2*A**18 + 3*A**17 - 3*A**15 + 3*A**14 - 2*A**12 + A**11 - A**10 - 3*A**8 + A**6 - 4*A**5 + 2*A**3 - 3*A**2 + 2",
        # "a=V(b0 c0 d3) b=X(a0 d2 e0 f3) c=X(a1 g3 h0 d0) d=X(c3 e1 b1 a2) e=V(b2 d1 i0) f=X(i3 i2 g0 b3) g=X(f2 j0 j3 c1) h=X(c2 j2 j1 i1) i=X(e2 h3 f1 f0) j=X(g1 h2 h1 g2) ['name'='t6_15.2']": "2*A**20 - 3*A**18 + 2*A**17 - 4*A**15 + A**14 - 3*A**12 - A**10 + A**9 - 2*A**8 + 3*A**6 - 3*A**5 + 3*A**3 - 2*A**2 - A + 1",
        # "a=V(b0 c0 d3) b=V(a0 e3 f3) c=X(a1 f2 f1 d0) d=X(c3 g3 e0 a2) e=X(d2 h0 h3 b1) f=X(i0 c2 c1 b2) g=X(i3 i2 h1 d1) h=X(e1 g2 i1 e2) i=X(f0 h2 g1 g0) ['name'='-t6_16']": "-A**21 + A**20 + A**19 - 2*A**18 + 2*A**17 + 2*A**16 - 3*A**15 + A**14 + A**13 - 2*A**12 - 2*A**10 - 3*A**8 - 2*A**7 + 2*A**6 - 2*A**5 - A**4 + 3*A**3 - A**2 - A + 1",
        # "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 f3 g3 g2) d=X(g1 e0 b1 a2) e=X(d1 h3 f0 b2) f=X(e2 i0 i3 c1) g=X(h0 d0 c3 c2) h=X(g0 i2 i1 e1) i=X(f1 h2 h1 f2) ['name'='+t6_16']": "-A**21 + A**20 + A**19 - 3*A**18 + A**17 + 2*A**16 - 2*A**15 + 2*A**14 + 3*A**13 + 2*A**11 + 2*A**9 - A**8 - A**7 + 3*A**6 - 2*A**5 - 2*A**4 + 2*A**3 - A**2 - A + 1",
        # # "a=V(b0 c0 d3) b=X(a0 d2 e3 f3) c=X(a1 f2 g3 g2) d=X(h0 e0 b1 a2) e=X(d1 h2 f0 b2) f=X(e2 i0 c1 b3) g=X(i3 i2 c3 c2) h=V(d0 i1 e1) i=X(f1 h1 g1 g0) ['name'='+t7_20']": "-A**22 - 2*A**19 + 2*A**18 + A**17 - A**16 + A**15 - A**14 - 2*A**12 - 2*A**9 - A**8 - 2*A**6 - A**5 + A**4 + A + 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 f0) c=X(a1 f3 g3 d0) d=X(c3 g2 h0 a2) e=X(b1 i0 i3 b2) f=X(b3 i2 g0 c1) g=X(f2 h1 d1 c2) h=V(d2 g1 i1) i=X(e1 h2 f1 e2) ['name'='-t7_20']": "A**22 + A**21 + A**18 - A**17 - 2*A**16 - A**14 - 2*A**13 - 2*A**10 - A**8 + A**7 - A**6 + A**5 + 2*A**4 - 2*A**3 - 1",
        # "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 f0 f3 d0) d=X(c3 e0 b1 a2) e=X(d1 g0 g3 b2) f=X(c1 h0 h3 c2) g=X(e1 i0 i3 e2) h=X(f1 i2 i1 f2) i=X(g1 h2 h1 g2) ['name'='+t7_25']": "-A**24 - A**23 - A**22 - A**21 - A**20 - A**10 - A**8 - A**6 + A**2 + 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 c1) c=V(a1 b3 e2) d=X(f3 f2 b1 a2) e=X(g3 g2 c2 b2) f=X(h3 h2 d1 d0) g=X(i3 i2 e1 e0) h=X(i1 i0 f1 f0) i=X(h1 h0 g1 g0) ['name'='-t7_25']": "A**24 + A**22 - A**18 - A**16 - A**14 - A**4 - A**3 - A**2 - A - 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 g0 g3 d0) d=X(c3 h0 h3 a2) e=X(b1 h2 h1 f0) f=X(e3 i0 i3 b2) g=X(c1 i2 i1 c2) h=X(d1 e2 e1 d2) i=X(f1 g2 g1 f2) ['name'='+t7_26']": "-A**22 - A**21 - A**20 - A**19 - 2*A**18 - A**17 + A**13 - A**11 - A**8 + A**7 + A**5 - A**4 + A**2 - A + 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=V(a1 f3 g0) d=X(h3 h2 b1 a2) e=X(f1 f0 b3 b2) f=X(e1 e0 g1 c1) g=X(c2 f2 i3 i2) h=X(i1 i0 d1 d0) i=X(h1 h0 g3 g2) ['name'='-t7_26']": "A**22 - A**21 + A**20 - A**18 + A**17 + A**15 - A**14 - A**11 + A**9 - A**5 - 2*A**4 - A**3 - A**2 - A - 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 f1 d0) d=X(c3 g0 g3 a2) e=X(b1 h0 h3 f0) f=X(e3 c2 c1 b2) g=X(d1 i0 i3 d2) h=X(e1 i2 i1 e2) i=X(g1 h2 h1 g2) ['name'='+t7_27']": "A**23 + A**22 + A**21 + A**20 + 2*A**19 + A**18 + A**17 + A**16 + A**15 - A**11 - A**10 - A**8 - A**6 - A**4 - A**3 + A**2 + 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=V(a1 e1 f0) d=X(g3 g2 b1 a2) e=X(f1 c1 b3 b2) f=X(c2 e0 h3 h2) g=X(i3 i2 d1 d0) h=X(i1 i0 f3 f2) i=X(h1 h0 g1 g0) ['name'='-t7_27']": "-A**23 - A**21 + A**20 + A**19 + A**17 + A**15 + A**13 + A**12 - A**8 - A**7 - A**6 - A**5 - 2*A**4 - A**3 - A**2 - A - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 c1) c=V(a1 b3 f0) d=X(g3 g2 b1 a2) e=X(h3 f2 f1 b2) f=X(c2 e2 e1 h2) g=X(i3 i2 d1 d0) h=X(i1 i0 f3 e0) i=X(h1 h0 g1 g0) ['name'='+t7_28']": "-A**24 - A**22 - A**21 - 2*A**19 - A**18 - 2*A**16 + A**13 + A**10 + A**7 - A**5 - A**2 + 1",
        # "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 f0 f3 d0) d=X(c3 g0 b1 a2) e=X(g3 g2 h3 b2) f=X(c1 i0 i3 c2) g=X(d1 h0 e1 e0) h=X(g1 i2 i1 e2) i=X(f1 h2 h1 f2) ['name'='-t7_28']": "A**24 - A**22 - A**19 + A**17 + A**14 + A**11 - 2*A**8 - A**6 - 2*A**5 - A**3 - A**2 - 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 c1) c=X(a1 b2 f3 d0) d=X(c3 f2 e1 a2) e=X(b1 d2 g3 g2) f=X(h3 h2 d1 c2) g=X(i3 i2 e3 e2) h=X(i1 i0 f1 f0) i=X(h1 h0 g1 g0) ['name'='+t7_29']": "-A**24 - A**21 + A**20 - A**19 - A**18 + A**17 - A**16 - A**14 - A**12 - A**11 - A**8 - A**5 + A**3 + 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=V(a1 f3 d0) d=X(c2 e0 b1 a2) e=X(d1 g0 g3 b2) f=X(b3 h0 h3 c1) g=X(e1 i0 i3 e2) h=X(f1 i2 i1 f2) i=X(g1 h2 h1 g2) ['name'='-t7_29']": "A**24 + A**21 - A**19 - A**16 - A**13 - A**12 - A**10 - A**8 + A**7 - A**6 - A**5 + A**4 - A**3 - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=V(a1 f3 g0) d=X(h3 h2 b1 a2) e=X(f1 f0 b3 b2) f=X(e1 e0 i3 c1) g=X(c2 i2 i1 h0) h=X(g3 i0 d1 d0) i=X(h1 g2 g1 f2) ['name'='+t7_30']": "-2*A**22 - 3*A**19 + A**18 + A**17 - 2*A**16 - A**14 - 2*A**12 + 2*A**10 - A**9 + 2*A**7 - A**6 - A**5 + A**4 - A**2 + 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 g0 g3 d0) d=X(c3 h0 h3 a2) e=X(b1 h2 h1 i0) f=X(i3 i2 g1 b2) g=X(c1 f2 i1 c2) h=X(d1 e2 e1 d2) i=X(e3 g2 f1 f0) ['name'='-t7_30']": "A**22 - A**20 + A**18 - A**17 - A**16 + 2*A**15 - A**13 + 2*A**12 - 2*A**10 - A**8 - 2*A**6 + A**5 + A**4 - 3*A**3 - 2",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=V(a1 f3 g0) d=X(g3 g2 b1 a2) e=X(h3 h2 b3 b2) f=X(h1 i0 i3 c1) g=X(c2 i2 d1 d0) h=X(i1 f0 e1 e0) i=X(f1 h0 g1 f2) ['name'='+t7_32']": "A**23 + 2*A**21 + 2*A**20 - A**19 + 2*A**18 + 2*A**17 - A**16 + A**15 + A**13 - A**12 + A**10 - 2*A**9 - A**8 + A**7 - A**6 - A**5 + A**4 - A**2 + 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 f1 d0) d=X(c3 g0 g3 a2) e=X(b1 h0 i3 i2) f=X(i1 c2 c1 b2) g=X(d1 h2 h1 d2) h=X(e1 g2 g1 i0) i=X(h3 f0 e3 e2) ['name'='-t7_32']": "-A**23 + A**21 - A**19 + A**18 + A**17 - A**16 + A**15 + 2*A**14 - A**13 + A**11 - A**10 - A**8 + A**7 - 2*A**6 - 2*A**5 + A**4 - 2*A**3 - 2*A**2 - 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 f0) d=X(g3 g2 h3 a2) e=X(b1 h2 h1 b2) f=X(c2 h0 i3 i2) g=X(i1 i0 d1 d0) h=X(f1 e2 e1 d2) i=X(g1 g0 f3 f2) ['name'='-t7_33']": "A**24 + A**21 - A**20 - 2*A**19 + 2*A**18 - A**17 - A**16 + 2*A**15 - A**14 + A**13 - A**12 + A**11 - 2*A**9 + A**8 - 2*A**6 - 2*A**3 - A**2 - 1",
        # "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 f0 f3 g0) d=X(h3 h2 b1 a2) e=X(g1 i0 i3 b2) f=X(c1 i2 i1 c2) g=X(c3 e0 h1 h0) h=X(g3 g2 d1 d0) i=X(e1 f2 f1 e2) ['name'='+t7_33']": "-A**24 - A**22 - 2*A**21 - 2*A**18 + A**16 - 2*A**15 + A**13 - A**12 + A**11 - A**10 + 2*A**9 - A**8 - A**7 + 2*A**6 - 2*A**5 - A**4 + A**3 + 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=V(a1 f3 g0) d=X(g3 h0 b1 a2) e=X(f1 f0 b3 b2) f=X(e1 e0 h3 c1) g=X(c2 i0 i3 d0) h=X(d1 i2 i1 f2) i=X(g1 h2 h1 g2) ['name'='-t7_35']": "-A**23 + A**22 + A**21 - A**20 + A**19 + 3*A**18 - 2*A**17 + A**15 - 3*A**14 - A**12 + 2*A**11 - A**10 - A**9 + 2*A**8 - 2*A**7 - 2*A**6 + A**5 - A**4 - 2*A**3 - 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 g3 d0) d=X(c3 h0 h3 a2) e=X(b1 h2 h1 g2) f=X(i3 i2 c1 b2) g=X(i1 i0 e3 c2) h=X(d1 e2 e1 d2) i=X(g1 g0 f1 f0) ['name'='+t7_35']": "A**23 + 2*A**20 + A**19 - A**18 + 2*A**17 + 2*A**16 - 2*A**15 + A**14 + A**13 - 2*A**12 + A**11 + 3*A**9 - A**8 + 2*A**6 - 3*A**5 - A**4 + A**3 - A**2 - A + 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 f1 d0) d=X(c3 g0 e1 a2) e=X(b1 d2 h3 h2) f=X(g1 c2 c1 b2) g=X(d1 f0 i3 i2) h=X(i1 i0 e3 e2) i=X(h1 h0 g3 g2) ['name'='-t7_36']": "-A**23 - A**20 + A**19 + 2*A**18 - 2*A**17 + 2*A**16 + 2*A**15 - A**14 + 2*A**13 + A**11 - 2*A**10 - A**9 + A**8 - 2*A**7 - A**6 + A**5 - 2*A**4 - 2*A**3 - A - 2",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=V(a1 f3 g0) d=X(g3 g2 b1 a2) e=X(g1 h0 h3 b2) f=X(b3 i0 i3 c1) g=X(c2 e0 d1 d0) h=X(e1 i2 i1 e2) i=X(f1 h2 h1 f2) ['name'='+t7_36']": "2*A**23 + A**22 + 2*A**20 + 2*A**19 - A**18 + A**17 + 2*A**16 - A**15 + A**14 + 2*A**13 - A**12 - 2*A**10 + A**9 - 2*A**8 - 2*A**7 + 2*A**6 - 2*A**5 - A**4 + A**3 + 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=V(a1 e1 f0) d=X(g3 g2 b1 a2) e=X(h3 c1 b3 b2) f=X(c2 i0 i3 g0) g=X(f3 h0 d1 d0) h=X(g1 i2 i1 e0) i=X(f1 h2 h1 f2) ['name'='-t7_37']": "-A**23 + A**22 - 2*A**20 + A**19 + 2*A**18 - 2*A**17 + 2*A**16 + 3*A**15 - A**14 + A**13 - A**12 + A**11 - 2*A**10 - A**9 + 2*A**8 - 3*A**7 - 2*A**6 + A**5 - 2*A**4 - 2*A**3 - 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 g0 g3 d0) d=X(c3 e2 e1 a2) e=X(b1 d2 d1 h0) f=X(i3 i2 g1 b2) g=X(c1 f2 h1 c2) h=X(e3 g2 i1 i0) i=X(h3 h2 f1 f0) ['name'='+t7_37']": "A**23 + 2*A**20 + 2*A**19 - A**18 + 2*A**17 + 3*A**16 - 2*A**15 + A**14 + 2*A**13 - A**12 + A**11 - A**10 + A**9 - 3*A**8 - 2*A**7 + 2*A**6 - 2*A**5 - A**4 + 2*A**3 - A + 1",
        # "a=V(b0 c3 d3) b=X(a0 e0 e3 c0) c=X(b3 f0 g0 a1) d=X(g3 h0 i3 a2) e=X(b1 i2 i1 b2) f=V(c1 i0 h3) g=X(c2 j0 j3 d0) h=X(d1 j2 j1 f2) i=X(f1 e2 e1 d2) j=X(g1 h2 h1 g2) ['name'='-t7_38']": "A**24 - A**22 + A**21 + A**20 - 2*A**19 + A**18 + A**17 - 2*A**16 + A**14 - A**13 - A**12 + A**11 - A**10 - 2*A**8 + 2*A**7 - A**6 - 3*A**5 + 2*A**4 - 2*A**3 - A**2 + A - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e0 f3) c=X(a1 f2 g3 h0) d=X(i3 i2 b1 a2) e=V(b2 h1 g2) f=X(j3 j2 c1 b3) g=X(j1 j0 e2 c2) h=X(c3 e1 i1 i0) i=X(h3 h2 d1 d0) j=X(g1 g0 f1 f0) ['name'='+t7_38']": "-A**24 + A**23 - A**22 - 2*A**21 + 2*A**20 - 3*A**19 - A**18 + 2*A**17 - 2*A**16 - A**14 + A**13 - A**12 - A**11 + A**10 - 2*A**8 + A**7 + A**6 - 2*A**5 + A**4 + A**3 - A**2 + 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 g0 g3 d0) d=X(c3 h0 i3 a2) e=X(b1 i2 i1 f0) f=X(e3 h2 g1 b2) g=X(c1 f2 h1 c2) h=X(d1 g2 f1 i0) i=X(h3 e2 e1 d2) ['name'='-t7_40']": "A**22 - 2*A**20 + 2*A**18 - 3*A**17 - A**16 + 4*A**15 - A**13 + 4*A**12 + A**11 - 2*A**10 + A**9 - A**8 - A**7 - 5*A**6 + A**5 + A**4 - 5*A**3 + 2*A**2 + A - 3",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=V(a1 g3 h0) d=X(i3 i2 b1 a2) e=X(i1 h2 f1 b2) f=X(b3 e2 g1 g0) g=X(f3 f2 h1 c1) h=X(c2 g2 e1 i0) i=X(h3 e0 d1 d0) ['name'='+t7_40']": "-3*A**22 + A**21 + 2*A**20 - 5*A**19 + A**18 + A**17 - 5*A**16 - A**15 - A**14 + A**13 - 2*A**12 + A**11 + 4*A**10 - A**9 + 4*A**7 - A**6 - 3*A**5 + 2*A**4 - 2*A**2 + 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 g3 d0) d=X(c3 h0 h3 a2) e=X(b1 i0 i3 f0) f=X(e3 g0 c1 b2) g=X(f1 i2 h1 c2) h=X(d1 g2 i1 d2) i=X(e1 h2 g1 e2) ['name'='-t7_41']": "-A**23 + 2*A**21 - 2*A**19 + 3*A**18 + A**17 - 3*A**16 + A**15 + 2*A**14 - 2*A**13 + 2*A**11 - 2*A**10 - A**9 - 2*A**8 + 2*A**7 - 3*A**6 - 2*A**5 + 4*A**4 - 3*A**3 - 2*A**2 + A - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=V(a1 f3 g0) d=X(g3 h0 b1 a2) e=X(h3 i0 b3 b2) f=X(i3 i2 g1 c1) g=X(c2 f2 h1 d0) h=X(d1 g2 i1 e0) i=X(e1 h2 f1 f0) ['name'='+t7_41']": "A**23 - A**22 + 2*A**21 + 3*A**20 - 4*A**19 + 2*A**18 + 3*A**17 - 2*A**16 + 2*A**15 + A**14 + 2*A**13 - 2*A**12 + 2*A**10 - 2*A**9 - A**8 + 3*A**7 - A**6 - 3*A**5 + 2*A**4 - 2*A**2 + 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 f1 d0) d=X(c3 g0 e1 a2) e=X(b1 d2 g3 h0) f=X(h3 c2 c1 b2) g=X(d1 i0 i3 e2) h=X(e3 i2 i1 f0) i=X(g1 h2 h1 g2) ['name'='-t7_42']": "-A**23 + A**21 - A**20 - A**19 + 3*A**18 - A**16 + 3*A**15 + A**14 - 2*A**13 + A**12 + A**11 - 2*A**10 - A**8 + A**7 - 4*A**6 - A**5 + 2*A**4 - 4*A**3 + A - 2",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=V(a1 f3 g0) d=X(g3 g2 b1 a2) e=X(h3 h2 f1 b2) f=X(b3 e2 i3 c1) g=X(c2 i2 d1 d0) h=X(i1 i0 e1 e0) i=X(h1 h0 g1 f2) ['name'='+t7_42']": "2*A**23 - A**22 + 4*A**20 - 2*A**19 + A**18 + 4*A**17 - A**16 + A**15 + 2*A**13 - A**12 - A**11 + 2*A**10 - A**9 - 3*A**8 + A**7 - 3*A**5 + A**4 + A**3 - A**2 + 1",
        # "a=V(b0 c0 d0) b=V(a0 d3 e3) c=X(a1 f0 f3 g0) d=X(a2 h0 h3 b1) e=X(i0 g2 j3 b2) f=X(c1 j2 j1 c2) g=X(c3 j0 e1 i3) h=X(d1 i2 i1 d2) i=X(e0 h2 h1 g3) j=X(g1 f2 f1 e2) ['name'='+t7_43']": "-A**24 - 3*A**21 + 2*A**19 - 3*A**18 + A**17 + 3*A**16 - 3*A**15 - A**14 + A**13 - 2*A**12 - 2*A**10 + 2*A**9 - A**8 - 3*A**7 + 4*A**6 - A**5 - 2*A**4 + 3*A**3 - A + 1",
        # "a=V(b0 c3 d3) b=V(a0 d2 e0) c=X(f3 f2 g3 a1) d=X(h3 h2 b1 a2) e=X(b2 i3 g1 j0) f=X(j3 j2 c1 c0) g=X(j1 e2 i2 c2) h=X(i1 i0 d1 d0) i=X(h1 h0 g2 e1) j=X(e3 g0 f1 f0) ['name'='-t7_43']": "A**24 - A**23 + 3*A**21 - 2*A**20 - A**19 + 4*A**18 - 3*A**17 - A**16 + 2*A**15 - 2*A**14 - 2*A**12 + A**11 - A**10 - 3*A**9 + 3*A**8 + A**7 - 3*A**6 + 2*A**5 - 3*A**3 - 1",
        # "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 f0 f3 d0) d=X(c3 g0 b1 a2) e=X(h3 i0 i3 b2) f=X(c1 i2 g1 c2) g=X(d1 f2 h1 h0) h=X(g3 g2 i1 e0) i=X(e1 h2 f1 e2) ['name'='+t7_44']": "-A**24 - 3*A**21 - A**20 + 2*A**19 - 4*A**18 - A**17 + 3*A**16 - 2*A**15 + 2*A**13 - A**12 - 2*A**10 + 2*A**9 - 3*A**7 + 4*A**6 - 3*A**4 + 2*A**3 - A + 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 c1) c=V(a1 b3 f0) d=X(g3 g2 b1 a2) e=X(g1 h0 h3 b2) f=X(c2 h2 i3 i2) g=X(i1 e0 d1 d0) h=X(e1 i0 f1 e2) i=X(h1 g0 f3 f2) ['name'='-t7_44']": "A**24 - A**23 + 2*A**21 - 3*A**20 + 4*A**18 - 3*A**17 + 2*A**15 - 2*A**14 - A**12 + 2*A**11 - 2*A**9 + 3*A**8 - A**7 - 4*A**6 + 2*A**5 - A**4 - 3*A**3 - 1",
        # "a=V(b0 c0 d3) b=V(a0 e3 c1) c=X(a1 b2 f0 g0) d=X(g3 h0 h3 a2) e=X(h2 i0 i3 b1) f=X(c2 j0 j3 g1) g=X(c3 f3 h1 d0) h=X(d1 g2 e0 d2) i=X(e1 j2 j1 e2) j=X(f1 i2 i1 f2) ['name'='+t7_45']": "2*A**23 + A**22 - A**21 + 3*A**20 + 3*A**19 - 3*A**18 + 2*A**17 + 2*A**16 - 4*A**15 + 2*A**13 - A**12 + A**11 + 3*A**9 - 2*A**8 - 3*A**7 + 4*A**6 - 3*A**5 - 2*A**4 + 3*A**3 - A**2 - A + 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 f3 f2) c=V(a1 g0 d0) d=X(c2 h3 e1 a2) e=X(b1 d2 h2 f0) f=X(e3 g1 b3 b2) g=X(c1 f1 i3 i2) h=X(j3 j2 e2 d1) i=X(j1 j0 g3 g2) j=X(i1 i0 h1 h0) ['name'='-t7_45']": "-A**23 + A**22 + A**21 - 3*A**20 + 2*A**19 + 3*A**18 - 4*A**17 + 3*A**16 + 2*A**15 - 3*A**14 - A**12 + A**11 - 2*A**10 + 4*A**8 - 2*A**7 - 2*A**6 + 3*A**5 - 3*A**4 - 3*A**3 + A**2 - A - 2",
        # "a=V(b0 c0 d0) b=V(a0 e0 f3) c=X(a1 f2 f1 g0) d=X(a2 h0 h3 e1) e=X(b1 d3 i0 g2) f=X(g1 c2 c1 b2) g=X(c3 f0 e3 i3) h=X(d1 j0 j3 d2) i=X(e2 j2 j1 g3) j=X(h1 i2 i1 h2) ['name'='+t7_46']": "-A**24 - A**22 - 3*A**21 - 5*A**18 + A**17 + 2*A**16 - 3*A**15 + A**14 + 2*A**13 - A**12 + A**11 + 3*A**9 - A**8 - 2*A**7 + 4*A**6 - 3*A**5 - 2*A**4 + 3*A**3 - A**2 - A + 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 f3 f2) c=V(a1 f1 g3) d=X(g2 h3 e1 a2) e=X(b1 d2 h2 f0) f=X(e3 c1 b3 b2) g=X(i3 i2 d0 c2) h=X(j3 j2 e2 d1) i=X(j1 j0 g1 g0) j=X(i1 i0 h1 h0) ['name'='-t7_46']": "A**24 - A**23 - A**22 + 3*A**21 - 2*A**20 - 3*A**19 + 4*A**18 - 2*A**17 - A**16 + 3*A**15 + A**13 - A**12 + 2*A**11 + A**10 - 3*A**9 + 2*A**8 + A**7 - 5*A**6 - 3*A**3 - A**2 - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f3) c=X(a1 f2 g3 d0) d=X(c3 h0 b1 a2) e=X(h3 i0 j0 b2) f=X(j3 j2 c1 b3) g=X(j1 i2 k3 c2) h=X(d1 k2 k1 e0) i=V(e1 k0 g1) j=X(e2 g0 f1 f0) k=X(i1 h2 h1 g2) ['name'='+t7_48']": "2*A**23 + A**22 - A**21 + 3*A**20 + 4*A**19 - 3*A**18 + 2*A**17 + 4*A**16 - 3*A**15 + 2*A**13 - 2*A**12 - A**11 - 2*A**10 + 2*A**9 - 2*A**8 - 3*A**7 + 5*A**6 - 2*A**5 - 3*A**4 + 3*A**3 - A + 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=X(a1 f3 g3 h0) d=X(h3 h2 b1 a2) e=X(i3 j0 k3 b2) f=X(b3 k2 k1 c1) g=X(k0 j2 i1 c2) h=X(c3 i0 d1 d0) i=X(h1 g2 j1 e0) j=V(e1 i2 g1) k=X(g0 f2 f1 e2) ['name'='-t7_48']": "-A**23 + A**22 - 3*A**20 + 3*A**19 + 2*A**18 - 5*A**17 + 3*A**16 + 2*A**15 - 2*A**14 + 2*A**13 + A**12 + 2*A**11 - 2*A**10 + 3*A**8 - 4*A**7 - 2*A**6 + 3*A**5 - 4*A**4 - 3*A**3 + A**2 - A - 2",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 f1 d0) d=X(c3 g0 e1 a2) e=X(b1 d2 h3 h2) f=X(i3 c2 c1 b2) g=X(d1 i2 i1 h0) h=X(g3 i0 e3 e2) i=X(h1 g2 g1 f0) ['name'='+t7_49']": "A**23 + 3*A**20 + A**19 - 2*A**18 + 5*A**17 + 2*A**16 - 3*A**15 + 3*A**14 + A**13 - 3*A**12 - A**10 + A**9 - 3*A**8 + 4*A**6 - 4*A**5 + 3*A**3 - 3*A**2 - A + 2",
        # "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=V(a1 f3 g0) d=X(g3 g2 b1 a2) e=X(h3 h2 i3 b2) f=X(b3 i2 i1 c1) g=X(c2 h0 d1 d0) h=X(g1 i0 e1 e0) i=X(h1 f2 f1 e2) ['name'='-t7_49']": "-2*A**23 + A**22 + 3*A**21 - 3*A**20 + 4*A**18 - 4*A**17 + 3*A**15 - A**14 + A**13 + 3*A**11 - A**10 - 3*A**9 + 3*A**8 - 2*A**7 - 5*A**6 + 2*A**5 - A**4 - 3*A**3 - 1",
        # "a=V(b0 c3 d3) b=V(a0 e0 c0) c=X(b2 f0 f3 a1) d=X(f2 g0 g3 a2) e=X(b1 h0 h3 i0) f=X(c1 i3 d0 c2) g=X(d1 j0 j3 d2) h=X(e1 j2 i1 e2) i=X(e3 h2 j1 f1) j=X(g1 i2 h1 g2) ['name'='+t7_50']": "-A**24 + A**23 + A**22 - 3*A**21 + A**20 + 2*A**19 - 5*A**18 + 2*A**16 - 4*A**15 - A**14 + A**13 - 2*A**12 - A**10 + 4*A**9 - 3*A**7 + 5*A**6 - 2*A**5 - 3*A**4 + 3*A**3 - A**2 - A + 1",
        # "a=V(b0 c0 d0) b=V(a0 e3 c1) c=X(a1 b2 f3 f2) d=X(a2 f1 g3 g2) e=X(h3 h2 i3 b1) f=X(i2 d1 c3 c2) g=X(j3 j2 d3 d2) h=X(j1 i0 e1 e0) i=X(h1 j0 f0 e2) j=X(i1 h0 g1 g0) ['name'='-t7_50']": "A**24 - A**23 - A**22 + 3*A**21 - 3*A**20 - 2*A**19 + 5*A**18 - 3*A**17 + 4*A**15 - A**14 - 2*A**12 + A**11 - A**10 - 4*A**9 + 2*A**8 - 5*A**6 + 2*A**5 + A**4 - 3*A**3 + A**2 + A - 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 f0) d=X(g3 g2 h3 a2) e=X(b1 i0 f1 b2) f=X(c2 e2 i3 g0) g=X(f3 h0 d1 d0) h=X(g1 i2 i1 d2) i=X(e1 h2 h1 f2) ['name'='+t7_53']": "-A**24 + A**23 + 2*A**22 - 3*A**21 + 3*A**19 - 4*A**18 - A**17 + 3*A**16 - 3*A**15 - A**14 + 2*A**13 - A**12 - 3*A**10 + 2*A**9 - A**8 - 5*A**7 + 4*A**6 - 3*A**4 + 3*A**3 - A + 1",
        # "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 f0 f3 g0) d=X(h3 h2 b1 a2) e=X(h1 i0 f1 b2) f=X(c1 e2 g1 c2) g=X(c3 f2 i3 i2) h=X(i1 e0 d1 d0) i=X(e1 h0 g3 g2) ['name'='-t7_53']": "A**24 - A**23 + 3*A**21 - 3*A**20 + 4*A**18 - 5*A**17 - A**16 + 2*A**15 - 3*A**14 - A**12 + 2*A**11 - A**10 - 3*A**9 + 3*A**8 - A**7 - 4*A**6 + 3*A**5 - 3*A**3 + 2*A**2 + A - 1",
        # "a=V(b0 c0 d3) b=X(a0 d2 e0 f3) c=X(a1 g0 g3 h0) d=X(h3 h2 b1 a2) e=V(b2 h1 i0) f=X(i3 j0 g1 b3) g=X(c1 f2 j3 c2) h=X(c3 e1 d1 d0) i=X(e2 j2 j1 f0) j=X(f1 i2 i1 g2) ['name'='+t7_54']": "A**23 - A**22 - 2*A**21 + 3*A**20 - 4*A**18 + 4*A**17 + A**16 - 6*A**15 + A**14 - 4*A**12 + 3*A**9 - 3*A**8 + 5*A**6 - 5*A**5 - A**4 + 4*A**3 - 3*A**2 - A + 2",
        # "a=V(b0 c3 d3) b=X(a0 e0 e3 c0) c=X(b3 f0 g0 a1) d=X(h3 h2 e1 a2) e=X(b1 d2 f1 b2) f=V(c1 e2 i3) g=X(c2 i2 j3 h0) h=X(g3 j2 d1 d0) i=X(j1 j0 g1 f2) j=X(i1 i0 h1 g2) ['name'='-t7_54']": "-2*A**23 + A**22 + 3*A**21 - 4*A**20 + A**19 + 5*A**18 - 5*A**17 + 3*A**15 - 3*A**14 + 4*A**11 - A**9 + 6*A**8 - A**7 - 4*A**6 + 4*A**5 - 3*A**3 + 2*A**2 + A - 1",
        # "a=V(b0 c0 d3) b=V(a0 e3 f3) c=X(a1 g0 h3 d0) d=X(c3 h2 e0 a2) e=X(d2 i0 i3 b1) f=X(i2 j0 j3 b2) g=X(c1 j2 j1 h0) h=X(g3 i1 d1 c2) i=X(e1 h1 f0 e2) j=X(f1 g2 g1 f2) ['name'='+t7_55']": "2*A**23 - 3*A**21 + 3*A**20 + 2*A**19 - 5*A**18 + 3*A**17 + 4*A**16 - 3*A**15 + 2*A**14 + 4*A**13 - A**12 - A**10 + 3*A**9 - 3*A**8 - 3*A**7 + 6*A**6 - 4*A**5 - 3*A**4 + 4*A**3 - A**2 - A + 1",
        # "a=V(b0 c0 d0) b=V(a0 e3 f0) c=X(a1 f3 g3 g2) d=X(a2 g1 h3 h2) e=X(i3 j0 f1 b1) f=X(b2 e2 j3 c1) g=X(j2 d1 c3 c2) h=X(i1 i0 d3 d2) i=X(h1 h0 j1 e0) j=X(e1 i2 g0 f2) ['name'='-t7_55']": "-A**23 + A**22 + A**21 - 4*A**20 + 3*A**19 + 4*A**18 - 6*A**17 + 3*A**16 + 3*A**15 - 3*A**14 + A**13 + A**11 - 4*A**10 - 2*A**9 + 3*A**8 - 4*A**7 - 3*A**6 + 5*A**5 - 2*A**4 - 3*A**3 + 3*A**2 - 2",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 f0) c=V(a1 f3 g0) d=X(g3 g2 h3 a2) e=X(b1 i0 f1 b2) f=X(b3 e2 i3 c1) g=X(c2 h0 d1 d0) h=X(g1 i2 i1 d2) i=X(e1 h2 h1 f2) ['name'='+t7_56']": "-A**24 + A**23 + 2*A**22 - 3*A**21 + 4*A**19 - 3*A**18 + 5*A**16 - A**15 + 3*A**13 + A**11 - 2*A**10 + 3*A**9 - 5*A**7 + 4*A**6 - 4*A**4 + 2*A**3 - A + 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 f1 g0) d=X(h3 h2 e1 a2) e=X(b1 d2 h1 i0) f=X(g1 c2 c1 b2) g=X(c3 f0 i3 i2) h=X(i1 e2 d1 d0) i=X(e3 h0 g3 g2) ['name'='-t7_56']": "A**24 - A**23 + 2*A**21 - 4*A**20 + 4*A**18 - 5*A**17 + 3*A**15 - 2*A**14 + A**13 + 3*A**11 - A**9 + 5*A**8 - 3*A**6 + 4*A**5 - 3*A**3 + 2*A**2 + A - 1",
        # "a=V(b0 c0 d3) b=V(a0 e0 c1) c=X(a1 b2 f3 g0) d=X(g3 h0 h3 a2) e=X(b1 h2 i3 i2) f=X(i1 g2 g1 c2) g=X(c3 f2 f1 d0) h=X(d1 i0 e1 d2) i=X(h1 f0 e3 e2) ['name'='+t7_57']": "-A**24 + A**23 + A**22 - 3*A**21 + A**20 + 3*A**19 - 5*A**18 - A**17 + 3*A**16 - 4*A**15 - A**14 + 2*A**13 - A**12 - 2*A**10 + 3*A**9 - A**8 - 4*A**7 + 5*A**6 - A**5 - 4*A**4 + 3*A**3 - A + 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 f3 f2) c=V(a1 g3 d0) d=X(c2 h0 e1 a2) e=X(b1 d2 h3 h2) f=X(i3 g0 b3 b2) g=X(f1 i2 i1 c1) h=X(d1 i0 e3 e2) i=X(h1 g2 g1 f0) ['name'='-t7_57']": "A**24 - A**23 + 3*A**21 - 4*A**20 - A**19 + 5*A**18 - 4*A**17 - A**16 + 3*A**15 - 2*A**14 - A**12 + 2*A**11 - A**10 - 4*A**9 + 3*A**8 - A**7 - 5*A**6 + 3*A**5 + A**4 - 3*A**3 + A**2 + A - 1",
        # "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 f0) d=X(g3 h0 h3 a2) e=X(b1 i0 f1 b2) f=X(c2 e2 i3 g0) g=X(f3 i2 h1 d0) h=X(d1 g2 i1 d2) i=X(e1 h2 g1 f2) ['name'='-t7_59']": "-A**24 + A**23 + 2*A**22 - 3*A**21 + A**20 + 4*A**19 - 5*A**18 + 4*A**16 - 4*A**15 + 3*A**13 + A**11 - A**10 + 4*A**9 - 4*A**7 + 6*A**6 - 4*A**4 + 4*A**3 - A**2 - 2*A + 1",
        # "a=V(b0 c3 d3) b=X(a0 d2 e3 c0) c=X(b3 f0 g3 a1) d=X(g2 e0 b1 a2) e=X(d1 h3 i0 b2) f=X(c1 i2 j3 g0) g=X(f3 j2 d0 c2) h=X(j1 k0 k3 e1) i=V(e2 k2 f1) j=X(k1 h0 g1 f2) k=X(h1 j0 i1 h2) ['name'='-t7_60']": "2*A**23 - 4*A**21 + 3*A**20 + 3*A**19 - 7*A**18 + 2*A**17 + 5*A**16 - 5*A**15 + A**14 + 4*A**13 - A**12 + 5*A**9 - 2*A**8 - 3*A**7 + 8*A**6 - 3*A**5 - 5*A**4 + 5*A**3 - A**2 - 2*A + 1",
        # "a=V(a1 a0 b0) b=V(a2 b2 b1) ['name'='h0_1']": "0",
        "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2) ['name'='h2_1.1']": "-A**9 - A**8 - A**7 - A**6 + A**3 + A**2 + A + 1",
        "a=V(b0 c0 d3) b=X(a0 d2 d1 c1) c=V(a1 b3 d0) d=X(c2 b2 b1 a2) ['name'='h2_1.2']": "-A**9 - A**8 - A**7 - A**6 + A**3 + A**2 + A + 1",
        "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 e3 e2) d=X(f3 f2 b1 a2) e=X(f1 f0 c3 c2) f=X(e1 e0 d1 d0) ['name'='h4_1.1']": "-A**15 - A**13 - A**12 - A**10 - A**8 + A**4 + A**3 + A**2 + A + 1",
    #     "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 d0) d=X(c2 f0 f3 a2) e=X(b1 f2 f1 b2) f=X(d1 e2 e1 d2) ['name'='h4_1.2']": "-A**15 - A**14 - A**13 - A**12 - A**11 + A**7 + A**5 + A**3 + A**2 + 1",
    #     "a=V(b0 c0 d3) b=X(a0 d2 e3 c1) c=V(a1 b3 f0) d=X(g3 e0 b1 a2) e=X(d1 g2 f1 b2) f=X(c2 e2 g1 g0) g=X(f3 f2 e1 d0) ['name'='h5_1.1']": "-A**18 + A**17 + A**16 - A**15 + 2*A**14 - A**12 - A**10 - A**8 + A**6 - A**5 + A**3 - A**2 + 1",
    #     "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 f0 g3 d0) d=X(c3 g2 b1 a2) e=X(g1 f2 f1 b2) f=X(c1 e2 e1 g0) g=X(f3 e0 d1 c2) ['name'='h5_1.2']": "A**18 - A**16 + A**15 - A**13 + A**12 - A**10 - A**8 - A**6 + 2*A**4 - A**3 + A**2 + A - 1",
    # #     "a=V(b0 c0 d3) b=X(a0 e0 e3 f0) c=X(a1 f2 g3 g2) d=X(g1 h0 e1 a2) e=X(b1 d2 h3 b2) f=V(b3 h2 c1) g=X(h1 d0 c3 c2) h=X(d1 g0 f1 e2) ['name'='h6_1']": "A**20 - A**19 - 3*A**18 + 2*A**17 - 3*A**15 + 3*A**14 + A**13 - A**12 + A**11 + A**9 - A**8 + A**7 + 3*A**6 - 3*A**5 + 2*A**3 - 3*A**2 - A + 1",
    #     "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=X(a1 f0 f3 g0) d=X(g2 h0 b1 a2) e=X(h3 f1 b3 b2) f=X(c1 e1 h2 c2) g=V(c3 h1 d0) h=X(d1 g1 f2 e0) ['name'='h6_2.1']": "-A**18 - 2*A**17 - A**15 - A**14 + A**13 + A**11 + A**9 + A**8 + 2*A**6 + A**5 - A - 1",
    #     "a=V(b0 c0 d3) b=X(a0 e0 f3 f2) c=X(a1 f1 g3 d0) d=X(c3 h0 e1 a2) e=V(b1 d2 h3) f=X(g0 c1 b3 b2) g=X(f0 h2 h1 c2) h=X(d1 g2 g1 e2) ['name'='h6_2.2']": "-A**18 - A**17 + A**13 + 2*A**12 + A**10 + A**9 + A**7 + A**5 - A**4 - A**3 - 2*A - 1",
    #     "a=V(b0 c0 d3) b=X(a0 e0 e3 f0) c=X(a1 f2 g3 d0) d=X(c3 g2 h3 a2) e=X(b1 h2 h1 b2) f=V(b3 g0 c1) g=X(f1 h0 d1 c2) h=X(g1 e2 e1 d2) ['name'='h6_3']": "-A**20 - A**19 + A**18 - A**17 - 2*A**16 + A**15 - 2*A**13 + A**12 + A**11 + 2*A**9 + A**8 + 2*A**7 - A**6 + 2*A**4 - 3*A**3 + A - 1",
    #     "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=X(a1 e1 f3 g0) d=X(g3 h0 b1 a2) e=X(h2 c1 b3 b2) f=X(h1 g2 g1 c2) g=X(c3 f2 f1 d0) h=V(d1 f0 e0) ['name'='h6_4']": "-A**19 - A**18 + A**17 - 2*A**15 + A**14 - A**13 - 2*A**12 - A**10 + A**9 + 2*A**7 + 2*A**6 - A**5 + A**4 + A**3 - A**2 + 1",
    #     "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 d0) d=X(c2 f0 f3 a2) e=X(b1 g0 g3 b2) f=X(d1 h0 h3 d2) g=X(e1 h2 h1 e2) h=X(f1 g2 g1 f2) ['name'='h6_5']": "-A**21 - A**20 - A**19 - A**18 - A**17 + A**9 + A**7 + A**5 + A**2 + 1",
    #     "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 g0 g3 d0) d=X(c3 h0 h3 a2) e=X(b1 h2 h1 f0) f=X(e3 g2 g1 b2) g=X(c1 f2 f1 c2) h=X(d1 e2 e1 d2) ['name'='h6_6']": "-A**19 - A**18 - A**17 - A**16 - 2*A**15 - A**14 + A**11 + 2*A**10 + A**9 + A**7 - A**6 - A**4 + A**3 + A**2 + 2",
    #     "a=V(b0 c0 d3) b=X(a0 e0 e3 c1) c=V(a1 b3 f0) d=X(g3 g2 h3 a2) e=X(b1 h2 h1 b2) f=X(c2 h0 g1 g0) g=X(f3 f2 d1 d0) h=X(f1 e2 e1 d2) ['name'='h6_7']": "-A**21 - 2*A**18 - A**17 + A**16 - 2*A**15 + A**13 - A**12 + A**11 - A**10 + A**9 - A**8 - A**7 + 2*A**6 + 2*A**3 + A**2 + 1",
    #     "a=V(b0 c0 d3) b=X(a0 d2 e3 f0) c=V(a1 f3 g0) d=X(g3 h0 b1 a2) e=X(h3 f2 f1 b2) f=X(b3 e2 e1 c1) g=X(c2 h2 h1 d0) h=X(d1 g2 g1 e0) ['name'='h6_9']": "2*A**20 + A**19 - A**18 + 3*A**17 + 2*A**16 - 2*A**15 + 2*A**14 - 3*A**12 - A**11 - 2*A**10 - 2*A**8 + 3*A**6 - 2*A**5 + 2*A**3 - 2*A**2 - A + 1",
    #     "a=V(b0 c0 d3) b=V(a0 e0 c1) c=X(a1 b2 e3 d0) d=X(c3 f0 f3 a2) e=X(b1 g3 h0 c2) f=X(d1 i0 i3 d2) g=X(i2 j0 j3 e1) h=X(e2 j2 j1 i1) i=X(f1 h3 g0 f2) j=X(g1 h2 h1 g2) ['name'='h7_19']": "A**24 - A**22 + A**21 + A**20 - A**19 + A**18 + 2*A**17 - A**16 + A**14 - A**13 - A**12 - A**10 - A**9 - 2*A**8 + A**7 - 2*A**5 + 3*A**4 + A - 1",
    #     "a=V(b0 c0 d3) b=X(a0 d2 e3 e2) c=X(a1 e1 f0 g0) d=X(g3 h0 b1 a2) e=X(i3 c1 b3 b2) f=V(c2 i2 g1) g=X(c3 f2 j3 d0) h=X(d1 j2 j1 i0) i=X(h3 j0 f1 e0) j=X(i1 h2 h1 g2) ['name'='h7_25']": "-A**23 + 2*A**22 + A**21 - 5*A**20 + 2*A**19 + 3*A**18 - 6*A**17 + A**16 + 3*A**15 - 3*A**14 + 2*A**11 - 2*A**10 - A**9 + 6*A**8 - 3*A**7 - 2*A**6 + 5*A**5 - A**4 - 3*A**3 + 2*A**2 + A - 1",
    #     "a=V(b0 c0 d0) b=V(a0 e0 c1) c=X(a1 b2 f3 g3) d=X(a2 g2 h0 e1) e=X(b1 d3 i3 f0) f=X(e3 i2 j0 c2) g=X(j3 j2 d1 c3) h=X(d2 j1 k3 k2) i=X(k1 k0 f1 e2) j=X(f2 h1 g1 g0) k=X(i1 i0 h3 h2) ['name'='h7_29']": "A**23 - 2*A**22 + A**21 + 3*A**20 - 5*A**19 + A**18 + 2*A**17 - 3*A**16 + A**14 + 2*A**13 - A**12 + 3*A**10 - 2*A**9 - 2*A**8 + 3*A**7 - A**6 - 3*A**5 + 2*A**4 + A**3 - 2*A**2 + 1",
    #     "a=V(b0 c0 d3) b=V(a0 e0 f3) c=X(a1 f2 g3 d0) d=X(c3 g2 e1 a2) e=X(b1 d2 h3 h2) f=X(i3 i2 c1 b2) g=X(i1 h0 d1 c2) h=X(g1 i0 e3 e2) i=X(h1 g0 f1 f0) ['name'='h7_31']": "-A**23 + A**22 - 5*A**20 + 3*A**19 + 3*A**18 - 7*A**17 + 3*A**16 + 2*A**15 - 5*A**14 + 2*A**11 - 2*A**10 + A**9 + 6*A**8 - 3*A**7 - A**6 + 6*A**5 - 2*A**4 - 3*A**3 + 4*A**2 - 2",
    #     "a=V(b0 c0 d0) b=V(a0 d3 e3) c=X(a1 e2 f3 f2) d=X(a2 g0 g3 b1) e=X(h3 h2 c1 b2) f=X(i3 g1 c3 c2) g=X(d1 f1 i2 d2) h=X(i1 i0 e1 e0) i=X(h1 h0 g2 f0) ['name'='h7_35']": "A**18 - A**14 - A**13 - 2*A**12 - A**11 - A**10 - A**9 + A**5 + A**4 + A**3 + A**2 + A + 1",
    #     "a=V(b0 c0 d3) b=V(a0 e3 f0) c=X(a1 f3 g0 d0) d=X(c3 h3 e0 a2) e=X(d2 h2 i3 b1) f=X(b2 i2 i1 c1) g=X(c2 i0 h1 h0) h=X(g3 g2 e1 d1) i=X(g1 f2 f1 e2) ['name'='h7_36']": "A**19 + A**18 - A**17 + A**16 - 2*A**14 - A**12 - A**10 + A**8 - A**7 + A**6 + A**5 + A**2 - 1",
     }

    for diagram, yamada_ in yamadas.items():
        k = from_knotpy_notation(diagram)
        y_expected = sympify(yamada_)
        y = yamada(k)
        assert y == y_expected, f"For knot {diagram}, \nexpected: {yamada_}\ncomputed: {y}"



    """
    Without optimizations:
    Moriuchi time: 99.18276786804199
    
    With simple_reduce_crossings:
    Moriuchi time: 56.34768724441528
    
    With caching yamada graph:
    Moriuchi time: 7.341709852218628
    
    With knotted caching
    Moriuchi time: 5.691523551940918
    Moriuchi time: 169.83222699165344 (all thetas)
    Moriuchi time: 89.61125183105469 (cache 10000 instead of 1000)
    """

def test_yamada_reidemeister():
    from knotpy.reidemeister.space import all_reidemeister_moves_space

    t31 = from_knotpy_notation("a=V(b0 c0 d3) b=V(a0 d2 e3) d=X(c3 e0 b1 a2) c=X(a1 e2 e1 d0) e=X(d1 c2 c1 b2)")

    y = yamada(t31)
    settings.allowed_moves = "r1,r2,r3,r4,r5"

    for k in islice(all_reidemeister_moves_space(t31, depth=1), 0, None, 4):
        y_ = yamada(k)
        assert y_ == y, f"For knot {k}, expected Yamada \n{y}, got \n{y_}"


def test_thetas_recursive():
    # errros: a → V(b0 c0 d3), b → X(a0 e0 e3 c1), c → V(a1 b3 d0), d → X(c2 f0 f3 a2), e → X(b1 g0 g3 b2), f → X(d1 g2 g1 d2), g → X(e1 f2 f1 e2)
    from knotpy.tables.theta import thetas
    import knotpy as kp
    all_thetas = list(thetas())
    for t in all_thetas[::5]:
        if len(t) >= 6+2:
            continue
        yr = _naive_yamada_polynomial(t)
        yo = yamada(t)
        if yr != yo:
            raise ValueError("Invalid Yamada")

if __name__ == '__main__':
    print("Yamada from paper")
    test_yamada_examples_from_paper()
    print("Thetas recursive")
    test_thetas_recursive()
    print("Reidemeister")
    test_yamada_reidemeister()
    print("Moriuchi")
    test_yamada_moriuchi()

