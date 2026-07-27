from scipy.interpolate import RBFInterpolator

import knotpy as kp


def test_colored_unplugging():
    # 5 different uncolored bonded knot candidates
    notation1 = "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 e3 f0) d=X(f3 g0 b1 a2) e=X(g3 g2 f1 c2) f=X(c3 e2 g1 d0) g=X(d1 f2 e1 e0)"
    notation2 = "a=V(b0 c0 d0) b=V(a0 d2 e0) c=V(a1 e3 f0) d=V(a2 g3 b1) e=X(b2 g2 f1 c1) f=X(c2 e2 g1 g0) g=X(f3 f2 e1 d1)"
    notation3 = "a=X(b3 b2 c3 c2) b=X(d0 e0 a1 a0) c=X(e3 f3 a3 a2) d=X(b0 f2 f1 g3) e=X(b1 g2 g1 c0) f=X(g0 d2 d1 c1) g=X(f0 e2 e1 d3)"
    notation4 = "a=V(b0 c0 d0) b=V(a0 d3 e0) c=V(a1 e2 f0) d=X(a2 f2 g0 b1) e=V(b2 g2 c1) f=V(c2 g1 d1) g=V(d2 f1 e1)"
    notation5 = "a=V(b0 c0 d3) b=V(a0 d2 e3) c=X(a1 e2 f3 f2) d=X(f1 g0 b1 a2) e=X(g3 g2 c1 b2) f=X(g1 d0 c3 c2) g=X(d1 f0 e1 e0)"

    knot1 = kp.from_knotpy_notation(notation1)
    knot2 = kp.from_knotpy_notation(notation2)
    knot3 = kp.from_knotpy_notation(notation3)
    knot4 = kp.from_knotpy_notation(notation4)
    knot5 = kp.from_knotpy_notation(notation5)

    knots = [knot1, knot2, knot3, knot4, knot5]

    for knot_index, knot in enumerate(knots):
        print(knot)
        bonded_knots = kp.bond_colorings(knot, bond_color="red", non_bonded_color="blue")
        #kp.export_pdf(bonded_knots, f"bonded_knots-{knot_index}.pdf")

        for b_index, b in enumerate(bonded_knots):
            b_unplug = kp.unplugging(b, simplify=True,  mixed_color="magenta")
            #kp.export_pdf(b_unplug,, f"unplugging-{knot_index}-{b_index}.pdf")

            print("Reidemeister moves on\n", b)


            for rb in kp.all_reidemeister_moves_space(b, depth=1):
                from knotpy.reidemeister.reidemeister import _is_all_colored


                print("Is all", _is_all_colored(rb))

                rb_unplug = kp.unplugging(rb, simplify=True, mixed_color="magenta")

                if b_unplug != rb_unplug:
                    print("not ok")
                    print("B ", b)
                    print("RB", rb)
                    kp.export_pdf([b, rb], "u_both.pdf", ignore_errors=True)
                    kp.export_pdf(b_unplug, "u_unplug_b.pdf", ignore_errors=True)
                    kp.export_pdf(rb_unplug, "u_unplug_rb.pdf", ignore_errors=True)

                    print(len(b_unplug), len(rb_unplug))
                    for _, __ in zip(b_unplug, rb_unplug):
                        print(_)
                        print(__)
                        print(_ == __, "!", len(_),len(__))

                        print(kp.canonical(_))
                        print(kp.canonical(__))

                    exit()

                else:
                    print("ok")

                assert b_unplug == rb_unplug, f"Diff:\n{b}\n{rb}"

def test_whitehead():
    """
    "Diagram a → V(b0), b → V(a0), c → X(d3 d2 e3 f0), d → X(f3 g0 c1 c0), e → X(g3 g2 f1 c2), f → X(c3 e2 g1 d0), g → X(d1 f2 e1 e0)"
"Diagram a → V(b0), b → V(a0), c → X(g3 g2 e1 f2), d → X(e3 g0 f1 f0), e → X(f3 c2 g1 d0), f → X(d3 d2 c3 e0), g → X(d1 e2 c1 c0)"

    Returns:

    """
    a="c → X(d3 d2 e3 f0), d → X(f3 g0 c1 c0), e → X(g3 g2 f1 c2), f → X(c3 e2 g1 d0), g → X(d1 f2 e1 e0)"
    b="c → X(g3 g2 e1 f2), d → X(e3 g0 f1 f0), e → X(f3 c2 g1 d0), f → X(d3 d2 c3 e0), g → X(d1 e2 c1 c0)"


    a="c → X(d3 d2 e3 f0), d → X(f3 g0 c1 c0), e → X(g3 g2 f1 c2), f → X(c3 e2 g1 d0), g → X(d1 f2 e1 e0)"
    b="c → X(g3 g2 e1 f2), d → X(e3 g0 f1 f0), e → X(f3 c2 g1 d0), f → X(d3 d2 c3 e0), g → X(d1 e2 c1 c0)"

    knot1 = kp.from_knotpy_notation(a)
    knot2 = kp.from_knotpy_notation(b)
    print(knot1)
    print(knot2)
    print(knot1 == knot2)

    q1=knot1.copy()
    q2=knot2.copy()

    for ep in q1.endpoints:
        ep.attr["color"] = "blue"
    for ep in q2.endpoints:
        ep.attr["color"] = "blue"


    c1 = kp.canonical(knot1)
    c2 = kp.canonical(knot2)
    print(c1)
    print(c2)
    print(c1 == c2)

    c1 = kp.canonical(q1)
    c2 = kp.canonical(q2)
    print(c1)
    print(c2)
    print(c1 == c2)

if __name__ == '__main__':
    #
    # d1 = "a → V(b0), b → V(a0), c → X(d3 d2 e3 f0), d → X(f3 g0 c1 c0), e → X(g3 g2 f1 c2), f → X(c3 e2 g1 d0), g → X(d1 f2 e1 e0)"
    # d2 = "a → V(b0), b → V(a0), c → X(g3 g2 d3 e0), d → X(f3 f2 e1 c2), e → X(c3 d2 f1 g0), f → X(g1 e2 d1 d0), g → X(e3 f0 c1 c0)"
    #
    # #d1 = "c → X(d3 d2 e3 f0), d → X(f3 g0 c1 c0), e → X(g3 g2 f1 c2), f → X(c3 e2 g1 d0), g → X(d1 f2 e1 e0)"
    # #d2 = "c → X(g3 g2 d3 e0), d → X(f3 f2 e1 c2), e → X(c3 d2 f1 g0), f → X(g1 e2 d1 d0), g → X(e3 f0 c1 c0)"
    #
    # k1 = kp.from_knotpy_notation(d1)
    # k2 = kp.from_knotpy_notation(d2)
    #
    # print(k1)
    # print(k2)
    #
    # print()
    #
    # print(kp.canonical(k1))
    # print(kp.canonical(k2))
    #
    #
    # exit()


    #test_whitehead()

    #exit()

    test_colored_unplugging()
