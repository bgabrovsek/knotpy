from knotpy import sanity_check, from_pd_notation
from knotpy.notation.native import from_knotpy_notation
from knotpy.invariants.yamada_colored import colored_yamada_polynomial
from knotpy.classes.convert import vertices_to_crossings
from sympy import expand, sympify
from knotpy.invariants.yamada import yamada_polynomial

def module2str(m: dict):
    if not m:
        return "0"
    #for g in m.values():
    return " + ".join(f"({expand(c)})[{str(g).replace('Diagram ','')}]" for g, c in m.items())


def test_colored_yamada_graph():
    theta_2 = "a=V(b0 b2 x3) b=V(a0 x0 a1) x=V(b1 x2 x1 a2) [;;a0:{'color'=1} b0:{'color'=1}]"
    #theta_2 = "a=V(b0 b1) b=V(a0 a1 x0) x=V(b2 x2 x1) [;;a0:{'color'=1} b0:{'color'=1}]"  # has bridge, ok
    #theta_2 = "a=V(b0 b2 a3 a2 b1) b=V(a0 a4 a1) [;;a0:{'color'=1} b0:{'color'=1}]"  # not ok, should be 2 + 1/A^2 + 1/A + A + A^2 but is A**4 + A**3 + 2*A**2 + A + 1

    #theta_2 = "a=V(b0 a2 a1 b1) b=V(a0 a3) [;;a0:{'color'=1} b0:{'color'=1}]" ok

    theta_2 = "a=V(b0 b2 b1) b=V(a0 a2 a1) c=V(c1 c0) ['framing'=0,'A'=0,'B'=1,'X'=0; ; a0:{'color'=1} b0:{'color'=1}]"

    k_2 = from_knotpy_notation(theta_2)

    y_2 = colored_yamada_polynomial(k_2, normalize=False)

    print(module2str(y_2))

    # 2 + 1/A^2 + 1/A + A + A^2

def test_colored_yamada_trivial():
    theta_1 = "a=V(b0 b2 b1) b=V(a0 a2 a1) [;;a0:{'color'=1} b0:{'color'=1}]"
    theta_2 = "a=V(b0 b2 x3) b=V(a0 x0 a1) x=X(b1 x2 x1 a2) [;;a0:{'color'=1} b0:{'color'=1}]"


    a1 = "a=V(b0 b2 x3) b=V(a0 x0 a1) x=V(b1 x2 x1 a2) ['framing'=0,'A'=0,'B'=0,'X'=1; ; a0:{'color'=1} b0:{'color'=1}]"
    a2 = "a=V(b0 b2 b1) b=V(a0 a2 a1) c=V(c1 c0) ['framing'=0,'A'=0,'B'=1,'X'=0; ; a0:{'color'=1} b0:{'color'=1}]"
    a3 = "a=V(b0 b2 b1) b=V(a0 a2 a1) ['framing'=0,'A'=1,'B'=0,'X'=0; ; a0:{'color'=1} b0:{'color'=1}]"

    k_1 = from_knotpy_notation(theta_1)
    k_2 = from_knotpy_notation(theta_2)

    print("\n=============================================\n")

    y_1 = colored_yamada_polynomial(k_1)
    print("\n=============================================\n")
    y_2 = colored_yamada_polynomial(k_2)
    print("\n=============================================\n")

    print(module2str(y_1))
    print(module2str(y_2))


    yy1 = colored_yamada_polynomial(from_knotpy_notation(a1), normalize=False)
    yy2 = colored_yamada_polynomial(from_knotpy_notation(a2), normalize=False)
    yy3 = colored_yamada_polynomial(from_knotpy_notation(a3), normalize=False)

    print(module2str(yy1))
    print(module2str(yy2))
    print(module2str(yy3))



def test_colored_yamada_one_bond():

    # 3_1 theta curve
    theta_1 = "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 e1 d0) d=X(c3 e0 b1 a2) e=X(d1 c2 c1 b2) [;;a0:{'color'=1} b0:{'color'=1}]"

    # 3_1 with R1 kink
    theta_2 = "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 x0 d0) d=X(c3 e0 b1 a2) e=X(d1 x3 c1 b2) x=X(c2 x2 x1 e1) [;;a0:{'color'=1} b0:{'color'=1}]"

    # 31 with R2 move
    theta_3 = "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 x3 x2 d0) d=X(c3 e0 b1 a2) e=X(d1 y2 y1 b2) x=X(y0 y3 c2 c1) y=X(x0 e2 e1 x1) [;;a0:{'color'=1} b0:{'color'=1}]"


    # 31 with R4 kink
    theta_4 = "a=V(b0 c0 d3) b=V(a0 x0 x3) c=X(a1 e2 e1 d0) d=X(c3 e0 x1 a2) e=X(d1 c2 c1 x2) x=X(b1 d3 e3 b2) [;;a0:{'color'=1} b0:{'color'=1}]"


    k_1 = from_knotpy_notation(theta_1)
    k_2 = from_knotpy_notation(theta_2)
    k_3 = from_knotpy_notation(theta_3)
    k_4 = from_knotpy_notation(theta_4)

    print(k_1)
    print(k_2)
    print(k_3)
    print(k_4)


    yamada_1 = colored_yamada_polynomial(k_1)
    yamada_2 = colored_yamada_polynomial(k_2)
    yamada_3 = colored_yamada_polynomial(k_3)
    yamada_4 = colored_yamada_polynomial(k_3)

    print(module2str(yamada_1))
    print(module2str(yamada_2))
    print(module2str(yamada_3))
    print(module2str(yamada_4))

    assert yamada_1 == yamada_2

    assert yamada_1 == yamada_3

    assert yamada_1 == yamada_4

    pass

def color_endpoints(k):
    for ep1, ep2 in k.arcs:
        if ep1.node in k.vertices and ep2.node in k.vertices:

            if all("color" not in ep.attr for ep in k.nodes[ep1.node]) and all("color" not in ep.attr for ep in k.nodes[ep2.node]):

                ep1.attr = {"color": 1}
                ep2.attr = {"color": 1}


def test_colored_yamada_three_bonds():
    code1 = "[[11,19,12],[1,19,18],[20,3,4],[23,20,9],[15,21,16],[7,8,21],[23,8,22,22],[15,6,14,7],[9,17,10,16],[6,10,5,11],[17,4,18,5],[3,14,2,13],[12,1,13,2]]"
    k1 = from_pd_notation(code1)
    vertices_to_crossings(k1)
    color_endpoints(k1)
    sanity_check(k1)
    print(k1)

    exit()

    y = colored_yamada_polynomial(k1)

def test_colored_yamada_two_bonds():
    from time import time

    b1 = "[[0,2,3],[0,5,6],[1,8,7],[1,13,14],[10,3,11,4],[2,12,15,11],[4,9,5,10],[8,14,9,15],[12,6,13,7]]"  # combined arcs of 5_6 and 5_7 from Yamada
    b2 = "[[0,16,17],[0,5,6],[1,8,7],[1,13,14],[10,3,11,4],[2,12,15,11],[4,9,5,10],[8,14,9,15],[12,6,13,7],[2,3,17,16]]"  # added R4 twist
    b3 = "[[0,2,3],[0,5,6],[1,15,14],[1,8,9],[10,3,11,4],[2,12,15,11],[4,9,5,10],[8,14,7,13],[12,6,13,7]]"  # added R5 twist + R2


    k1 = makeit(b1)
    k2 = makeit(b2)
    k3 = makeit(b3)

    t = time()
    cy1 = colored_yamada_polynomial(k1)
    print("Colored yamada:", cy1, time() - t)

    t = time()
    cy2 = colored_yamada_polynomial(k2)
    print("Colored yamada:", cy2, time() - t)

    t = time()
    cy3 = colored_yamada_polynomial(k3)
    print("Colored yamada:", cy3, time() - t)

    """
    
    
    {Diagram a → V(a1 a0 a3 a2): A**15 - A**14 - 4*A**13 + 4*A**12 - A**11 - 13*A**10 + 12*A**9 + 14*A**8 - 27*A**7 + 7*A**6 + 16*A**5 - 13*A**4 - A**3 + 4*A**2 - A, 
     Diagram a → V(b0 b1), b → V(a0 a1): A**12 - 3*A**11 - 4*A**10 + 9*A**9 + 7*A**8 - 15*A**7 - 3*A**6 + 15*A**5 - 3*A**4 - 8*A**3 + 3*A**2 + A - 1, 
    Diagram named a → V(a1 a0), b → V(b1 b0): A**16 - A**15 - A**13 - 2*A**12 - A**11 + A**10 - 2*A**9 + 2*A**8 - A**6 + A**5 - A**4}
   
    {Diagram a → V(a1 a0 a3 a2): A**15 - A**14 - 4*A**13 + 4*A**12 - A**11 - 13*A**10 + 12*A**9 + 14*A**8 - 27*A**7 + 7*A**6 + 16*A**5 - 13*A**4 - A**3 + 4*A**2 - A, 
     Diagram a → V(b0 b1), b → V(a0 a1): A**12 - 3*A**11 - 4*A**10 + 9*A**9 + 7*A**8 - 15*A**7 - 3*A**6 + 15*A**5 - 3*A**4 - 8*A**3 + 3*A**2 + A - 1, 
     Diagram named a → V(a1 a0), b → V(b1 b0): A**16 - A**15 - A**13 - 2*A**12 - A**11 + A**10 - 2*A**9 + 2*A**8 - A**6 + A**5 - A**4}
   
    {Diagram a → V(a1 a0 a3 a2): A**15 - 5*A**13 + 5*A**12 - 16*A**10 + 10*A**9 + 17*A**8 - 22*A**7 - A**6 + 15*A**5 - 7*A**4 - 3*A**3 + 4*A**2 - A, 
     Diagram a → V(b0 b1), b → V(a0 a1): 2*A**12 - 3*A**11 - 8*A**10 + 9*A**9 + 13*A**8 - 14*A**7 - 7*A**6 + 11*A**5 - 5*A**3 + A**2 + A - 1, 
     Diagram named a → V(a1 a0), b → V(b1 b0): A**16 - A**15 + A**14 - 2*A**13 - A**12 - A**11 - A**10}
   
    {Diagram a → V(a1 a0 a3 a2): -4*A**13 + 5*A**12 + 3*A**11 - 13*A**10 + 13*A**9 + 11*A**8 - 29*A**7 + 10*A**6 + 13*A**5 - 16*A**4 + A**3 + 5*A**2 - 2*A, 
     Diagram a → V(b0 b1), b → V(a0 a1): A**12 - 2*A**11 - 4*A**10 + 7*A**9 + 5*A**8 - 13*A**7 + 14*A**5 - 5*A**4 - 8*A**3 + 5*A**2 + A - 2, 
     Diagram named  a → V(a1 a0), b → V(b1 b0): A**16 - 2*A**15 + A**14 - A**13 - A**12 + 3*A**11 + A**8 - 3*A**7 - A**6 - A**5 - A**4}
    
    
    
    """




    # code1 = "[[0,6,7],[0,3,4],[1,9,8],[1,14,15],[3,13,2,12],[12,5,11,4],[5,10,6,11],[10,2,9,15],[13,7,14,8]]"
    # code2 = "[[0,16,17],[0,3,4],[1,9,8],[1,14,15],[16,6,7,17],[3,13,2,12],[12,5,11,4],[5,10,6,11],[10,2,9,15],[13,7,14,8]]"
    # code3 = "[[0,16,17],[0,3,4],[1,2,14],[1,9,10],[16,6,7,17],[3,13,2,12],[12,5,11,4],[5,10,6,11],[13,7,15,8],[8,15,9,14]]"
    # k1 = from_pd_notation(code1, normalize="crossing")
    # color_endpoints(k1)
    # sanity_check(k1)
    # print(k1)
    #
    # print("ok")
    #
    # k2 = from_pd_notation(code2, normalize="crossing")
    # color_endpoints(k2)
    # sanity_check(k2)
    # print(k2)
    # print("ok")
    #
    # k3 = from_pd_notation(code3, normalize="crossing")
    # color_endpoints(k3)
    # sanity_check(k3)
    # print(k3)
    # print("ok")
    #
    #
    # y1 = colored_yamada_polynomial(k1)
    # y2 = colored_yamada_polynomial(k2)
    # y3 = colored_yamada_polynomial(k3)
    #
    # print("____________")
    # print(y1)
    # print("____________")
    # print(y2)
    # print("____________")
    # print(y3)
    # print("____________")
    #
    # assert y1 == y2
    # assert y1 == y3

    """!
    {Diagram a → V(a1 a0 a3 a2): A**15 - A**14 - 4*A**13 + 4*A**12 - A**11 - 13*A**10 + 12*A**9 + 14*A**8 - 27*A**7 + 7*A**6 + 16*A**5 - 13*A**4 - A**3 + 4*A**2 - A, 
    Diagram a → V(b0 b1), b → V(a0 a1): A**12 - 3*A**11 - 4*A**10 + 9*A**9 + 7*A**8 - 15*A**7 - 3*A**6 + 15*A**5 - 3*A**4 - 8*A**3 + 3*A**2 + A - 1, 
    Diagram named  (disjoint component)⊔ (disjoint component) a → V(a1 a0), b → V(b1 b0): A**16 - A**15 - A**13 - 2*A**12 - A**11 + A**10 - 2*A**9 + 2*A**8 - A**6 + A**5 - A**4}

"""

    exit()

def test_expressions():

    """

    Returns:

    {Diagram a → V(a1 a0 a3 a2): A**15 - A**14 - 4*A**13 + 4*A**12 - A**11 - 13*A**10 + 12*A**9 + 14*A**8 - 27*A**7 + 7*A**6 + 16*A**5 - 13*A**4 - A**3 + 4*A**2 - A,
     Diagram a → V(b0 b1), b → V(a0 a1): A**12 - 3*A**11 - 4*A**10 + 9*A**9 + 7*A**8 - 15*A**7 - 3*A**6 + 15*A**5 - 3*A**4 - 8*A**3 + 3*A**2 + A - 1,
    Diagram named a → V(a1 a0), b → V(b1 b0): A**16 - A**15 - A**13 - 2*A**12 - A**11 + A**10 - 2*A**9 + 2*A**8 - A**6 + A**5 - A**4}

    {Diagram a → V(a1 a0 a3 a2): A**15 - A**14 - 4*A**13 + 4*A**12 - A**11 - 13*A**10 + 12*A**9 + 14*A**8 - 27*A**7 + 7*A**6 + 16*A**5 - 13*A**4 - A**3 + 4*A**2 - A,
     Diagram a → V(b0 b1), b → V(a0 a1): A**12 - 3*A**11 - 4*A**10 + 9*A**9 + 7*A**8 - 15*A**7 - 3*A**6 + 15*A**5 - 3*A**4 - 8*A**3 + 3*A**2 + A - 1,
     Diagram named a → V(a1 a0), b → V(b1 b0): A**16 - A**15 - A**13 - 2*A**12 - A**11 + A**10 - 2*A**9 + 2*A**8 - A**6 + A**5 - A**4}

    {Diagram a → V(a1 a0 a3 a2): A**15 - 5*A**13 + 5*A**12 - 16*A**10 + 10*A**9 + 17*A**8 - 22*A**7 - A**6 + 15*A**5 - 7*A**4 - 3*A**3 + 4*A**2 - A,
     Diagram a → V(b0 b1), b → V(a0 a1): 2*A**12 - 3*A**11 - 8*A**10 + 9*A**9 + 13*A**8 - 14*A**7 - 7*A**6 + 11*A**5 - 5*A**3 + A**2 + A - 1,
     Diagram named a → V(a1 a0), b → V(b1 b0): A**16 - A**15 + A**14 - 2*A**13 - A**12 - A**11 - A**10}

    {Diagram a → V(a1 a0 a3 a2): -4*A**13 + 5*A**12 + 3*A**11 - 13*A**10 + 13*A**9 + 11*A**8 - 29*A**7 + 10*A**6 + 13*A**5 - 16*A**4 + A**3 + 5*A**2 - 2*A,
     Diagram a → V(b0 b1), b → V(a0 a1): A**12 - 2*A**11 - 4*A**10 + 7*A**9 + 5*A**8 - 13*A**7 + 14*A**5 - 5*A**4 - 8*A**3 + 5*A**2 + A - 2,
     Diagram named  a → V(a1 a0), b → V(b1 b0): A**16 - 2*A**15 + A**14 - A**13 - A**12 + 3*A**11 + A**8 - 3*A**7 - A**6 - A**5 - A**4}
    """
    s11 = sympify("A**15 - A**14 - 4*A**13 + 4*A**12 - A**11 - 13*A**10 + 12*A**9 + 14*A**8 - 27*A**7 + 7*A**6 + 16*A**5 - 13*A**4 - A**3 + 4*A**2 - A")
    s12 = sympify("A**12 - 3*A**11 - 4*A**10 + 9*A**9 + 7*A**8 - 15*A**7 - 3*A**6 + 15*A**5 - 3*A**4 - 8*A**3 + 3*A**2 + A - 1")
    s13 = sympify("A**16 - A**15 - A**13 - 2*A**12 - A**11 + A**10 - 2*A**9 + 2*A**8 - A**6 + A**5 - A**4")

    s21 = sympify("A**15 - 5*A**13 + 5*A**12 - 16*A**10 + 10*A**9 + 17*A**8 - 22*A**7 - A**6 + 15*A**5 - 7*A**4 - 3*A**3 + 4*A**2 - A")
    s22 = sympify("2*A**12 - 3*A**11 - 8*A**10 + 9*A**9 + 13*A**8 - 14*A**7 - 7*A**6 + 11*A**5 - 5*A**3 + A**2 + A - 1")
    s23 = sympify("A**16 - A**15 + A**14 - 2*A**13 - A**12 - A**11 - A**10")

    s31 = sympify("-4*A**13 + 5*A**12 + 3*A**11 - 13*A**10 + 13*A**9 + 11*A**8 - 29*A**7 + 10*A**6 + 13*A**5 - 16*A**4 + A**3 + 5*A**2 - 2*A")
    s32 = sympify("A**12 - 2*A**11 - 4*A**10 + 7*A**9 + 5*A**8 - 13*A**7 + 14*A**5 - 5*A**4 - 8*A**3 + 5*A**2 + A - 2")
    s33 = sympify("A**16 - 2*A**15 + A**14 - A**13 - A**12 + 3*A**11 + A**8 - 3*A**7 - A**6 - A**5 - A**4")

    sigma = sympify("A+1+A**(-1)")

    print("A**18 + A**15 - 2*A**13 + A**12 - A**11 - 2*A**10 + A**9 - 3*A**8 + A**7 - 3*A**6 - 3*A**3 - A - 2")

    s1 = sympify(s11) * (-sigma**2) + sympify(s12) *sigma + sympify(s13) * sigma**2
    print(expand(s1))

    s2 = sympify(s21) * (-sigma**2) + sympify(s22) *sigma + sympify(s23) * sigma**2
    print(expand(s2))

    s3 = sympify(s31) * (-sigma**2) + sympify(s32) *sigma + sympify(s33) * sigma**2
    print(expand(s3))

def makeit(s):
    k = from_pd_notation(s)
    color_endpoints(k)
    sanity_check(k)
    print(k)
    return k

def colored_yamada_one_bond_reidemeister():
    σ = sympify("A+1+A**(-1)")
    A = sympify("A")
    s1 = "[[0,1,8],[0,4,5],[2,7,3,6],[7,4,8,3],[5,2,6,1]]"  # trefoil
    h1 = "[[0,1,2],[0,4,5],[1,5,3,6],[6,3,4,2]]"  # handcuff

    e1 = "[[0,1,2],[0,2,1]"  # state of handcuff

    k1 = makeit(s1)
    cy1 = colored_yamada_polynomial(k1)
    uy1 = yamada_polynomial(k1)

    cy1 = list(cy1.values())[0]
    print("             Yamada:", uy1)
    print("     Colored Yamada:", cy1)
    print(" σ * Colored Yamada:", expand(-A * σ * cy1))


if __name__ == '__main__':
    #test_colored_yamada_graph()
    #test_colored_yamada_trivial()
    #test_colored_yamada_one_bond()
    #test_colored_yamada_three_bonds()

    test_colored_yamada_two_bonds()
    #test_expressions()
    #colored_yamada_one_bond_reidemeister()