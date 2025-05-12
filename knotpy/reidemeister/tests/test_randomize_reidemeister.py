from knotpy import yamada_polynomial, sanity_check
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.invariants.jones_polynomial import jones_polynomial
from knotpy.reidemeister.reidemeister import randomize_diagram
from sandbox.classification_knotoids.knotpy.notation import from_knotpy_notation
from sandbox.classification_knotoids.knotpy.reidemeister.reidemeister_5 import find_reidemeister_5_untwists
from knotpy import settings

def test_randomize_knot():
    settings.allowed_reidemeister_moves = "r1,r2,r3"

    k = PlanarDiagram("3_1")
    j = jones_polynomial(k)

    for i in range(10):
        k_ = randomize_diagram(k, crossing_increasing_moves=2)
        assert k != k_  # unlikely they are the same
        assert jones_polynomial(k_) == j


def test_randomize_theta():
    settings.allowed_reidemeister_moves = "r1,r2,r3,r4,r5"
    t1 = PlanarDiagram("t0_1")
    t2 = PlanarDiagram("+t3_1")
    t3 = PlanarDiagram("t4_1.1")
    t4 = PlanarDiagram("h0_1")
    t5 = PlanarDiagram("h2_1.1")
    thetas = [t1, t2, t3, t4, t5]

    for theta in thetas:
        y = yamada_polynomial(theta)
        print("***")
        print(theta)
        print(" ", y)
        for i in range(20):
            theta_ = randomize_diagram(theta, crossing_increasing_moves=3)
            print(" ", theta_.attr["_sequence"])
            y_ = yamada_polynomial(theta_)
            print("  ", y_)
            assert sanity_check(theta_)
            assert y_ == y


    settings.allowed_reidemeister_moves = "r1,r2,r3"

def test_randomize_theta_direct():
    from knotpy.reidemeister import choose_reidemeister_1_add_kink, choose_reidemeister_1_remove_kink
    from knotpy.reidemeister import choose_reidemeister_2_unpoke, choose_reidemeister_2_poke
    from knotpy.reidemeister import choose_reidemeister_3_triangle, choose_reidemeister_4_slide, choose_reidemeister_5_twist, choose_reidemeister_5_untwist
    from knotpy.reidemeister import reidemeister_3, reidemeister_1_add_kink, reidemeister_2_poke, reidemeister_4_slide, reidemeister_5_twist, reidemeister_5_untwist, reidemeister_1_remove_kink, reidemeister_2_unpoke
    from knotpy import export_pdf
    settings.allowed_reidemeister_moves = "r1,r2,r3,r4,r5"

    thetas = [PlanarDiagram("t0_1"), PlanarDiagram("+t3_1"), PlanarDiagram("t4_1.1"), PlanarDiagram("h0_1"), PlanarDiagram("h2_1.1")]
    thetas = [PlanarDiagram("t0_1"), PlanarDiagram("h0_1")]

    for theta in thetas:
        y = yamada_polynomial(theta)
        k = theta.copy()
        for i in range(100):

            if (location := choose_reidemeister_3_triangle(k, random=True)) is not None:
                q = reidemeister_3(k, location, inplace=False)
                if (yq := yamada_polynomial(q)) != y:
                    print("***\n",theta,"\n",k,"\n","R3", location,"\n", q, "***")
                    print(y, "vs.\n", yq)
                    exit()
                else:
                    print("R3")

            if (location := choose_reidemeister_2_unpoke(k, random=True)) is not None:
                q = reidemeister_2_unpoke(k, location, inplace=False)
                if(yq := yamada_polynomial(q)) != y:
                    print("***\n",theta,"\n",k,"\n","R2 unpoke", location, "\n",q, "***")
                    print(y, "vs.\n", yq)
                    exit()
                else:
                    print("R2 unpoke")

            if (location := choose_reidemeister_2_poke(k, random=True)) is not None:
                q = reidemeister_2_poke(k, location, inplace=False)
                if (yq := yamada_polynomial(q)) != y:
                    print("***\n",theta,"\n",k,"\n","R2 poke", location, "\n",q, "***")
                    print(y, "vs.\n", yq)
                    exit()
                else:
                    print("R2 poke")

            if (location := choose_reidemeister_1_add_kink(k, random=True)) is not None:
                q = reidemeister_1_add_kink(k, location, inplace=False)
                if (yq := yamada_polynomial(q)) != y:
                    print("***\n",theta,"\n",k,"\n","R1 add", location, "\n",q, "***")
                    print(y, "vs.\n", yq)
                    exit()
                else:
                    print("R1 add")

            if (location := choose_reidemeister_1_remove_kink(k, random=True)) is not None:
                q = reidemeister_1_remove_kink(k, location, inplace=False)
                if (yq := yamada_polynomial(q)) != y:
                    print("***\n",theta,"\n",k,"\n","R1 remove", location, "\n",q, "***")
                    print(y, "vs.\n", yq)
                    exit()
                else:
                    print("R1 remove")

            if (location := choose_reidemeister_5_untwist(k, random=True)) is not None:
                q = reidemeister_5_untwist(k, location, inplace=False)
                if (yq := yamada_polynomial(q)) != y:
                    print("***\n",theta,"\n",k,"\n","R5 untwist", location,"\n", q, "***")
                    print(y, "vs.\n", yq)
                    exit()
                else:
                    print("R5 untwist")

            if (location := choose_reidemeister_5_twist(k, random=True)) is not None:
                q = reidemeister_5_twist(k, location, inplace=False)
                if (yq := yamada_polynomial(q)) != y:
                    print("***\n",theta,"\n",k,"\n","R4 twist", location, "\n",q, "***")
                    print(y, "vs.\n", yq)
                    exit()
                else:
                    print("R5 twist")

            if (location := choose_reidemeister_4_slide(k, random=True)) is not None:
                q = reidemeister_4_slide(k, location, inplace=False)
                if (yq := yamada_polynomial(q)) != y:
                    print("***\n",theta,"\n",k,"\n","R4", location, "\n",q, "***")
                    print(y, "vs.\n", yq)
                    exit()
                else:
                    print("R4 slide")


if __name__ == '__main__':
    #test_randomize_knot()
    #test_randomize_theta()
    test_randomize_theta_direct()